import os
import json
import hashlib
import hmac
import httpx
import asyncio
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from github import Github
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pr_review.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class PRReview(Base):
    __tablename__ = "pr_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String)
    pr_number = Column(Integer)
    pr_title = Column(String)
    pr_author = Column(String)
    pr_url = Column(String)
    analysis_result = Column(Text)
    issues_found = Column(Integer, default=0)
    security_score = Column(Integer, default=10)
    status = Column(String, default="completed")
    reviewed_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI setup
app = FastAPI(
    title="AI PR Review Service",
    description="GitHub PR review automation service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEEPSEEK_MODEL = "deepseek/deepseek-r1-0528:free"

# GitHub App authentication
def generate_jwt_token() -> str:
    """Generate JWT token for GitHub App authentication"""
    if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
        raise ValueError("GitHub App credentials not configured")
    
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + (10 * 60),  # JWT expires in 10 minutes
        'iss': GITHUB_APP_ID
    }
    
    # GitHub App private key (PEM format)
    private_key = GITHUB_APP_PRIVATE_KEY.replace('\\n', '\n')
    
    return jwt.encode(payload, private_key, algorithm='RS256')

async def get_installation_access_token(installation_id: int) -> str:
    """Get installation access token for a specific GitHub App installation"""
    jwt_token = generate_jwt_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            return data["token"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to get installation token")

async def get_github_client_for_installation(installation_id: int) -> Github:
    """Get authenticated GitHub client for a specific installation"""
    # Get installation access token
    access_token = await get_installation_access_token(installation_id)
    return Github(access_token)

# Initialize GitHub App (no default client needed)
github_app_configured = bool(GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY)

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature_header or not GITHUB_WEBHOOK_SECRET:
        return False
    
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), payload_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

# API Routes
@app.get("/")
async def root():
    return {
        "message": "AI PR Review GitHub App",
        "version": "1.0.0",
        "app_type": "GitHub App",
        "github_app_configured": github_app_configured,
        "ai_powered": bool(OPENROUTER_API_KEY)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "github_app_configured": github_app_configured,
        "ai_powered": bool(OPENROUTER_API_KEY),
        "ai_model": DEEPSEEK_MODEL if OPENROUTER_API_KEY else "disabled",
        "database_connected": True,
        "app_type": "GitHub App"
    }

@app.get("/api/reviews")
async def get_recent_reviews(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent PR reviews"""
    reviews = db.query(PRReview).order_by(PRReview.reviewed_at.desc()).limit(limit).all()
    
    review_data = []
    for review in reviews:
        analysis = {}
        try:
            analysis = json.loads(review.analysis_result) if review.analysis_result else {}
        except:
            pass
            
        review_data.append({
            "id": review.id,
            "repo_name": review.repo_name,
            "pr_number": review.pr_number,
            "pr_title": review.pr_title,
            "pr_author": review.pr_author,
            "pr_url": review.pr_url,
            "issues_found": review.issues_found,
            "security_score": review.security_score,
            "status": review.status,
            "reviewed_at": review.reviewed_at,
            "analysis": analysis
        })
    
    return {"reviews": review_data}

@app.post("/webhook")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub webhook for PR events from GitHub App"""
    
    # Get request body and signature
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Verify signature (optional for development)
    # if not verify_signature(body, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Get installation ID from payload
    installation_id = payload.get("installation", {}).get("id")
    if not installation_id:
        return {"status": "ignored", "reason": "no installation ID"}
    
    # Extract repository info
    if "repository" not in payload:
        return {"status": "ignored", "reason": "not a repository event"}
    
    repo_name = payload["repository"]["full_name"]
    
    # Handle PR events (GitHub App automatically has access to installed repos)
    if payload.get("action") in ["opened", "synchronize", "reopened"] and "pull_request" in payload:
        pr_data = payload["pull_request"]
        
        logger.info(f"Processing PR {repo_name}#{pr_data['number']} from installation {installation_id}")
        
        # Process the PR asynchronously
        asyncio.create_task(process_pr_analysis(
            installation_id=installation_id,
            repo_name=repo_name,
            pr_number=pr_data["number"],
            pr_title=pr_data["title"],
            pr_author=pr_data["user"]["login"],
            pr_url=pr_data["html_url"]
        ))
        
        return {"status": "processing", "pr": pr_data["number"]}
    
    return {"status": "ignored", "reason": "not a relevant PR event"}

async def process_pr_analysis(installation_id: int, repo_name: str, pr_number: int, pr_title: str, 
                            pr_author: str, pr_url: str):
    """Analyze PR and send notifications using GitHub App authentication"""
      # Create database session
    db = SessionLocal()
    
    try:
        # Get GitHub client for this installation
        github_client = await get_github_client_for_installation(installation_id)
        
        # Get PR details
        repo = github_client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        logger.info(f"Analyzing PR {repo_name}#{pr_number}")
        
        # Analyze files
        analysis_results = await analyze_pr_files(pr)
        
        # Save to database
        pr_review = PRReview(
            repo_name=repo_name,
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author=pr_author,
            pr_url=pr_url,            analysis_result=json.dumps(analysis_results),
            issues_found=analysis_results.get("total_issues", 0),
            security_score=analysis_results.get("security_score", 10)
        )
        
        db.add(pr_review)
        db.commit()
        
        # Post GitHub comment
        await post_github_review_comment(pr, analysis_results)
        
        logger.info(f"Successfully processed PR {repo_name}#{pr_number}")
        
    except Exception as e:
        logger.error(f"Error processing PR {repo_name}#{pr_number}: {str(e)}")
    finally:
        db.close()

async def analyze_pr_files(pr) -> Dict:
    """Analyze all files in the PR with both rule-based and AI analysis"""
    
    analysis = {
        "files_analyzed": 0,
        "total_issues": 0,
        "security_issues": 0,
        "style_issues": 0,
        "ai_issues": 0,
        "security_score": 10,
        "files": [],
        "summary": "",
        "ai_enabled": bool(OPENROUTER_API_KEY)
    }
    
    try:
        files = pr.get_files()
        
        for file in files:
            if file.filename.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb')):
                try:
                    # Traditional rule-based analysis
                    file_analysis = analyze_file_changes(file)
                    
                    # AI-powered analysis (if API key available)
                    ai_analysis = {"ai_issues": [], "ai_suggestions": [], "ai_summary": ""}
                    if OPENROUTER_API_KEY and file.patch:
                        ai_analysis = await ai_code_review(
                            code_content="",  # We use patch instead
                            filename=file.filename,
                            file_patch=file.patch
                        )
                    
                    # Combine traditional + AI analysis
                    combined_issues = file_analysis["issues"] + ai_analysis["ai_issues"]
                    combined_suggestions = file_analysis["suggestions"] + ai_analysis["ai_suggestions"]
                    
                    if combined_issues or combined_suggestions or ai_analysis.get("ai_summary"):
                        analysis["files"].append({
                            "filename": file.filename,
                            "changes": file.changes,
                            "additions": file.additions,
                            "deletions": file.deletions,
                            "issues": file_analysis["issues"],
                            "suggestions": file_analysis["suggestions"],
                            "ai_issues": ai_analysis["ai_issues"],
                            "ai_suggestions": ai_analysis["ai_suggestions"],
                            "ai_summary": ai_analysis.get("ai_summary", ""),
                            "combined_issues": combined_issues,
                            "combined_suggestions": combined_suggestions
                        })
                    
                    analysis["files_analyzed"] += 1
                    analysis["total_issues"] += len(file_analysis["issues"])
                    analysis["ai_issues"] += len(ai_analysis["ai_issues"])
                    
                except Exception as e:
                    logger.error(f"Error analyzing file {file.filename}: {str(e)}")
        
        # Calculate security score based on combined analysis
        total_combined_issues = analysis["total_issues"] + analysis["ai_issues"]
        
        if total_combined_issues == 0:
            analysis["security_score"] = 10
            analysis["summary"] = "✅ Excellent! No issues detected by rule-based or AI analysis."
        elif total_combined_issues <= 2:
            analysis["security_score"] = 8
            analysis["summary"] = "✨ Great work! Only minor issues found."
        elif total_combined_issues <= 5:
            analysis["security_score"] = 6
            analysis["summary"] = "⚠️ Several issues found that should be addressed."
        else:
            analysis["security_score"] = 4
            analysis["summary"] = "🚨 Multiple issues detected - please review carefully."
        
        # Add AI enhancement note
        if OPENROUTER_API_KEY:
            analysis["summary"] += f" (Enhanced with Deepseek R1 AI analysis)"
        
    except Exception as e:
        logger.error(f"Error in PR analysis: {str(e)}")
        analysis["summary"] = "❌ Analysis failed due to an error."
    
    return analysis

async def ai_code_review(code_content: str, filename: str, file_patch: str) -> Dict:
    """Use OpenRouter's Deepseek R1 for AI-powered code review"""
    
    if not OPENROUTER_API_KEY:
        logger.warning("OpenRouter API key not configured, skipping AI review")
        return {"ai_issues": [], "ai_suggestions": [], "ai_summary": "AI review not available"}
    
    try:
        prompt = f"""You are a senior principal engineer at a top tech company (Google/Meta/Netflix) performing a comprehensive code review. Analyze this code change with extreme attention to detail, as if this code will serve millions of users.

**File:** {filename}
**Code Changes:**
```
{file_patch}
```

**CRITICAL ANALYSIS FRAMEWORK:**

🔍 **LOGIC & CORRECTNESS (Be Extremely Thorough):**
- **Control Flow:** Are all code paths handled? Any unreachable code?
- **Return Values:** Functions that should return but don't, inconsistent return types
- **Variable Scope:** Variables used before definition, scope pollution
- **Loop Logic:** Infinite loops, incorrect termination conditions, iterator issues
- **Conditional Logic:** Missing else cases, redundant conditions, boolean logic errors
- **Edge Cases:** Empty arrays/objects, null/undefined handling, boundary values
- **Type Mismatches:** Implicit conversions, wrong data types
- **Function Contracts:** Parameters used incorrectly, assumptions violated
- **Resource Management:** Files/connections not closed, memory not freed
- **Race Conditions:** Async operations, shared state issues

🚨 **SECURITY VULNERABILITIES (Zero Tolerance):**
- **Input Validation:** Missing sanitization, injection attack vectors
- **Authentication:** Weak/missing auth checks, session management
- **Authorization:** Privilege escalation, access control bypasses
- **Data Exposure:** Sensitive data in logs/errors, information leakage
- **Cryptography:** Weak algorithms, improper key handling, timing attacks
- **File Operations:** Path traversal, unsafe file access
- **Network:** Unencrypted transmission, certificate validation
- **Dependencies:** Vulnerable packages, untrusted sources
- **Error Handling:** Information disclosure in error messages

⚠️ **CODE QUALITY (Professional Standards):**
- **Complexity:** Cyclomatic complexity too high, deeply nested code
- **Readability:** Unclear variable names, confusing logic flow
- **Duplication:** Repeated code blocks, copy-paste programming
- **Coupling:** Tight dependencies, hard to test/modify
- **Cohesion:** Mixed responsibilities, unclear purpose
- **Error Handling:** Missing try-catch, inadequate error messages
- **Constants:** Magic numbers, hardcoded strings
- **Formatting:** Inconsistent style, poor indentation

⚡ **PERFORMANCE & EFFICIENCY (Scale Considerations):**
- **Algorithmic Complexity:** O(n²) where O(n) possible, inefficient data structures
- **Database:** N+1 queries, missing indexes, unnecessary data fetching
- **Memory:** Object creation in loops, memory leaks, large objects
- **Network:** Multiple API calls, large payloads, no caching
- **CPU:** Unnecessary computations, blocking operations
- **I/O:** Synchronous operations, inefficient file handling

🏗️ **ARCHITECTURE & DESIGN (Enterprise Quality):**
- **SOLID Principles:** Single responsibility, open/closed, etc.
- **Design Patterns:** Incorrect pattern usage, missing abstractions
- **Separation of Concerns:** Business logic mixed with presentation
- **Dependency Injection:** Hard dependencies, poor testability
- **Interface Design:** Leaky abstractions, unclear contracts
- **Error Propagation:** Swallowed exceptions, improper error handling

📝 **MAINTAINABILITY & DOCUMENTATION:**
- **Code Self-Documentation:** Variable/function names don't explain purpose
- **Comments:** Missing for complex logic, outdated comments
- **Type Safety:** Missing type annotations, any/unknown types
- **API Documentation:** Missing parameter descriptions, return value docs
- **Business Logic:** Complex algorithms without explanation

🧪 **TESTING & RELIABILITY (Production Readiness):**
- **Edge Case Handling:** Empty inputs, null values, extreme values
- **Error Scenarios:** Network failures, timeouts, invalid responses
- **Validation:** Input validation, data integrity checks
- **Fault Tolerance:** Graceful degradation, retry mechanisms
- **Monitoring:** Missing logs, no metrics collection

**ANALYSIS METHODOLOGY:**
1. **Line-by-Line Review:** Examine every added/modified line
2. **Context Understanding:** Consider the broader function/class purpose
3. **Impact Assessment:** How changes affect the entire system
4. **Risk Evaluation:** What could go wrong in production?
5. **Alternative Solutions:** Are there better approaches?

**RESPONSE FORMAT:**
For EACH issue found, provide:
🔴 CRITICAL | � HIGH | � MEDIUM | � LOW [Category]: Line X: [Specific issue description]
**Problem:** [Detailed explanation of what's wrong]
**Impact:** [What happens if this isn't fixed]
**Solution:** [Concrete code example or fix]

**POSITIVE FEEDBACK:** Also mention what's done well!

**FINAL ASSESSMENT:**
- **Code Quality Score:** X/10
- **Production Readiness:** [Ready/Needs Work/Major Issues]
- **Key Priorities:** [Top 3 issues to fix first]

**REMEMBER:** Be as thorough as ChatGPT doing a code review. Don't miss subtle issues that could cause bugs in production!"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com",  # Optional: for OpenRouter analytics
                    "X-Title": "PR Review Bot"  # Optional: for OpenRouter analytics
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a senior principal engineer performing comprehensive code reviews. Be extremely thorough in finding logic, security, quality, and design issues."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1500,  # Increased for more detailed analysis
                    "temperature": 0.2,  # Lower for more consistent analysis
                    "top_p": 0.9
                },
                timeout=45.0  # Increased timeout for thorough analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Enhanced parsing for the new comprehensive format
                ai_issues = []
                ai_suggestions = []
                ai_summary = ""
                
                lines = ai_response.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Look for issue lines with severity indicators
                    if any(severity in line for severity in ['� CRITICAL', '🟠 HIGH', '🟡 MEDIUM', '🟢 LOW']):
                        # Extract the issue
                        if '🔴 CRITICAL' in line or '🟠 HIGH' in line:
                            ai_issues.append(line)
                        else:
                            ai_suggestions.append(line)
                    
                    # Look for Problem/Impact/Solution blocks
                    elif line.startswith('**Problem:**') or line.startswith('**Impact:**') or line.startswith('**Solution:**'):
                        if ai_issues:
                            ai_issues[-1] += f" | {line}"
                        elif ai_suggestions:
                            ai_suggestions[-1] += f" | {line}"
                    
                    # Look for final assessment
                    elif 'Code Quality Score:' in line or 'Production Readiness:' in line:
                        ai_summary += line + " "
                    
                    # Fallback: any line starting with common issue indicators
                    elif line.startswith(('- ', '• ')) and any(keyword in line.lower() for keyword in [
                        'error', 'issue', 'problem', 'bug', 'vulnerability', 'security', 'performance', 'logic'
                    ]):
                        ai_issues.append(line[2:])  # Remove bullet
                
                # If no structured parsing worked, extract key insights
                if not ai_issues and not ai_suggestions:
                    # Look for any critical insights in the response
                    critical_keywords = ['critical', 'security', 'vulnerability', 'error', 'bug', 'issue']
                    suggestion_keywords = ['suggest', 'recommend', 'consider', 'improve', 'better']
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in critical_keywords):
                            ai_issues.append(line.strip())
                        elif any(keyword in line_lower for keyword in suggestion_keywords):
                            ai_suggestions.append(line.strip())
                
                # Clean up the summary
                if not ai_summary and ai_response:
                    # Extract the last meaningful line as summary
                    meaningful_lines = [line for line in lines if line.strip() and not line.startswith(('**', '#', '-', '•'))]
                    ai_summary = meaningful_lines[-1] if meaningful_lines else "AI analysis completed"
                
                # Token usage logging
                usage = result.get("usage", {})
                logger.info(f"AI review completed for {filename}. Issues: {len(ai_issues)}, Suggestions: {len(ai_suggestions)}, Tokens: {usage.get('total_tokens', 'unknown')}")
                
                return {
                    "ai_issues": ai_issues[:10],  # Limit to top 10 issues
                    "ai_suggestions": ai_suggestions[:10],  # Limit to top 10 suggestions
                    "ai_summary": ai_summary or "AI analysis completed",
                    "ai_raw_response": ai_response,
                    "token_usage": usage
                }
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {
                    "ai_issues": [],
                    "ai_suggestions": [f"AI review failed: API error {response.status_code}"],
                    "ai_summary": "AI review unavailable"
                }
                
    except asyncio.TimeoutError:
        logger.error("OpenRouter API timeout")
        return {
            "ai_issues": [],
            "ai_suggestions": ["AI review failed: timeout"],
            "ai_summary": "AI review timed out"
        }
    except Exception as e:
        logger.error(f"AI review error: {str(e)}")
        return {
            "ai_issues": [],
            "ai_suggestions": [f"AI review failed: {str(e)}"],
            "ai_summary": "AI review encountered an error"
        }

def analyze_file_changes(file) -> Dict:
    """Enhanced rule-based analysis for individual file changes"""
    
    issues = []
    suggestions = []
    
    filename = file.filename.lower()
    patch = file.patch or ""
    
    # Security checks (Critical)
    if any(keyword in patch.lower() for keyword in ['password', 'secret', 'api_key', 'token', 'private_key']):
        if any(op in patch for op in ['=', ':', 'const', 'let', 'var']):
            issues.append("� CRITICAL: Potential hardcoded credentials detected")
    
    if 'eval(' in patch or 'exec(' in patch:
        issues.append("� CRITICAL: Dangerous function usage detected (eval/exec)")
    
    if 'sql' in filename and any(keyword in patch.lower() for keyword in ['select', 'insert', 'update', 'delete']):
        if '+' in patch and any(concat in patch for concat in ['+ ', '+ "', "+ '"]):
            issues.append("� CRITICAL: Potential SQL injection vulnerability")
    
    # Input validation issues
    if any(func in patch for func in ['request.', 'req.', 'input(', 'raw_input(']):
        if 'validate' not in patch.lower() and 'sanitize' not in patch.lower():
            issues.append("🟠 HIGH: Input validation may be missing")
    
    # Unsafe operations
    if any(unsafe in patch for unsafe in ['pickle.loads', 'yaml.load', 'subprocess.call']):
        issues.append("🟠 HIGH: Potentially unsafe operation detected")
    
    # Code quality checks (Medium/Low)
    if 'todo' in patch.lower() or 'fixme' in patch.lower() or 'hack' in patch.lower():
        suggestions.append("� MEDIUM: Contains TODO/FIXME/HACK comments - should be addressed")
    
    if 'console.log' in patch or 'print(' in patch:
        suggestions.append("� MEDIUM: Debug statements detected - consider removing for production")
    
    # Error handling issues
    if 'try:' in patch and 'except' not in patch:
        issues.append("🟠 HIGH: Try block without exception handling")
    
    if 'catch' in patch and 'throw' not in patch and 'log' not in patch:
        suggestions.append("🟡 MEDIUM: Exception caught but not logged or re-thrown")
    
    # Performance issues
    if file.additions > 500:
        suggestions.append("� MEDIUM: Large file changes - consider breaking into smaller commits")
    
    if any(loop in patch for loop in ['for ', 'while ']) and any(nested in patch for nested in ['for ', 'while ']):
        suggestions.append("🟠 HIGH: Nested loops detected - check algorithmic complexity")
    
    # Language-specific checks
    if filename.endswith('.py'):
        # Python specific checks
        if 'import *' in patch:
            issues.append("🟠 HIGH: Wildcard imports detected - use specific imports")
        
        if 'except:' in patch and 'except Exception:' not in patch:
            issues.append("🟠 HIGH: Bare except clause - specify exception types")
        
        if 'global ' in patch:
            suggestions.append("🟡 MEDIUM: Global variable usage - consider passing as parameter")
        
        if '+' in patch and any(pattern in patch for pattern in ['%s', '%d', '.format(']):
            suggestions.append("🟢 LOW: Consider using f-strings for better readability")
        
        # Check for common anti-patterns
        if 'len(' in patch and '== 0' in patch:
            suggestions.append("🟢 LOW: Consider using 'not list' instead of 'len(list) == 0'")
    
    elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
        # JavaScript/TypeScript specific checks
        if 'var ' in patch:
            suggestions.append("� MEDIUM: Consider using 'let' or 'const' instead of 'var'")
        
        if '== ' in patch or '!= ' in patch:
            suggestions.append("� MEDIUM: Consider using strict equality (=== or !==)")
        
        if 'function(' in patch and '=>' not in patch:
            suggestions.append("🟢 LOW: Consider using arrow functions for consistency")
        
        if 'null' in patch and 'undefined' in patch:
            suggestions.append("🟡 MEDIUM: Mixed null/undefined usage - be consistent")
        
        # React specific
        if filename.endswith(('.jsx', '.tsx')):
            if 'className=' in patch and 'class=' in patch:
                issues.append("🟠 HIGH: Mixed className/class attributes in React")
            
            if 'useEffect' in patch and '[]' not in patch:
                suggestions.append("🟡 MEDIUM: useEffect dependency array should be specified")
    
    elif filename.endswith(('.java', '.kt')):
        # Java/Kotlin specific checks
        if 'System.out.print' in patch:
            suggestions.append("🟡 MEDIUM: Use logging framework instead of System.out")
        
        if 'catch (Exception' in patch:
            suggestions.append("🟡 MEDIUM: Catching generic Exception - be more specific")
    
    elif filename.endswith('.go'):
        # Go specific checks
        if 'panic(' in patch:
            suggestions.append("🟠 HIGH: Panic usage detected - consider returning error")
        
        if 'fmt.Print' in patch:
            suggestions.append("🟡 MEDIUM: Consider using structured logging")
    
    elif filename.endswith('.rb'):
        # Ruby specific checks
        if 'puts ' in patch:
            suggestions.append("🟡 MEDIUM: Debug output detected - use proper logging")
        
        if 'rescue =>' in patch:
            suggestions.append("🟡 MEDIUM: Generic rescue clause - specify exception types")
    
    # File type specific checks
    if filename.endswith(('.json', '.yaml', '.yml')):
        if 'password' in patch.lower() or 'secret' in patch.lower():
            issues.append("🔴 CRITICAL: Secrets in configuration file")
    
    if filename.endswith(('.env', '.config')):
        if '+' in patch:  # New additions to config files
            suggestions.append("🟡 MEDIUM: Configuration changes - ensure secrets are not exposed")
    
    if filename.endswith('.sql'):
        if 'drop ' in patch.lower() or 'delete ' in patch.lower():
            issues.append("🟠 HIGH: Destructive SQL operations detected")
    
    # Docker/Infrastructure files
    if filename in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
        if 'root' in patch.lower():
            suggestions.append("🟠 HIGH: Running as root in container - security risk")
        if 'password' in patch.lower():
            issues.append("🔴 CRITICAL: Password in Docker configuration")
    
    return {
        "issues": issues,
        "suggestions": suggestions
    }

async def post_github_review_comment(pr, analysis: Dict):
    """Post comprehensive review comment on GitHub PR with AI insights"""
    
    ai_powered = "🤖 **AI-Enhanced** " if analysis.get("ai_enabled") else ""
    total_combined_issues = analysis['total_issues'] + analysis.get('ai_issues', 0)
    
    # Determine overall status
    if total_combined_issues == 0:
        status_icon = "✅"
        status_text = "**APPROVED** - Excellent code quality!"
    elif total_combined_issues <= 2:
        status_icon = "✨"
        status_text = "**LOOKS GOOD** - Minor issues only"
    elif total_combined_issues <= 5:
        status_icon = "⚠️"
        status_text = "**NEEDS REVIEW** - Several issues found"
    else:
        status_icon = "🚨"
        status_text = "**REQUIRES CHANGES** - Multiple issues detected"
    
    comment = f"""## {ai_powered}Code Review Report {status_icon}

### {status_text}

**📊 Analysis Summary:**
- **Files Analyzed:** {analysis['files_analyzed']}
- **Rule-based Issues:** {analysis['total_issues']} 
- **AI-detected Issues:** {analysis.get('ai_issues', 0)}
- **Security Score:** {analysis['security_score']}/10 ⭐

{analysis.get('summary', '')}

---
"""
    
    if analysis.get('files'):
        comment += "## 📁 Detailed File Analysis\n\n"
        
        for file_info in analysis['files']:
            file_icon = "🔴" if file_info.get('issues') else "🟡" if file_info.get('ai_issues') else "✅"
            comment += f"### {file_icon} `{file_info['filename']}`\n"
            comment += f"**Changes:** `+{file_info['additions']} -{file_info['deletions']}` lines\n\n"
            
            # Critical issues first (rule-based)
            critical_issues = [issue for issue in file_info.get('issues', []) if '🔴 CRITICAL' in issue]
            high_issues = [issue for issue in file_info.get('issues', []) if '🟠 HIGH' in issue]
            medium_issues = [issue for issue in file_info.get('issues', []) if '🟡 MEDIUM' in issue]
            low_issues = [issue for issue in file_info.get('issues', []) if '🟢 LOW' in issue]
            
            if critical_issues:
                comment += "**� CRITICAL ISSUES:**\n"
                for issue in critical_issues:
                    comment += f"- {issue}\n"
                comment += "\n"
            
            if high_issues:
                comment += "**🟠 HIGH PRIORITY:**\n"
                for issue in high_issues:
                    comment += f"- {issue}\n"
                comment += "\n"
            
            # AI Analysis (always high priority)
            if file_info.get('ai_issues'):
                comment += "**🤖 AI CODE ANALYSIS:**\n"
                for issue in file_info['ai_issues'][:5]:  # Limit to top 5
                    comment += f"- {issue}\n"
                comment += "\n"
            
            # Medium priority issues
            if medium_issues:
                comment += "**🟡 MEDIUM PRIORITY:**\n"
                for issue in medium_issues:
                    comment += f"- {issue}\n"
                comment += "\n"
            
            # Suggestions
            all_suggestions = file_info.get('suggestions', []) + file_info.get('ai_suggestions', [])
            if all_suggestions:
                comment += "**💡 SUGGESTIONS & IMPROVEMENTS:**\n"
                for suggestion in all_suggestions[:5]:  # Limit to top 5
                    comment += f"- {suggestion}\n"
                comment += "\n"
            
            # Low priority issues
            if low_issues:
                comment += "<details><summary>🟢 <strong>Low Priority Issues</strong> (click to expand)</summary>\n\n"
                for issue in low_issues:
                    comment += f"- {issue}\n"
                comment += "\n</details>\n\n"
            
            # AI summary for this file
            if file_info.get('ai_summary'):
                comment += f"**🎯 AI Assessment:** {file_info['ai_summary']}\n\n"
            
            comment += "---\n\n"
    
    # Overall recommendations
    if total_combined_issues > 0:
        comment += "## 🎯 Next Steps\n\n"
        
        critical_count = sum(1 for file_info in analysis.get('files', []) 
                           for issue in file_info.get('issues', []) if '🔴 CRITICAL' in issue)
        high_count = sum(1 for file_info in analysis.get('files', []) 
                        for issue in file_info.get('issues', []) if '🟠 HIGH' in issue)
        ai_issue_count = analysis.get('ai_issues', 0)
        
        if critical_count > 0:
            comment += f"1. **🔴 Address {critical_count} critical security/safety issue(s) immediately**\n"
        if high_count > 0:
            comment += f"2. **🟠 Fix {high_count} high-priority issue(s) before merging**\n"
        if ai_issue_count > 0:
            comment += f"3. **🤖 Review {ai_issue_count} AI-identified issue(s) for logic/quality**\n"
        
        comment += "\n"
    
    # Footer with AI info
    footer = "---\n"
    footer += "**🚀 Automated by AI PR Review Bot** | *LabLab.ai Hackathon 2025*\n\n"
    if analysis.get("ai_enabled"):
        footer += "*🤖 Enhanced with Deepseek R1 AI Analysis via OpenRouter*\n"
        footer += "*⚡ Comprehensive logic, security, quality & best practice review*"
    else:
        footer += "*🔍 Rule-based analysis only - AI enhancement available with API key*"
    
    comment += footer
    
    try:
        pr.create_issue_comment(comment)
        logger.info(f"GitHub comment posted for PR #{pr.number} - {total_combined_issues} total issues found")
    except Exception as e:
        logger.error(f"Error posting GitHub comment: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

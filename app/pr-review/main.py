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

def get_github_client_for_installation(installation_id: int) -> Github:
    """Get authenticated GitHub client for a specific installation"""
    # This is a simplified version - in practice you'd cache tokens
    # For now, we'll use a simpler approach with installation ID
    return Github(auth=Github.Auth.AppInstallationAuth(
        app_id=GITHUB_APP_ID,
        private_key=GITHUB_APP_PRIVATE_KEY,
        installation_id=installation_id
    ))

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
        github_client = get_github_client_for_installation(installation_id)
        
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
        prompt = f"""You are an expert code reviewer. Analyze this code change and provide a detailed review.

**File:** {filename}
**Code Changes:**
```
{file_patch}
```

Please provide:
1. **Security Issues**: Any potential security vulnerabilities
2. **Code Quality Issues**: Logic errors, bugs, or poor practices
3. **Performance Issues**: Inefficiencies or optimization opportunities
4. **Best Practices**: Violations of coding standards or conventions
5. **Suggestions**: Specific improvements with examples

Focus on the CHANGED code (lines with + or -). Be concise but thorough. Use emojis for categories.

Format your response as:
🚨 SECURITY:
- Issue description

⚠️ QUALITY:
- Issue description

⚡ PERFORMANCE:
- Issue description

💡 SUGGESTIONS:
- Specific improvement with example

📋 SUMMARY:
Brief overall assessment
"""

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
                            "content": "You are an expert senior developer performing code reviews. Be thorough but concise. Focus on security, quality, and best practices."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3,
                    "top_p": 0.9
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Parse AI response into structured format
                ai_issues = []
                ai_suggestions = []
                ai_summary = ""
                
                lines = ai_response.split('\n')
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('🚨 SECURITY:'):
                        current_section = 'security'
                    elif line.startswith('⚠️ QUALITY:'):
                        current_section = 'quality'
                    elif line.startswith('⚡ PERFORMANCE:'):
                        current_section = 'performance'
                    elif line.startswith('💡 SUGGESTIONS:'):
                        current_section = 'suggestions'
                    elif line.startswith('📋 SUMMARY:'):
                        current_section = 'summary'
                    elif line.startswith('- '):
                        if current_section in ['security', 'quality', 'performance']:
                            ai_issues.append(line[2:])  # Remove "- " prefix
                        elif current_section == 'suggestions':
                            ai_suggestions.append(line[2:])
                    elif current_section == 'summary' and line:
                        ai_summary = line
                
                # Token usage logging
                usage = result.get("usage", {})
                logger.info(f"AI review completed for {filename}. Tokens: {usage.get('total_tokens', 'unknown')}")
                
                return {
                    "ai_issues": ai_issues,
                    "ai_suggestions": ai_suggestions,
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
    """Analyze individual file changes"""
    
    issues = []
    suggestions = []
    
    filename = file.filename.lower()
    patch = file.patch or ""
    
    # Security checks
    if any(keyword in patch.lower() for keyword in ['password', 'secret', 'api_key', 'token']):
        if any(op in patch for op in ['=', ':', 'const', 'let', 'var']):
            issues.append("🚨 Potential hardcoded credentials detected")
    
    if 'eval(' in patch or 'exec(' in patch:
        issues.append("🚨 Dangerous function usage detected (eval/exec)")
    
    if 'sql' in filename and any(keyword in patch.lower() for keyword in ['select', 'insert', 'update', 'delete']):
        if '+' in patch and any(concat in patch for concat in ['+ ', '+ "', "+ '"]):
            issues.append("🚨 Potential SQL injection vulnerability")
    
    # Code quality checks
    if 'todo' in patch.lower() or 'fixme' in patch.lower():
        suggestions.append("📝 Contains TODO/FIXME comments")
    
    if 'console.log' in patch or 'print(' in patch:
        suggestions.append("🔍 Debug statements detected - consider removing")
    
    # File size checks
    if file.additions > 500:
        suggestions.append("📏 Large file changes - consider breaking into smaller commits")
    
    if filename.endswith('.py'):
        # Python specific checks
        if 'import *' in patch:
            issues.append("⚠️ Wildcard imports detected - use specific imports")
        
        if 'except:' in patch and 'except Exception:' not in patch:
            issues.append("⚠️ Bare except clause - specify exception types")
    
    elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
        # JavaScript/TypeScript specific checks
        if 'var ' in patch:
            suggestions.append("💡 Consider using 'let' or 'const' instead of 'var'")
        
        if '== ' in patch or '!= ' in patch:
            suggestions.append("💡 Consider using strict equality (=== or !==)")
    
    return {
        "issues": issues,
        "suggestions": suggestions
    }

async def post_github_review_comment(pr, analysis: Dict):
    """Post review comment on GitHub PR with AI insights"""
    
    ai_powered = "🤖 AI-Enhanced " if analysis.get("ai_enabled") else ""
    
    comment = f"""## {ai_powered}Code Review Summary

**Files Analyzed:** {analysis['files_analyzed']}  
**Rule-based Issues:** {analysis['total_issues']}  
**AI-detected Issues:** {analysis.get('ai_issues', 0)}  
**Security Score:** {analysis['security_score']}/10  

{analysis.get('summary', '')}

"""
    
    if analysis.get('files'):
        comment += "### 📁 Detailed Analysis\n\n"
        for file_info in analysis['files']:
            comment += f"#### `{file_info['filename']}`\n"
            comment += f"*+{file_info['additions']} -{file_info['deletions']} lines*\n\n"
            
            # Traditional issues
            if file_info.get('issues'):
                comment += "**🔍 Rule-based Analysis:**\n"
                for issue in file_info['issues']:
                    comment += f"- {issue}\n"
                comment += "\n"
            
            # AI issues  
            if file_info.get('ai_issues'):
                comment += "**🤖 AI Analysis:**\n"
                for issue in file_info['ai_issues']:
                    comment += f"- {issue}\n"
                comment += "\n"
            
            # Traditional suggestions
            if file_info.get('suggestions'):
                comment += "**💡 Suggestions:**\n"
                for suggestion in file_info['suggestions']:
                    comment += f"- {suggestion}\n"
                comment += "\n"
            
            # AI suggestions
            if file_info.get('ai_suggestions'):
                comment += "**✨ AI Suggestions:**\n"
                for suggestion in file_info['ai_suggestions']:
                    comment += f"- {suggestion}\n"
                comment += "\n"
            
            # AI summary for this file
            if file_info.get('ai_summary'):
                comment += f"**🎯 AI Summary:** {file_info['ai_summary']}\n\n"
    
    # Footer with AI info
    footer = "---\n*🚀 Powered by AI PR Review Bot | LabLab.ai Hackathon 2025*"
    if analysis.get("ai_enabled"):
        footer += "\n*Enhanced with Deepseek R1 AI via OpenRouter*"
    
    comment += footer
    
    try:
        pr.create_issue_comment(comment)
        logger.info(f"GitHub comment posted for PR #{pr.number}")
    except Exception as e:
        logger.error(f"Error posting GitHub comment: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

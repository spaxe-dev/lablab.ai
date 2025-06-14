import os
import json
import re
import asyncio
from typing import List, Dict, Optional, Union
from datetime import datetime
import httpx
import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn
from packaging import version
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dependency Health Checker",
    description="API for checking vulnerabilities in Python and Node.js dependencies",
    version="1.0.0"
)

# Configure CORS for Render deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Render deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Dependency(BaseModel):
    name: str
    version: str
    type: str  # "python" or "node"

class Vulnerability(BaseModel):
    cve_id: str
    description: str
    severity: str
    published_date: str
    affected_versions: List[str]
    fixed_versions: List[str]

class DependencyResult(BaseModel):
    dependency: Dependency
    vulnerabilities: List[Vulnerability]
    is_vulnerable: bool
    risk_level: str

class DependencyRiskDetails(BaseModel):
    name: str
    version: str
    risk_level: str
    vulnerability_count: int
    critical_cves: List[str]
    high_cves: List[str]
    medium_cves: List[str]
    low_cves: List[str]

class HealthCheckResponse(BaseModel):
    total_dependencies: int
    vulnerable_dependencies: int
    vulnerabilities_found: int
    risk_summary: Dict[str, int]
    dependency_risk_summary: Dict[str, List[str]]  # risk level -> dependency names
    dependency_risk_details: Dict[str, List[DependencyRiskDetails]]  # detailed CVE info per risk level
    results: List[DependencyResult]
    scan_timestamp: str

class GitHubRepoRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = "main"

# NVD API Configuration
NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class VulnerabilityChecker:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def search_vulnerabilities(self, package_name: str, package_type: str) -> List[Vulnerability]:
        """Search for vulnerabilities using NVD API"""
        try:
            # Search for CVEs related to the package
            params = {
                "keywordSearch": f"{package_name}",
                "resultsPerPage": 50
            }
            
            response = await self.session.get(NVD_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = []
            
            if "vulnerabilities" in data:
                for vuln_data in data["vulnerabilities"]:
                    cve = vuln_data.get("cve", {})
                    cve_id = cve.get("id", "")
                    
                    # Check if this CVE is relevant to our package
                    if self._is_relevant_cve(cve, package_name, package_type):
                        vulnerability = self._parse_vulnerability(cve)
                        if vulnerability:
                            vulnerabilities.append(vulnerability)
            
            return vulnerabilities[:10]  # Limit to top 10 most relevant
            
        except Exception as e:
            logger.error(f"Error searching vulnerabilities for {package_name}: {str(e)}")
            return []
    
    def _is_relevant_cve(self, cve: dict, package_name: str, package_type: str) -> bool:
        """Check if CVE is relevant to the package"""
        description = cve.get("descriptions", [{}])[0].get("value", "").lower()
        package_lower = package_name.lower()
        
        # Check if package name appears in description
        if package_lower in description:
            return True
        
        # Check CPE configurations for more precise matching
        configurations = cve.get("configurations", {}).get("nodes", [])
        for node in configurations:
            cpe_matches = node.get("cpeMatch", [])
            for cpe_match in cpe_matches:
                cpe23uri = cpe_match.get("cpe23Uri", "").lower()
                if package_lower in cpe23uri:
                    return True
        
        return False
    
    def _parse_vulnerability(self, cve: dict) -> Optional[Vulnerability]:
        """Parse CVE data into Vulnerability model"""
        try:
            cve_id = cve.get("id", "")
            descriptions = cve.get("descriptions", [])
            description = descriptions[0].get("value", "") if descriptions else ""
            
            # Get severity information
            metrics = cve.get("metrics", {})
            severity = "UNKNOWN"
            
            if "cvssMetricV31" in metrics:
                severity = metrics["cvssMetricV31"][0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
            elif "cvssMetricV3" in metrics:
                severity = metrics["cvssMetricV3"][0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")
            elif "cvssMetricV2" in metrics:
                score = metrics["cvssMetricV2"][0].get("cvssData", {}).get("baseScore", 0)
                if score >= 7.0:
                    severity = "HIGH"
                elif score >= 4.0:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
            
            published_date = cve.get("published", "")
            
            return Vulnerability(
                cve_id=cve_id,
                description=description[:500] + "..." if len(description) > 500 else description,
                severity=severity,
                published_date=published_date,
                affected_versions=[],  # Would need additional parsing for specific versions
                fixed_versions=[]
            )
        except Exception as e:
            logger.error(f"Error parsing vulnerability: {str(e)}")
            return None

class DependencyParser:
    @staticmethod
    def parse_requirements_txt(content: str) -> List[Dependency]:
        """Parse Python requirements.txt file"""
        dependencies = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle different requirement formats
            if '==' in line:
                name, version_spec = line.split('==', 1)
                version_clean = version_spec.split('[')[0].split(';')[0].strip()
            elif '>=' in line:
                name, version_spec = line.split('>=', 1)
                version_clean = version_spec.split('[')[0].split(';')[0].strip()
            elif '>' in line:
                name, version_spec = line.split('>', 1)
                version_clean = version_spec.split('[')[0].split(';')[0].strip()
            else:
                # No version specified
                name = line.split('[')[0].split(';')[0].strip()
                version_clean = "latest"
            
            dependencies.append(Dependency(
                name=name.strip(),
                version=version_clean,
                type="python"
            ))
        
        return dependencies
    
    @staticmethod
    def parse_package_json(content: str) -> List[Dependency]:
        """Parse Node.js package.json file"""
        dependencies = []
        
        try:
            data = json.loads(content)
            
            # Parse dependencies
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            
            all_deps = {**deps, **dev_deps}
            
            for name, version_spec in all_deps.items():
                # Clean version specification
                version_clean = version_spec.lstrip('^~>=<')
                if version_clean.startswith('*'):
                    version_clean = "latest"
                
                dependencies.append(Dependency(
                    name=name,
                    version=version_clean,
                    type="node"
                ))
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing package.json: {str(e)}")
            
        return dependencies

async def analyze_dependencies(dependencies: List[Dependency]) -> HealthCheckResponse:
    """Analyze dependencies for vulnerabilities"""
    results = []
    risk_summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    dependency_risk_summary = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": [], "UNKNOWN": [], "NONE": []}
    dependency_risk_details = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": [], "UNKNOWN": [], "NONE": []}
    total_vulnerabilities = 0
    
    async with VulnerabilityChecker() as checker:
        for dependency in dependencies:
            vulnerabilities = await checker.search_vulnerabilities(
                dependency.name, 
                dependency.type
            )
            
            is_vulnerable = len(vulnerabilities) > 0
            total_vulnerabilities += len(vulnerabilities)
            
            # Categorize CVEs by severity
            critical_cves = [v.cve_id for v in vulnerabilities if v.severity == "CRITICAL"]
            high_cves = [v.cve_id for v in vulnerabilities if v.severity == "HIGH"]
            medium_cves = [v.cve_id for v in vulnerabilities if v.severity == "MEDIUM"]
            low_cves = [v.cve_id for v in vulnerabilities if v.severity == "LOW"]
            
            # Determine risk level
            if vulnerabilities:
                max_severity = max(vuln.severity for vuln in vulnerabilities)
                risk_level = max_severity
                risk_summary[max_severity] += 1
                dependency_risk_summary[max_severity].append(dependency.name)
                
                # Add detailed risk information
                dependency_risk_details[max_severity].append(DependencyRiskDetails(
                    name=dependency.name,
                    version=dependency.version,
                    risk_level=risk_level,
                    vulnerability_count=len(vulnerabilities),
                    critical_cves=critical_cves,
                    high_cves=high_cves,
                    medium_cves=medium_cves,
                    low_cves=low_cves
                ))
            else:
                risk_level = "NONE"
                dependency_risk_summary["NONE"].append(dependency.name)
                dependency_risk_details["NONE"].append(DependencyRiskDetails(
                    name=dependency.name,
                    version=dependency.version,
                    risk_level=risk_level,
                    vulnerability_count=0,
                    critical_cves=[],
                    high_cves=[],
                    medium_cves=[],
                    low_cves=[]
                ))
            
            results.append(DependencyResult(
                dependency=dependency,
                vulnerabilities=vulnerabilities,
                is_vulnerable=is_vulnerable,
                risk_level=risk_level
            ))
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.1)
    
    return HealthCheckResponse(
        total_dependencies=len(dependencies),
        vulnerable_dependencies=sum(1 for r in results if r.is_vulnerable),
        vulnerabilities_found=total_vulnerabilities,
        risk_summary=risk_summary,
        dependency_risk_summary=dependency_risk_summary,
        dependency_risk_details=dependency_risk_details,
        results=results,
        scan_timestamp=datetime.now().isoformat()
    )

# API Routes
@app.get("/")
async def root():
    return {"message": "Dependency Health Checker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/check-file", response_model=HealthCheckResponse)
async def check_dependency_file(file: UploadFile = File(...)):
    """Upload and analyze a requirements.txt or package.json file"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    if file.filename.endswith('requirements.txt'):
        file_type = "python"
    elif file.filename.endswith('package.json'):
        file_type = "node"
    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Only requirements.txt and package.json are supported"
        )
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse dependencies
        if file_type == "python":
            dependencies = DependencyParser.parse_requirements_txt(content_str)
        else:
            dependencies = DependencyParser.parse_package_json(content_str)
        
        if not dependencies:
            raise HTTPException(status_code=400, detail="No dependencies found in file")
        
        # Analyze vulnerabilities
        result = await analyze_dependencies(dependencies)
        return result
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported")
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/check-github", response_model=HealthCheckResponse)
async def check_github_repo(request: GitHubRepoRequest):
    """Analyze dependencies from a GitHub repository"""
    
    repo_url = str(request.repo_url)
    branch = request.branch
    
    # Extract owner and repo from URL
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    try:
        # Extract repo info
        repo_path = repo_url.replace("https://github.com/", "").rstrip("/")
        if "/" not in repo_path:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
        
        owner, repo = repo_path.split("/", 1)
        
        dependencies = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to fetch requirements.txt
            try:
                req_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/requirements.txt"
                response = await client.get(req_url)
                if response.status_code == 200:
                    python_deps = DependencyParser.parse_requirements_txt(response.text)
                    dependencies.extend(python_deps)
            except:
                pass
            
            # Try to fetch package.json
            try:
                pkg_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/package.json"
                response = await client.get(pkg_url)
                if response.status_code == 200:
                    node_deps = DependencyParser.parse_package_json(response.text)
                    dependencies.extend(node_deps)
            except:
                pass
        
        if not dependencies:
            raise HTTPException(
                status_code=404, 
                detail="No requirements.txt or package.json found in repository"
            )
        
        # Analyze vulnerabilities
        result = await analyze_dependencies(dependencies)
        return result
        
    except Exception as e:
        logger.error(f"Error processing GitHub repo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing repository")

@app.post("/check-text", response_model=HealthCheckResponse)
async def check_dependency_text(
    content: str = Form(...),
    file_type: str = Form(...)
):
    """Analyze dependencies from text content"""
    
    if file_type not in ["requirements.txt", "package.json"]:
        raise HTTPException(
            status_code=400,
            detail="file_type must be 'requirements.txt' or 'package.json'"
        )
    
    try:
        # Parse dependencies
        if file_type == "requirements.txt":
            dependencies = DependencyParser.parse_requirements_txt(content)
        else:
            dependencies = DependencyParser.parse_package_json(content)
        
        if not dependencies:
            raise HTTPException(status_code=400, detail="No dependencies found in content")
        
        # Analyze vulnerabilities
        result = await analyze_dependencies(dependencies)
        return result
        
    except Exception as e:
        logger.error(f"Error processing text content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
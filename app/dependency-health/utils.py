"""Utility functions for the Dependency Health Checker"""

import re
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def is_valid_github_url(url: str) -> bool:
    """Check if the provided URL is a valid GitHub repository URL"""
    try:
        parsed = urlparse(url)
        if parsed.netloc != "github.com":
            return False
        
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            return False
        
        return True
    except Exception:
        return False

def extract_github_info(url: str) -> Optional[Dict[str, str]]:
    """Extract owner and repository name from GitHub URL"""
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        
        if len(path_parts) >= 2:
            return {
                "owner": path_parts[0],
                "repo": path_parts[1]
            }
    except Exception as e:
        logger.error(f"Error extracting GitHub info: {str(e)}")
    
    return None

def normalize_version(version_string: str) -> str:
    """Normalize version string by removing prefixes and suffixes"""
    # Remove common prefixes
    version_clean = re.sub(r'^[~^>=<]+', '', version_string.strip())
    
    # Remove build metadata and pre-release identifiers
    version_clean = re.split(r'[-+]', version_clean)[0]
    
    # Handle special cases
    if version_clean in ['*', 'latest', '']:
        return 'latest'
    
    return version_clean

def parse_requirement_line(line: str) -> Optional[Dict[str, str]]:
    """Parse a single line from requirements.txt"""
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None
    
    # Handle different operators
    operators = ['==', '>=', '<=', '>', '<', '~=']
    
    for op in operators:
        if op in line:
            parts = line.split(op, 1)
            if len(parts) == 2:
                name = parts[0].strip()
                version = parts[1].split('[')[0].split(';')[0].strip()
                return {
                    "name": name,
                    "version": normalize_version(version),
                    "operator": op
                }
    
    # No version specified
    name = line.split('[')[0].split(';')[0].strip()
    return {
        "name": name,
        "version": "latest",
        "operator": ""
    }

def calculate_risk_score(vulnerabilities: List[Dict]) -> int:
    """Calculate a risk score based on vulnerabilities"""
    score = 0
    severity_weights = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4,
        "LOW": 2,
        "UNKNOWN": 1
    }
    
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "UNKNOWN")
        score += severity_weights.get(severity, 1)
    
    return score

def format_vulnerability_summary(vulnerabilities: List[Dict]) -> str:
    """Create a human-readable summary of vulnerabilities"""
    if not vulnerabilities:
        return "No vulnerabilities found"
    
    severity_counts = {}
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    summary_parts = []
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            summary_parts.append(f"{count} {severity.lower()}")
    
    return f"{len(vulnerabilities)} vulnerabilities found: " + ", ".join(summary_parts)

def sanitize_package_name(name: str) -> str:
    """Sanitize package name for API queries"""
    # Remove common prefixes and suffixes
    name = name.strip().lower()
    
    # Remove scope for npm packages (e.g., @types/node -> node)
    if name.startswith('@'):
        parts = name.split('/')
        if len(parts) > 1:
            name = parts[1]
    
    return name

def is_version_affected(package_version: str, affected_ranges: List[str]) -> bool:
    """Check if a package version is affected by vulnerability ranges"""
    # This is a simplified version check
    # In production, you'd want to use proper version comparison libraries
    
    if package_version == "latest":
        return True  # Assume latest might be affected
    
    # For now, return True if we can't determine (conservative approach)
    return True

def generate_report_id() -> str:
    """Generate a unique report ID"""
    import uuid
    return str(uuid.uuid4())[:8]

def validate_file_content(content: str, file_type: str) -> bool:
    """Validate file content based on type"""
    try:
        if file_type == "package.json":
            json.loads(content)
            return True
        elif file_type == "requirements.txt":
            # Basic validation - check if it looks like requirements format
            lines = content.strip().split('\n')
            valid_lines = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if parse_requirement_line(line):
                    valid_lines += 1
            return valid_lines > 0
    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        return False
    
    return False

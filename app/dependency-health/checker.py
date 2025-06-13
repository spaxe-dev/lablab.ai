"""
Vulnerability Checker Module
Checks dependencies for known security vulnerabilities using NVD API
"""
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class VulnerabilityChecker:
    """Check dependencies for security vulnerabilities using NVD API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers
        headers = {
            'User-Agent': 'Dependency-Health-Monitor/1.0',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            headers['apiKey'] = self.api_key
            
        self.session.headers.update(headers)
        
        # Rate limiting (without API key: 5 requests per 30 seconds)
        # With API key: 50 requests per 30 seconds
        self.rate_limit = 50 if api_key else 5
        self.time_window = 30
        self.request_times = []
    
    def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        now = time.time()
        
        # Remove requests older than time window
        self.request_times = [t for t in self.request_times if now - t < self.time_window]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.rate_limit:
            sleep_time = self.time_window - (now - self.request_times[0])
            if sleep_time > 0:
                print(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def search_vulnerabilities(self, package_name: str, version: Optional[str] = None) -> Dict:
        """
        Search for vulnerabilities for a specific package
        
        Args:
            package_name (str): Name of the package to search for
            version (str, optional): Specific version to check
            
        Returns:
            Dict: Vulnerability information
        """
        self._rate_limit_check()
        
        # Build search parameters - use a simpler approach
        params = {
            'keywordSearch': f"{package_name} python",  # Add python to narrow search
            'resultsPerPage': 10
        }
        
        try:
            print(f"Searching NVD for: {package_name}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            # Handle different response codes
            if response.status_code == 403:
                print(f"Rate limited by NVD API. Waiting...")
                time.sleep(10)
                response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 404:
                print(f"No vulnerabilities found for {package_name} (404)")
                return {
                    'package_name': package_name,
                    'package_version': version,
                    'total_results': 0,
                    'vulnerabilities': [],
                    'search_timestamp': datetime.now().isoformat()
                }
            
            if response.status_code != 200:
                print(f"API returned status code {response.status_code} for {package_name}")
                return {
                    'package_name': package_name,
                    'package_version': version,
                    'error': f'API returned status code {response.status_code}',
                    'vulnerabilities': [],
                    'search_timestamp': datetime.now().isoformat()
                }
            
            data = response.json()
            vulnerabilities = []
            
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    cve_data = vuln.get('cve', {})
                    
                    # Extract basic CVE information
                    cve_id = cve_data.get('id', 'Unknown')
                    
                    # Get description
                    descriptions = cve_data.get('descriptions', [])
                    description = ''
                    for desc in descriptions:
                        if desc.get('lang') == 'en':
                            description = desc.get('value', '')
                            break
                    
                    # Filter out irrelevant results
                    if package_name.lower() not in description.lower():
                        continue
                    
                    # Get CVSS scores
                    metrics = cve_data.get('metrics', {})
                    cvss_score = None
                    severity = 'Unknown'
                    
                    # Try CVSS v3.1 first, then v3.0, then v2.0
                    for version_key in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                        if version_key in metrics and metrics[version_key]:
                            metric = metrics[version_key][0]
                            if version_key.startswith('cvssMetricV3'):
                                cvss_data = metric.get('cvssData', {})
                                cvss_score = cvss_data.get('baseScore')
                                severity = cvss_data.get('baseSeverity', 'Unknown')
                            else:  # v2
                                cvss_data = metric.get('cvssData', {})
                                cvss_score = cvss_data.get('baseScore')
                                # Convert v2 score to severity
                                if cvss_score:
                                    if cvss_score >= 7.0:
                                        severity = 'HIGH'
                                    elif cvss_score >= 4.0:
                                        severity = 'MEDIUM'
                                    else:
                                        severity = 'LOW'
                            break
                    
                    # Get published and modified dates
                    published = cve_data.get('published', '')
                    last_modified = cve_data.get('lastModified', '')
                    
                    # Get references
                    references = []
                    ref_data = cve_data.get('references', [])
                    for ref in ref_data[:3]:  # Limit to first 3 references
                        references.append({
                            'url': ref.get('url', ''),
                            'source': ref.get('source', '')
                        })
                    
                    vulnerability_info = {
                        'cve_id': cve_id,
                        'description': description,
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'published_date': published,
                        'last_modified': last_modified,
                        'references': references,
                        'package_name': package_name,
                        'package_version': version
                    }
                    
                    vulnerabilities.append(vulnerability_info)
            
            return {
                'package_name': package_name,
                'package_version': version,
                'total_results': data.get('totalResults', 0),
                'vulnerabilities': vulnerabilities,
                'search_timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching vulnerabilities for {package_name}: {str(e)}")
            return {
                'package_name': package_name,
                'package_version': version,
                'error': str(e),
                'vulnerabilities': [],
                'search_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Unexpected error for {package_name}: {str(e)}")
            return {
                'package_name': package_name,
                'package_version': version,
                'error': str(e),
                'vulnerabilities': [],
                'search_timestamp': datetime.now().isoformat()
            }
    
    def check_multiple_packages(self, packages: List[Dict[str, str]]) -> List[Dict]:
        """
        Check multiple packages for vulnerabilities
        
        Args:
            packages (List[Dict]): List of package dictionaries with name and version
            
        Returns:
            List[Dict]: List of vulnerability results for each package
        """
        results = []
        
        for i, package in enumerate(packages):
            package_name = package.get('name', '')
            version = package.get('version')
            
            print(f"Checking {i+1}/{len(packages)}: {package_name}")
            
            result = self.search_vulnerabilities(package_name, version)
            results.append(result)
            
            # Small delay between requests to be respectful
            time.sleep(2)
        
        return results
    
    def get_severity_summary(self, results: List[Dict]) -> Dict:
        """
        Get a summary of vulnerabilities by severity
        
        Args:
            results (List[Dict]): List of vulnerability check results
            
        Returns:
            Dict: Summary of vulnerabilities by severity
        """
        summary = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'Unknown': 0,
            'total_packages': len(results),
            'vulnerable_packages': 0,
            'total_vulnerabilities': 0
        }
        
        for result in results:
            if result.get('vulnerabilities'):
                summary['vulnerable_packages'] += 1
                
                for vuln in result['vulnerabilities']:
                    severity = vuln.get('severity', 'Unknown')
                    if severity in summary:
                        summary[severity] += 1
                    summary['total_vulnerabilities'] += 1
        
        return summary

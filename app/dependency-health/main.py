"""
Dependency Health Monitor - Main Application
A tool that scans project dependencies for security vulnerabilities and health issues
"""
import os
import sys
import json
import argparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Optional

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import DependencyParser
from checker import VulnerabilityChecker

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js backend integration

# Global instances
dependency_parser = DependencyParser()
vulnerability_checker = VulnerabilityChecker()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'dependency-health-monitor'
    })

@app.route('/api/scan', methods=['POST'])
def scan_dependencies():
    """
    Scan dependencies for vulnerabilities
    Expects JSON payload with requirements_file path or requirements_content
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle file path or direct content
        requirements_file = data.get('requirements_file')
        requirements_content = data.get('requirements_content')
        
        if not requirements_file and not requirements_content:
            return jsonify({'error': 'Either requirements_file or requirements_content must be provided'}), 400
        
        # Parse dependencies
        if requirements_file:
            # Check if file exists
            if not os.path.exists(requirements_file):
                return jsonify({'error': f'Requirements file not found: {requirements_file}'}), 404
            
            dependencies = dependency_parser.parse_requirements_file(requirements_file)
        else:
            # Create temporary file from content
            temp_file_path = 'temp_requirements.txt'
            try:
                with open(temp_file_path, 'w') as f:
                    f.write(requirements_content)
                dependencies = dependency_parser.parse_requirements_file(temp_file_path)
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        
        if not dependencies:
            return jsonify({'error': 'No dependencies found or could not parse requirements'}), 400
        
        # Prepare packages for vulnerability checking
        packages_to_check = []
        for dep in dependencies:
            package_info = {
                'name': dep['name'],
                'version': dependency_parser.extract_version_from_spec(dep['specifier'])
            }
            packages_to_check.append(package_info)
        
        # Check for vulnerabilities
        vulnerability_results = vulnerability_checker.check_multiple_packages(packages_to_check)
        
        # Get severity summary
        severity_summary = vulnerability_checker.get_severity_summary(vulnerability_results)
        
        # Prepare response
        response_data = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_dependencies': len(dependencies),
            'dependencies_analyzed': len(packages_to_check),
            'severity_summary': severity_summary,
            'dependencies': dependencies,
            'vulnerability_results': vulnerability_results
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/scan/file', methods=['POST'])
def scan_requirements_file():
    """
    Scan a specific requirements.txt file
    Expects form data with file upload
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith(('.txt', '.in')):
            return jsonify({'error': 'File must be a requirements file (.txt or .in)'}), 400
        
        # Read file content
        requirements_content = file.read().decode('utf-8')
        
        # Use the scan endpoint logic
        return scan_dependencies_from_content(requirements_content)
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

def scan_dependencies_from_content(content: str) -> Dict:
    """Helper function to scan dependencies from content"""
    # Create temporary file
    temp_file_path = 'temp_requirements.txt'
    try:
        with open(temp_file_path, 'w') as f:
            f.write(content)
        
        dependencies = dependency_parser.parse_requirements_file(temp_file_path)
        
        if not dependencies:
            return {'error': 'No dependencies found or could not parse requirements'}
        
        # Prepare packages for vulnerability checking
        packages_to_check = []
        for dep in dependencies:
            package_info = {
                'name': dep['name'],
                'version': dependency_parser.extract_version_from_spec(dep['specifier'])
            }
            packages_to_check.append(package_info)
        
        # Check for vulnerabilities
        vulnerability_results = vulnerability_checker.check_multiple_packages(packages_to_check)
        
        # Get severity summary
        severity_summary = vulnerability_checker.get_severity_summary(vulnerability_results)
        
        return {
            'scan_timestamp': datetime.now().isoformat(),
            'total_dependencies': len(dependencies),
            'dependencies_analyzed': len(packages_to_check),
            'severity_summary': severity_summary,
            'dependencies': dependencies,
            'vulnerability_results': vulnerability_results
        }
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.route('/api/package/<package_name>', methods=['GET'])
def check_single_package(package_name: str):
    """
    Check a single package for vulnerabilities
    """
    try:
        version = request.args.get('version')
        
        result = vulnerability_checker.search_vulnerabilities(package_name, version)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Error checking package: {str(e)}'}), 500

@app.route('/api/packages', methods=['POST'])
def check_multiple_packages():
    """
    Check multiple packages for vulnerabilities
    Expects JSON payload with list of packages: [{"name": "package", "version": "1.0.0"}]
    """
    try:
        data = request.get_json()
        
        if not data or 'packages' not in data:
            return jsonify({'error': 'No packages provided'}), 400
        
        packages = data['packages']
        
        if not isinstance(packages, list):
            return jsonify({'error': 'Packages must be a list'}), 400
        
        # Validate package format
        for pkg in packages:
            if not isinstance(pkg, dict) or 'name' not in pkg:
                return jsonify({'error': 'Each package must have a name field'}), 400
        
        # Check vulnerabilities
        results = vulnerability_checker.check_multiple_packages(packages)
        severity_summary = vulnerability_checker.get_severity_summary(results)
        
        return jsonify({
            'scan_timestamp': datetime.now().isoformat(),
            'packages_checked': len(packages),
            'severity_summary': severity_summary,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Error checking packages: {str(e)}'}), 500

def main():
    """Main function to run the dependency health monitor"""
    parser = argparse.ArgumentParser(description='Dependency Health Monitor')
    parser.add_argument('--file', '-f', type=str, help='Path to requirements.txt file to scan')
    parser.add_argument('--server', '-s', action='store_true', help='Start the Flask API server')
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port for the Flask server (default: 5000)')
    parser.add_argument('--host', type=str, default='localhost', help='Host for the Flask server (default: localhost)')
    parser.add_argument('--api-key', type=str, help='NVD API key for higher rate limits')
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        global vulnerability_checker
        vulnerability_checker = VulnerabilityChecker(api_key=args.api_key)
    
    if args.server:
        print(f"Starting Dependency Health Monitor API server on {args.host}:{args.port}")
        print("Available endpoints:")
        print(f"  GET  {args.host}:{args.port}/health - Health check")
        print(f"  POST {args.host}:{args.port}/api/scan - Scan dependencies")
        print(f"  POST {args.host}:{args.port}/api/scan/file - Upload and scan requirements file")
        print(f"  GET  {args.host}:{args.port}/api/package/<name> - Check single package")
        print(f"  POST {args.host}:{args.port}/api/packages - Check multiple packages")
        
        app.run(host=args.host, port=args.port, debug=True)
    
    elif args.file:
        # Command line scanning
        print(f"Scanning dependencies in: {args.file}")
        
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found")
            return 1
        
        # Parse dependencies
        dependencies = dependency_parser.parse_requirements_file(args.file)
        
        if not dependencies:
            print("No dependencies found or could not parse requirements file")
            return 1
        
        print(f"Found {len(dependencies)} dependencies:")
        for dep in dependencies:
            print(f"  - {dep['name']} {dep['specifier']}")
        
        # Prepare packages for vulnerability checking
        packages_to_check = []
        for dep in dependencies:
            package_info = {
                'name': dep['name'],
                'version': dependency_parser.extract_version_from_spec(dep['specifier'])
            }
            packages_to_check.append(package_info)
        
        print("\nChecking for vulnerabilities...")
        
        # Check for vulnerabilities
        vulnerability_results = vulnerability_checker.check_multiple_packages(packages_to_check)
        
        # Display results
        severity_summary = vulnerability_checker.get_severity_summary(vulnerability_results)
        
        print(f"\n=== VULNERABILITY SCAN RESULTS ===")
        print(f"Total packages scanned: {severity_summary['total_packages']}")
        print(f"Vulnerable packages: {severity_summary['vulnerable_packages']}")
        print(f"Total vulnerabilities: {severity_summary['total_vulnerabilities']}")
        
        print(f"\nSeverity breakdown:")
        print(f"  CRITICAL: {severity_summary['CRITICAL']}")
        print(f"  HIGH: {severity_summary['HIGH']}")
        print(f"  MEDIUM: {severity_summary['MEDIUM']}")
        print(f"  LOW: {severity_summary['LOW']}")
        
        # Show detailed results for vulnerable packages
        for result in vulnerability_results:
            if result.get('vulnerabilities'):
                print(f"\n📦 {result['package_name']} ({result['package_version'] or 'any version'})")
                print(f"   Found {len(result['vulnerabilities'])} vulnerabilities:")
                
                for vuln in result['vulnerabilities']:
                    severity_icon = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟠', 
                        'MEDIUM': '🟡',
                        'LOW': '🟢'
                    }.get(vuln['severity'], '⚪')
                    
                    print(f"   {severity_icon} {vuln['cve_id']} - {vuln['severity']}")
                    if vuln['cvss_score']:
                        print(f"      CVSS Score: {vuln['cvss_score']}")
                    print(f"      {vuln['description'][:100]}...")
        
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    exit(main())
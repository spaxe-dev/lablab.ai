"""
Test script for the Dependency Health Monitor API
"""
import requests
import json

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("=== HEALTH CHECK ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_scan_endpoint():
    """Test the scan endpoint with requirements content"""
    try:
        test_requirements = """
flask==2.2.0
requests==2.28.0
django==3.2.0
"""
        
        payload = {
            'requirements_content': test_requirements
        }
        
        response = requests.post(
            'http://localhost:5000/api/scan',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print("\n=== SCAN ENDPOINT TEST ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total dependencies: {data['total_dependencies']}")
            print(f"Dependencies analyzed: {data['dependencies_analyzed']}")
            print(f"Vulnerable packages: {data['severity_summary']['vulnerable_packages']}")
            print(f"Total vulnerabilities: {data['severity_summary']['total_vulnerabilities']}")
            print("Severity breakdown:", data['severity_summary'])
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Scan endpoint test failed: {e}")
        return False

def test_single_package_endpoint():
    """Test the single package endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/package/flask?version=2.2.0')
        
        print("\n=== SINGLE PACKAGE TEST ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Package: {data['package_name']}")
            print(f"Version: {data['package_version']}")
            print(f"Vulnerabilities found: {len(data['vulnerabilities'])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Single package test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Testing Dependency Health Monitor API")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test scan endpoint
        scan_ok = test_scan_endpoint()
        
        # Test single package endpoint
        package_ok = test_single_package_endpoint()
        
        print("\n" + "=" * 50)
        print("🎉 API Tests Summary:")
        print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        print(f"Scan Endpoint: {'✅ PASS' if scan_ok else '❌ FAIL'}")
        print(f"Single Package: {'✅ PASS' if package_ok else '❌ FAIL'}")
        
        if health_ok and scan_ok and package_ok:
            print("\n🎉 All tests passed! API is ready for integration.")
        else:
            print("\n⚠️ Some tests failed. Check the API server.")
    else:
        print("\n❌ Health check failed. Make sure the API server is running.")

if __name__ == "__main__":
    main()

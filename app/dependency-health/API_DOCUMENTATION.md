# Dependency Health Monitor API

A Flask-based API service that scans Python dependencies for security vulnerabilities using the National Vulnerability Database (NVD) API.

## Features

- **Dependency Parsing**: Parses `requirements.txt` files to extract dependency information
- **Vulnerability Scanning**: Checks dependencies against the NVD database for known CVEs
- **REST API**: Provides endpoints for integration with web applications
- **Rate Limiting**: Handles NVD API rate limits automatically
- **CORS Support**: Enabled for frontend integration

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-14T10:30:00.000Z",
  "service": "dependency-health-monitor"
}
```

### Scan Dependencies
```
POST /api/scan
```
Scans dependencies for vulnerabilities from a requirements file or content.

**Request Body:**
```json
{
  "requirements_file": "/path/to/requirements.txt",
  // OR
  "requirements_content": "flask==2.3.3\nrequests==2.31.0"
}
```

**Response:**
```json
{
  "scan_timestamp": "2025-06-14T10:30:00.000Z",
  "total_dependencies": 5,
  "dependencies_analyzed": 5,
  "severity_summary": {
    "CRITICAL": 0,
    "HIGH": 2,
    "MEDIUM": 1,
    "LOW": 0,
    "total_packages": 5,
    "vulnerable_packages": 2,
    "total_vulnerabilities": 3
  },
  "dependencies": [
    {
      "name": "flask",
      "raw_line": "flask==2.3.3",
      "line_number": 1,
      "specifier": "==2.3.3",
      "versions": [
        {
          "operator": "==",
          "version": "2.3.3"
        }
      ]
    }
  ],
  "vulnerability_results": [
    {
      "package_name": "flask",
      "package_version": "2.3.3",
      "total_results": 1,
      "vulnerabilities": [
        {
          "cve_id": "CVE-2023-30861",
          "description": "Flask before 2.2.5 and 2.3.x before 2.3.2 has a security vulnerability...",
          "cvss_score": 7.5,
          "severity": "HIGH",
          "published_date": "2023-05-02T18:15:00.000",
          "last_modified": "2023-05-15T13:52:00.000",
          "references": [
            {
              "url": "https://github.com/pallets/flask/security/advisories/GHSA-m2qf-hxjv-5gpq",
              "source": "github.com/advisories",
              "tags": ["Vendor Advisory"]
            }
          ]
        }
      ]
    }
  ]
}
```

### Upload and Scan File
```
POST /api/scan/file
```
Upload a requirements file and scan for vulnerabilities.

**Request:** Multipart form data with file field named `file`

**Response:** Same as `/api/scan`

### Check Single Package
```
GET /api/package/{package_name}?version={version}
```
Check a single package for vulnerabilities.

**Parameters:**
- `package_name`: Name of the package
- `version` (optional): Specific version to check

**Response:**
```json
{
  "package_name": "requests",
  "package_version": "2.31.0",
  "total_results": 0,
  "vulnerabilities": [],
  "search_timestamp": "2025-06-14T10:30:00.000Z"
}
```

### Check Multiple Packages
```
POST /api/packages
```
Check multiple packages for vulnerabilities.

**Request Body:**
```json
{
  "packages": [
    {"name": "flask", "version": "2.3.3"},
    {"name": "requests", "version": "2.31.0"}
  ]
}
```

**Response:**
```json
{
  "scan_timestamp": "2025-06-14T10:30:00.000Z",
  "packages_checked": 2,
  "severity_summary": {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 0,
    "LOW": 0,
    "total_packages": 2,
    "vulnerable_packages": 1,
    "total_vulnerabilities": 1
  },
  "results": [...]
}
```

## Usage

### Command Line Interface

```bash
# Scan a requirements file
python main.py --file requirements.txt

# Start the API server
python main.py --server --port 5000 --host localhost

# Use with NVD API key for higher rate limits
python main.py --server --api-key YOUR_API_KEY
```

### Integration with Next.js Backend

```javascript
// Example Next.js API route
export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const response = await fetch('http://localhost:5000/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requirements_content: req.body.requirements
        })
      });
      
      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      res.status(500).json({ error: 'Failed to scan dependencies' });
    }
  }
}
```

## Environment Variables

- `NVD_API_KEY`: Optional NVD API key for higher rate limits (50 req/30s vs 5 req/30s)
- `FLASK_ENV`: Set to `development` for debug mode

## Rate Limiting

The service automatically handles NVD API rate limiting:
- **Without API key**: 5 requests per 30 seconds
- **With API key**: 50 requests per 30 seconds

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (file not found)
- `500`: Internal Server Error

Error responses include a descriptive message:
```json
{
  "error": "Description of the error"
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python main.py --server
```

The service will start on `http://localhost:5000` by default.

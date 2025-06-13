# Dependency Health Monitor

A Python-based tool that scans project dependencies for security vulnerabilities using the National Vulnerability Database (NVD). This tool can be used as a standalone CLI application or as a Flask API service for integration with web applications.

## Features

- 🔍 **Dependency Analysis**: Parses `requirements.txt` files and extracts dependency information
- 🛡️ **Vulnerability Scanning**: Checks dependencies against the NVD database for known CVEs
- 📊 **Severity Classification**: Categorizes vulnerabilities by severity (CRITICAL, HIGH, MEDIUM, LOW)
- 🌐 **REST API**: Provides HTTP endpoints for web application integration
- ⚡ **Rate Limiting**: Automatically handles NVD API rate limits
- 🔌 **CORS Support**: Enabled for frontend integration
- 📝 **Detailed Reports**: Provides comprehensive vulnerability information including CVSS scores

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
python setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up configuration files
- Run a health check

### Option 2: Manual Setup

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Scan a requirements file:**
```bash
python main.py --file requirements.txt
```

**Start API server:**
```bash
python main.py --server --port 5000
```

**Use with NVD API key (recommended for higher rate limits):**
```bash
python main.py --server --api-key YOUR_NVD_API_KEY
```

### API Server

Start the server and access these endpoints:

- `GET /health` - Health check
- `POST /api/scan` - Scan dependencies from file path or content
- `POST /api/scan/file` - Upload and scan requirements file
- `GET /api/package/<name>` - Check single package
- `POST /api/packages` - Check multiple packages

### Integration with Next.js Backend

Create an API route in your Next.js backend:

```javascript
// pages/api/scan-dependencies.js
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

## Example Output

```
=== VULNERABILITY SCAN RESULTS ===
Total packages scanned: 5
Vulnerable packages: 2
Total vulnerabilities: 3

Severity breakdown:
  CRITICAL: 0
  HIGH: 2
  MEDIUM: 1
  LOW: 0

📦 flask (2.3.3)
   Found 1 vulnerabilities:
   🟠 CVE-2023-30861 - HIGH
      CVSS Score: 7.5
      Flask before 2.2.5 and 2.3.x before 2.3.2 has a security vulnerability...

📦 requests (2.28.0)
   Found 2 vulnerabilities:
   🟠 CVE-2023-32681 - HIGH
      CVSS Score: 6.1
      Requests before 2.31.0 has a security vulnerability...
```

## Configuration

### Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
# NVD API Key (optional, for higher rate limits)
NVD_API_KEY=your_api_key_here

# Flask Configuration
FLASK_HOST=localhost
FLASK_PORT=5000
FLASK_ENV=development
```

### NVD API Key

Get a free API key from [NVD](https://nvd.nist.gov/developers/request-an-api-key) for higher rate limits:
- Without API key: 5 requests per 30 seconds
- With API key: 50 requests per 30 seconds

## API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API reference.

## Architecture

```
dependency-health/
├── main.py              # Main application and Flask API
├── parser.py            # Requirements file parser
├── checker.py           # Vulnerability checker using NVD API
├── requirements.txt     # Python dependencies
├── setup.py            # Automated setup script
├── .env.example        # Environment configuration template
└── API_DOCUMENTATION.md # API reference
```

## Components

- **DependencyParser**: Parses `requirements.txt` files using the `packaging` library
- **VulnerabilityChecker**: Queries the NVD API for vulnerability information
- **Flask API**: Provides HTTP endpoints for web integration
- **CLI Interface**: Command-line tool for direct usage

## GitHub App Integration (Future)

This tool is designed to be extended as a GitHub App similar to Dependabot:

1. **Webhook Handling**: React to repository events
2. **Automated Scanning**: Scan dependencies on commits/PRs
3. **Issue Creation**: Create GitHub issues for vulnerabilities
4. **PR Comments**: Add vulnerability reports to pull requests

## Rate Limiting

The tool automatically handles NVD API rate limiting with exponential backoff and request queuing.

## Error Handling

- Graceful handling of network errors
- Malformed requirements file parsing
- API rate limit management
- Detailed error reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the API documentation
2. Review error messages carefully
3. Ensure your NVD API key is valid (if using one)
4. Check network connectivity to NVD API

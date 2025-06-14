# Dependency Health Checker

A FastAPI-based web application that analyzes Python `requirements.txt` and Node.js `package.json` files for security vulnerabilities using the National Vulnerability Database (NVD).

## Features

- 🔍 **Vulnerability Scanning**: Analyzes dependencies against the NVD database
- 📁 **File Upload Support**: Upload `requirements.txt` or `package.json` files
- 🐙 **GitHub Integration**: Analyze repositories directly from GitHub URLs
- 📊 **Risk Assessment**: Categorizes vulnerabilities by severity (Critical, High, Medium, Low)
- 🚀 **FastAPI Backend**: High-performance async API with automatic documentation
- 🌐 **CORS Support**: Ready for Next.js frontend integration

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

### Vulnerability Checking

- `POST /check-file` - Upload and analyze a dependency file
- `POST /check-github` - Analyze GitHub repository dependencies
- `POST /check-text` - Analyze dependency content from text

## Quick Start

### Local Development

1. **Create virtual environment and install dependencies:**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac  
source venv/bin/activate

pip install -r requirements.txt
```

2. **Start the server:**

```bash
python main.py
```

The server will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### Render Deployment

For production deployment on Render, the service automatically uses:
- `Procfile` for process definition
- `runtime.txt` for Python version
- `requirements.txt` for dependencies

No additional setup scripts needed!

## API Usage Examples

### Upload File

```bash
curl -X POST "http://localhost:8000/check-file" \
  -F "file=@requirements.txt"
```

### Check GitHub Repository

```bash
curl -X POST "http://localhost:8000/check-github" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repo",
    "branch": "main"
  }'
```

### Check Text Content

```bash
curl -X POST "http://localhost:8000/check-text" \
  -F "content=requests==2.25.1\nflask==1.1.4" \
  -F "file_type=requirements.txt"
```

## Response Format

```json
{
  "total_dependencies": 5,
  "vulnerable_dependencies": 2,
  "vulnerabilities_found": 3,
  "risk_summary": {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 0,
    "UNKNOWN": 0
  },
  "results": [
    {
      "dependency": {
        "name": "requests",
        "version": "2.25.1",
        "type": "python"
      },
      "vulnerabilities": [
        {
          "cve_id": "CVE-2023-32681",
          "description": "Requests library vulnerability...",
          "severity": "MEDIUM",
          "published_date": "2023-05-26T18:15:00",
          "affected_versions": [],
          "fixed_versions": []
        }
      ],
      "is_vulnerable": true,
      "risk_level": "MEDIUM"
    }
  ],
  "scan_timestamp": "2025-06-14T10:30:00"
}
```

## Integration with Next.js

The API is designed to work seamlessly with a Next.js backend. Here's how to integrate:

### 1. Next.js API Route Example

```javascript
// pages/api/check-dependencies.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch('http://localhost:8000/check-file', {
      method: 'POST',
      body: req.body, // Forward the file upload
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to check dependencies' });
  }
}
```

### 2. Frontend Integration

```javascript
// Frontend component
const checkDependencies = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/check-dependencies', {
    method: 'POST',
    body: formData,
  });

  return response.json();
};
```

## Configuration

### Environment Variables

- `NVD_API_KEY` - Optional NVD API key for higher rate limits
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Rate Limiting

The application includes built-in rate limiting to respect the NVD API limits:
- 0.1 second delay between requests
- Maximum 60 requests per minute

## Supported File Formats

### requirements.txt
```
requests==2.25.1
flask>=1.1.0
django~=3.2.0
numpy
```

### package.json
```json
{
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "~4.17.19"
  },
  "devDependencies": {
    "jest": "^26.6.0"
  }
}
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI        │    │   NVD API       │
│   Frontend      │───▶│   Backend        │───▶│   Database      │
│                 │    │   (Port 8000)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Development

### Project Structure

```
dependency-health/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── setup.bat           # Setup script
├── start.bat           # Start script
├── test_api.py         # API test suite
└── README.md           # This file
```

### Adding New Features

1. **New Vulnerability Sources**: Extend the `VulnerabilityChecker` class
2. **File Format Support**: Add parsers to `DependencyParser` class
3. **Risk Scoring**: Modify the `calculate_risk_score` function in `utils.py`

## Error Handling

The API provides detailed error responses:

```json
{
  "detail": "No dependencies found in file",
  "status_code": 400
}
```

Common error codes:
- `400` - Bad request (invalid file format, no dependencies found)
- `404` - Not found (GitHub repository or files not found)
- `422` - Validation error (invalid request format)
- `500` - Internal server error

## Security Considerations

- File upload size limited to 5MB
- Input validation for all endpoints
- Rate limiting to prevent abuse
- CORS configured for specific origins only

## Performance

- Async operations for concurrent vulnerability checking
- Connection pooling for HTTP requests
- Caching can be added for repeated dependency checks
- Background task support for large repositories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Run the test suite with `python test_api.py`
3. Check server logs for detailed error information

---

**Note**: This application is designed for the lablab.ai hackathon and integrates with the Next.js backend for a complete dependency management solution.

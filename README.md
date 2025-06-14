# �️ Dependency Health Checker

A comprehensive security vulnerability scanner for Python and Node.js dependencies, built with FastAPI and Next.js. Designed for the LabLab.ai hackathon to help developers identify and manage security risks in their projects.

## ✨ Features

- 🔍 **Multi-Format Support**: Analyze `requirements.txt`, `package.json`, and raw text
- 🐙 **GitHub Integration**: Direct repository scanning via GitHub URLs
- 📊 **Risk Assessment**: Categorizes vulnerabilities by severity (Critical, High, Medium, Low)
- 🛡️ **NVD Integration**: Real-time vulnerability data from National Vulnerability Database
- 🚀 **High Performance**: Async FastAPI backend with concurrent vulnerability checking
- 🌐 **Web Interface**: Simple HTML/JS frontend for easy testing
- 📡 **RESTful API**: Well-documented endpoints with OpenAPI/Swagger docs

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTML/JS Frontend  │    │   Next.js API    │    │   FastAPI       │
│   (Static Files)    │───▶│   Proxy Layer    │───▶│   Service       │
│                     │    │   (Port 3000)    │    │   (Port 8000)   │
└─────────────────────┘    └──────────────────┘    └─────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │   NVD API       │
                           │   (External)    │
                           └─────────────────┘
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.10+ (for FastAPI service)
- Node.js 18+ (for Next.js backend)
- Git

### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd lablab.ai
```

### **2. Start the FastAPI Service**
```bash
cd app/dependency-health

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the service
python main.py
```

The FastAPI service will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### **3. Start the Next.js Backend**
```bash
cd backend
npm install
npm run dev
```

The Next.js backend will be available at:
- Backend: http://localhost:3000
- API Status: http://localhost:3000/api/status

### **4. Open the Frontend**
Simply open `frontend/index.html` in your browser, or serve it with a local server:

```bash
# Using Python
cd frontend
python -m http.server 8080

# Using Node.js (if you have serve installed)
npx serve frontend
```

## 📡 API Endpoints

### **System Status**
- `GET /api/status` - Check service health and get endpoint overview

### **Dependency Health (via Next.js Proxy)**
- `POST /api/dependency-health/check-file` - Upload dependency files
- `POST /api/dependency-health/check-github` - Analyze GitHub repositories  
- `POST /api/dependency-health/check-text` - Analyze text content
- `GET /api/dependency-health/health` - Service health check

### **Direct FastAPI Endpoints**
- `POST /check-file` - Upload and analyze dependency files
- `POST /check-github` - Analyze GitHub repository dependencies
- `POST /check-text` - Analyze dependency content from text
- `GET /health` - FastAPI service health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## 🛠️ Tech Stack

**Backend Services:**
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and serialization
- **HTTPX** - Async HTTP client for external API calls
- **Uvicorn** - ASGI server for running FastAPI

**API Proxy Layer:**
- **Next.js 15** - React-based API backend and service integration
- **TypeScript** - Type-safe backend development

**Frontend:**
- **HTML5/CSS3** - Simple, responsive web interface
- **Vanilla JavaScript** - No framework dependencies
- **Fetch API** - Modern HTTP client for API calls

**External Services:**
- **NVD API** - National Vulnerability Database
- **GitHub API** - Repository access and analysis

**Deployment:**
- **Render** - Cloud hosting platform
- **Python 3.10+** - Runtime environment

## 📁 Project Structure

```
lablab.ai/
├── app/
│   └── dependency-health/          # FastAPI service
│       ├── main.py                 # FastAPI application
│       ├── config.py              # Configuration settings
│       ├── utils.py               # Utility functions
│       ├── requirements.txt       # Python dependencies
│       ├── Procfile              # Render deployment config
│       ├── runtime.txt           # Python version specification
│       └── README.md             # Service documentation
├── backend/                       # Next.js API proxy
│   ├── src/app/api/              # API routes
│   │   ├── status/               # System status endpoint
│   │   └── dependency-health/    # Proxy endpoints
│   ├── package.json              # Node.js dependencies
│   ├── next.config.ts            # Next.js configuration
│   └── render.yaml               # Render deployment config
├── frontend/
│   ├── index.html                # Web interface
│   └── (static assets)
├── README.md                     # This file
└── requirements.txt              # Root Python dependencies
```

## ⚙️ Configuration

### **Environment Variables**

**For Local Development:**
```env
# Optional: NVD API key for higher rate limits
NVD_API_KEY=your_nvd_api_key_here

# FastAPI service URL (used by Next.js backend)
DEPENDENCY_HEALTH_URL=http://localhost:8000
```

**For Production (Render):**
```env
# FastAPI service URL
DEPENDENCY_HEALTH_URL=https://your-fastapi-service.onrender.com

# Optional: NVD API key
NVD_API_KEY=your_nvd_api_key_here
```

### **Rate Limiting**
The application includes built-in rate limiting to respect NVD API limits:
- 0.1 second delay between requests
- Maximum 50 results per query
- Graceful error handling for API timeouts

## 🎯 Usage Examples

### **1. File Upload Analysis**
```bash
curl -X POST "http://localhost:8000/check-file" \
  -F "file=@requirements.txt"
```

### **2. GitHub Repository Analysis**
```bash
curl -X POST "http://localhost:8000/check-github" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repository",
    "branch": "main"
  }'
```

### **3. Text Content Analysis**
```bash
curl -X POST "http://localhost:8000/check-text" \
  -F "content=requests==2.25.1\nflask==1.1.4" \
  -F "file_type=requirements.txt"
```

### **4. Via Next.js Proxy (Frontend)**
```javascript
// Check dependencies via proxy (avoids CORS issues)
const response = await fetch('/api/dependency-health/check-github', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    repo_url: 'https://github.com/username/repo'
  })
});

const result = await response.json();
```

## 📊 Response Format

All API endpoints return a consistent JSON format:

**Success Response:**
```json
{
  "success": true,
  "data": {
    "total_dependencies": 5,
    "vulnerable_dependencies": 2,
    "vulnerabilities_found": 8,
    "risk_summary": {
      "CRITICAL": 0,
      "HIGH": 1,
      "MEDIUM": 3,
      "LOW": 4,
      "UNKNOWN": 0
    },
    "dependency_risk_summary": {
      "HIGH": ["requests"],
      "MEDIUM": ["flask", "django"],
      "LOW": ["numpy", "pandas"]
    },
    "dependency_risk_details": {
      "HIGH": [
        {
          "dependency": "requests",
          "version": "2.25.1",
          "vulnerabilities": ["CVE-2023-32681"],
          "risk_level": "HIGH"
        }
      ]
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
            "description": "Requests library vulnerability description...",
            "severity": "HIGH",
            "published_date": "2023-05-26T18:15:00",
            "affected_versions": ["<2.31.0"],
            "fixed_versions": ["2.31.0"]
          }
        ],
        "is_vulnerable": true,
        "risk_level": "HIGH"
      }
    ],
    "scan_timestamp": "2025-06-14T10:30:00"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Repository not found",
  "details": "The specified GitHub repository could not be accessed"
}
```

## 🔍 Supported File Formats

### **requirements.txt** (Python)
```txt
requests==2.25.1
flask>=1.1.0
django~=3.2.0
numpy
pandas>=1.0.0,<2.0.0
```

### **package.json** (Node.js)
```json
{
  "dependencies": {
    "express": "^4.17.1",
    "lodash": "~4.17.19",
    "axios": ">=0.21.0"
  },
  "devDependencies": {
    "jest": "^26.6.0"
  }
}
```

## 🚀 Deployment

### **Render Deployment**

1. **Deploy FastAPI Service:**
   - Push your code to GitHub
   - Create a new Web Service on Render
   - Connect your repository
   - Set build command: `pip install -r app/dependency-health/requirements.txt`
   - Set start command: `cd app/dependency-health && python main.py`

2. **Deploy Next.js Backend:**
   - Create another Web Service
   - Set build command: `cd backend && npm install && npm run build`
   - Set start command: `cd backend && npm start`
   - Add environment variable: `DEPENDENCY_HEALTH_URL=https://your-fastapi-service.onrender.com`

3. **Deploy Frontend:**
   - Use Render's Static Site service
   - Point to the `frontend` directory

### **Local Development Tips**
- Use `python main.py` to run the FastAPI service with auto-reload
- Use `npm run dev` for Next.js development server
- Check http://localhost:3000/api/status for service health
- Visit http://localhost:8000/docs for FastAPI documentation

## 🔒 Security Features

- **Input Validation**: All endpoints validate input data
- **File Upload Limits**: 5MB maximum file size
- **Rate Limiting**: Built-in protection against API abuse
- **CORS Configuration**: Configurable origins for security
- **Error Handling**: Sanitized error messages
- **Timeout Handling**: 30-second request timeouts

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`  
3. **Make your changes** and add tests if applicable
4. **Test thoroughly**: Run both FastAPI and Next.js services
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### **Development Setup**
```bash
# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests
cd app/dependency-health
python -m pytest tests/

# Check code formatting
black . --check
flake8 .
```

## 🐛 Troubleshooting

### **Common Issues**

**FastAPI Service Won't Start:**
- Check Python version (3.10+ required)
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use

**Next.js Backend Errors:**
- Ensure Node.js 18+ is installed
- Run `npm install` in the backend directory
- Check environment variables are set correctly

**CORS Errors in Frontend:**
- Use the Next.js proxy endpoints instead of direct FastAPI calls
- Ensure the backend is running on port 3000
- Check CORS settings in `app/dependency-health/main.py`

**GitHub Repository Analysis Fails:**
- Verify the repository URL is correct and public
- Check if the repository contains dependency files
- Ensure network connectivity to GitHub API

## 📈 Performance

- **Concurrent Processing**: Async vulnerability checking for multiple dependencies
- **Connection Pooling**: Efficient HTTP client with connection reuse
- **Rate Limiting**: Respects NVD API rate limits
- **Caching**: Can be extended with Redis for repeated queries
- **Timeout Handling**: 30-second timeouts prevent hanging requests

## � License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **API Documentation**: Visit http://localhost:8000/docs when running locally
- 🐛 **Bug Reports**: Create an issue on GitHub
- 💬 **Questions**: Contact the development team
- 📧 **Security Issues**: Report privately via email

---

## 🎉 LabLab.ai Hackathon Ready!

This project demonstrates:
- **Modern Architecture**: Microservices with API gateway pattern
- **Security Focus**: Real-world vulnerability scanning capabilities  
- **Production Ready**: Comprehensive error handling and monitoring
- **Developer Friendly**: Excellent documentation and easy setup
- **Scalable Design**: Ready for additional AI-powered services

Perfect for hackathons, portfolio projects, and production deployment!

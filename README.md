# 🚀 LabLab.ai Hackathon Project

A comprehensive AI-powered toolkit for developers, featuring dependency vulnerability scanning, automated test generation, and AI-powered pull request reviews.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React         │    │   Next.js        │    │   FastAPI       │
│   Frontend      │───▶│   Backend        │───▶│   Services      │
│   (Port 3001)   │    │   (Port 3000)    │    │   (8000-8002)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Services

### ✅ **Dependency Health Checker** (Port 8000)
- 🛡️ **Vulnerability Scanning**: Check Python and Node.js dependencies
- 📁 **File Upload**: Support for `requirements.txt` and `package.json`
- 🐙 **GitHub Integration**: Analyze repositories directly
- 📊 **Risk Assessment**: Categorize vulnerabilities by severity
- 🔗 **NVD Integration**: Real-time vulnerability data

### ⏳ **Auto Test Generator** (Port 8001)
- 🧪 **Test Generation**: Automatic unit test creation
- 🐍 **Multi-Language**: Python, JavaScript, TypeScript support
- 📋 **Test Types**: Unit, integration, and E2E tests

### ⏳ **PR Review Assistant** (Port 8002)  
- 📋 **Code Review**: AI-powered pull request analysis
- 🔍 **Security Scan**: Identify security vulnerabilities
- ⚡ **Performance**: Performance optimization suggestions

## 🚀 Quick Start

### **Local Development**

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd lablab.ai
```

2. **Start Dependency Health Service**
```bash
cd app/dependency-health
setup.bat
start.bat
```

3. **Start Next.js Backend**
```bash
cd backend
npm install
npm run dev
```

4. **Visit the applications:**
- Backend Dashboard: http://localhost:3000
- FastAPI Docs: http://localhost:8000/docs
- API Status: http://localhost:3000/api/status

### **Render Deployment** 

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed deployment instructions.

**Quick Deploy:**
1. Push to public GitHub repository
2. Deploy FastAPI service on Render
3. Deploy Next.js backend on Render  
4. Update environment variables
5. Deploy React frontend

## 📡 API Endpoints

### **System Status**
- `GET /api/status` - Check all services health

### **Dependency Health**
- `POST /api/dependency-health/check-file` - Upload dependency files
- `POST /api/dependency-health/check-github` - Analyze GitHub repos
- `POST /api/dependency-health/check-text` - Analyze text content

### **Auto Tests** (Coming Soon)
- `POST /api/auto-tests/generate` - Generate test cases

### **PR Review** (Coming Soon)
- `POST /api/pr-review/review` - Review pull requests

## 🛠️ Tech Stack

**Backend:**
- **Next.js 15** - API backend and service integration
- **FastAPI** - High-performance Python services
- **TypeScript** - Type-safe backend development

**Services:**
- **NVD API** - Vulnerability database
- **GitHub API** - Repository integration
- **HTTPX** - Async HTTP client

**Deployment:**
- **Render** - Cloud hosting platform
- **Docker** - Containerization (optional)

## 📁 Project Structure

```
lablab.ai/
├── app/                          # FastAPI Services
│   ├── dependency-health/        # ✅ Vulnerability scanner
│   ├── auto-tests/              # ⏳ Test generator  
│   └── pr-review/               # ⏳ PR reviewer
├── backend/                     # ✅ Next.js API backend
│   ├── src/app/api/            # API routes
│   └── package.json
├── frontend/                    # React frontend
└── RENDER_DEPLOYMENT.md        # Deployment guide
```

## 🔧 Configuration

### **Environment Variables**

**Local Development:**
```env
DEPENDENCY_HEALTH_URL=http://localhost:8000
AUTO_TESTS_URL=http://localhost:8001
PR_REVIEW_URL=http://localhost:8002
```

**Production (Render):**
```env
DEPENDENCY_HEALTH_URL=https://your-service.onrender.com
AUTO_TESTS_URL=https://your-auto-tests.onrender.com
PR_REVIEW_URL=https://your-pr-review.onrender.com
```

## 🎯 Features

### **✅ Working Features**
- ✅ Dependency vulnerability scanning
- ✅ File upload support (requirements.txt, package.json)
- ✅ GitHub repository analysis  
- ✅ Risk assessment and categorization
- ✅ RESTful API with OpenAPI docs
- ✅ CORS support for frontend integration
- ✅ Comprehensive error handling
- ✅ Health monitoring

### **⏳ Coming Soon**
- ⏳ Automated test case generation
- ⏳ AI-powered pull request reviews
- ⏳ Frontend React application
- ⏳ Real-time notifications
- ⏳ Dashboard analytics

## 📊 Example Response

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
      "LOW": 4
    },
    "results": [...]
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details

## 🆘 Support

- 📖 Check API documentation at `/docs`
- 🐛 Report issues on GitHub
- 💬 Contact the team for questions

---

**🎉 Ready for LabLab.ai Hackathon!**

This project demonstrates modern microservices architecture with AI-powered tools for developers. Perfect for hackathons, portfolios, and production use.

# 🚀 **StackHub - AI-Powered Code Intelligence Platform** | LabLab.ai Hackathon 2025

> **Revolutionizing Developer Workflows with AI** 🤖✨

StackHub is a comprehensive AI-powered code intelligence platform that transforms how developers work - from dependency security analysis to intelligent code reviews. Built for the **LabLab.ai Hackathon 2025** to showcase the future of AI-assisted development.

## 🌟 **Live Demo**
🎯 **StackHub Dashboard**: https://stackhub-dashboard.onrender.com

## 🎯 **Core Features**

### 🛡️ **Dependency Health Monitor** - ✅ LIVE
> *"Your AI security analyst that never sleeps"*

- 🔍 **Smart Vulnerability Detection**: Scans Python & Node.js dependencies with AI-enhanced analysis
- 🐙 **GitHub Repository Analysis**: Analyzes entire repositories instantly  
- 📊 **Risk Intelligence**: AI-powered severity assessment and remediation suggestions
- 🛡️ **Real-time Protection**: Connects to National Vulnerability Database
- 🤖 **Interactive Dashboard**: Modern, responsive UI with real-time results

### 📋 **AI PR Reviews** - ✅ LIVE  
> *"Intelligent code reviews powered by advanced AI"*

- 🤖 **Smart Code Analysis**: AI-powered pull request reviews
- 📝 **Detailed Feedback**: Comprehensive suggestions for code improvement
- 🔍 **Pattern Recognition**: Identifies potential issues and best practices
- ⚡ **Instant Results**: Fast, accurate analysis of code changes



## 🚀 **StackHub Architecture**

```
┌──────────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
│   🌐 StackHub UI      │    │   🔄 Backend Hub    │    │   🤖 AI Services     │
│   Modern Dashboard    │───▶│   Next.js API      │───▶│   FastAPI Engines    │
│   (Render Static)     │    │   (Render Service)  │    │   (Render Services)  │
└──────────────────────┘    └─────────────────────┘    └──────────────────────┘
                                      │
                                      ▼
                   ┌─────────────────────────────────────────────┐
                   │   🌍 External APIs & Services               │
                   │   NVD • GitHub • OpenRouter • Databases    │
                   └─────────────────────────────────────────────┘
```

## 🌐 **Live Services**

- 🎯 **StackHub Dashboard**: https://stackhub-dashboard.onrender.com
- 🛡️ **Dependency Health API**: https://dependency-health.onrender.com
- 🔄 **Backend Hub**: https://stackhub-backend.onrender.com
- 📋 **PR Review Bot**: [GitHub Integration Active]


### **🚀 Manual Setup (Current)**

**1. Activate the Dependency Health Guardian**
```bash
cd app/dependency-health

# Create AI environment
python -m venv ai-env
ai-env\Scripts\activate  # Windows
# source ai-env/bin/activate  # Linux/Mac

# Install AI powers
pip install -r requirements.txt

# Launch the guardian
python main.py
```

**2. Boot the AI Orchestrator**
```bash
cd backend
npm install
npm run dev
```

**3. Access Your AI Dashboard**
- 🎯 **AI Hub**: http://localhost:3000
- 🛡️ **Security AI**: http://localhost:8000/docs
- 📊 **System Status**: http://localhost:3000/api/status
- 🌐 **Frontend**: Open `frontend/index.html`

## 🔮 **StackHub API Endpoints**

### **🤖 System Status**
- `GET /api/status` - System health & service status

### **🛡️ Dependency Health API**
- `POST /api/dependency-health/check-file` - Upload and analyze dependency files
- `POST /api/dependency-health/check-github` - Analyze GitHub repositories
- `POST /api/dependency-health/check-text` - Analyze dependency text
- `GET /api/dependency-health/health` - Service health check

### **📋 PR Review API**  
- `POST /api/pr-review/review` - AI-powered pull request analysis
- `GET /api/pr-review/health` - PR review service status

### **🕷️ GitHub Webhooks**
- `POST /api/webhooks/github` - GitHub integration endpoint

## 🛠️ **Next-Gen Tech Stack**

**🤖 AI Services Layer:**
- **FastAPI** - Lightning-fast AI service framework
- **HTTPX** - Async AI communication

**🔄 Orchestration Layer:**
- **Next.js 15** - AI service orchestrator
- **TypeScript** - Type-safe AI interactions
- **React** - Dynamic AI interfaces

**🌐 Intelligence Layer:**
- **NVD API** - Vulnerability intelligence
- **GitHub API** - Code repository analysis

**☁️ Cloud Infrastructure:**
- **Render** - Scalable cloud deployment

## 📁 **StackHub Project Structure**

```
stackhub/                           # 🚀 StackHub Root
├── app/                           # 🤖 AI Services
│   ├── dependency-health/         # 🛡️ Security Analysis (LIVE)
│   │   ├── main.py               # FastAPI security engine
│   │   ├── utils.py              # Analysis utilities
│   │   └── requirements.txt      # Service dependencies
│   ├── pr-review/                # 📋 PR Review AI (LIVE)
│   │   ├── main.py              # Code review engine
│   │   └── AI prompts & logic   # Review intelligence
│   └── auto-tests/               # 🧪 Test Generation (DEV)
│       └── main.py              # Test generation engine
├── backend/                      # 🔄 API Hub
│   ├── src/app/api/             # Unified API endpoints
│   │   ├── status/              # System status
│   │   ├── dependency-health/   # Security API proxy
│   │   ├── pr-review/           # Review API proxy
│   │   └── webhooks/            # GitHub integration
│   └── convex/                  # Database layer
├── frontend/                    # 🌐 StackHub Dashboard
│   ├── dashboard.html          # Main dashboard interface
│   ├── index.html             # Landing page
│   └── render.yaml            # Deployment config
└── docs/                       # 📚 Documentation
    ├── README.md              # This file
    └── deployment guides      # Setup instructions
```




### **🛡️ Security in Action**
```bash
# Instant vulnerability detection
curl -X POST "http://localhost:8000/check-github" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/vulnerable-project/example",
    "ai_enhanced": true,
    "deep_analysis": true
  }'
```


**Smart Success Response:**
```json
{
  "success": true,
  "ai_confidence": 0.98,
  "processing_time_ms": 1247,
  "data": {
    "total_dependencies": 15,
    "ai_risk_score": 7.3,
    "vulnerabilities_found": 3,
    "ai_recommendations": [
      {
        "priority": "HIGH",
        "action": "Update requests to 2.31.0",
        "ai_reasoning": "Critical security vulnerability detected",
        "confidence": 0.96
      }
    ],
    "risk_summary": {
      "CRITICAL": 0,
      "HIGH": 1,
      "MEDIUM": 2,
      "LOW": 0
    },
    "ai_insights": {
      "security_trend": "improving",
      "recommendation_impact": "high",
      "false_positive_likelihood": 0.02
    }
  }
}
```


## 🏆 **LabLab.ai Hackathon Features**

### **✅ LIVE & READY**
- 🛡️ **AI Security Scanner**: Real-time vulnerability detection
- 🔍 **Smart Analysis**: GitHub repository intelligence
- 📊 **Risk AI**: Intelligent vulnerability assessment
- 🚀 **Performance**: Sub-second AI responses
- 🌐 **Web Interface**: Intuitive AI dashboard
- 📡 **API Gateway**: Unified AI service access


---

*Built with ❤️ and 🤖 for TraeIDE Limitless Hackathon 2025*
*Let's make development limitless!* 🚀✨

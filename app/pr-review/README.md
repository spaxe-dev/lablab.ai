# 🤖 AI PR Review Bot

A GitHub App that analyzes Pull Requests and provides intelligent feedback through AI-powered code review and automated GitHub comments.

## ✨ Features

- 🔍 **Automated PR Analysis**: Analyzes Python, JavaScript, TypeScript, and other code files
- 🛡️ **Security Scanning**: Detects potential security vulnerabilities and hardcoded credentials
- 📊 **Code Quality Assessment**: Provides style suggestions and best practice recommendations
- 🤖 **AI-Enhanced Reviews**: Powered by OpenRouter's Deepseek R1 LLM for intelligent insights
- 📝 **GitHub Comments**: Detailed review comments posted directly to PRs
- 🔧 **GitHub App**: Install on any repository, no personal tokens required
- 📋 **Review History**: Track all PR reviews and their outcomes

## 🚀 Quick Start

### **Local Development**

1. **Install Dependencies**
```bash
cd app/pr-review
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
# GitHub App Configuration (Required)
export GITHUB_APP_ID=your_github_app_id
export GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
export GITHUB_WEBHOOK_SECRET=your_webhook_secret

# AI Enhancement (Recommended)
export OPENROUTER_API_KEY=your_openrouter_api_key

# Optional
export DATABASE_URL=sqlite:///./pr_review.db
```

3. **Run the Service**
```bash
python main.py
```

The service will be available at http://localhost:8002

### **Render Deployment**

1. **Create a new Web Service** on Render
2. **Connect your repository**
3. **Set the following:**
   - Build Command: `pip install -r app/pr-review/requirements.txt`
   - Start Command: `cd app/pr-review && python main.py`
4. **Add Environment Variables:**
   - `GITHUB_APP_ID`: Your GitHub App ID
   - `GITHUB_APP_PRIVATE_KEY`: Your GitHub App private key (PEM format)  
   - `GITHUB_WEBHOOK_SECRET`: Your webhook secret
   - `OPENROUTER_API_KEY`: Your OpenRouter API key for AI analysis
   - `DATABASE_URL`: PostgreSQL database URL (Render provides this)

## 🔧 Configuration

### **GitHub App Setup**

1. **Create a GitHub App:**
   - Go to GitHub Settings → Developer settings → GitHub Apps
   - Click "New GitHub App"
   - Set the following:
     - **App name**: `AI PR Review Bot` (or your preferred name)
     - **Homepage URL**: `https://your-service.onrender.com`
     - **Webhook URL**: `https://your-service.onrender.com/webhook`
     - **Webhook secret**: Generate a secure secret
     - **Permissions**: 
       - Repository permissions: Pull requests (Read & write), Contents (Read), Metadata (Read)
     - **Events**: Subscribe to "Pull requests"

2. **Install the App:**
   - After creating the app, install it on your repositories
   - The app will automatically receive webhooks for PR events

3. **Configure Environment Variables:**
   - `GITHUB_APP_ID`: Found in your app's settings
   - `GITHUB_APP_PRIVATE_KEY`: Generate and download from app settings
   - `GITHUB_WEBHOOK_SECRET`: The secret you set in step 1

### **OpenRouter Setup (AI Enhancement)**

1. **Get OpenRouter API Key:**
   - Go to [OpenRouter.ai](https://openrouter.ai)
   - Sign up and get your API key
   - Set as `OPENROUTER_API_KEY` environment variable

2. **AI Model Configuration:**
   - Currently using: `deepseek/deepseek-r1-0528:free`
   - This provides intelligent code analysis beyond rule-based checks
   - Free model with good performance for code review tasks

## 📡 API Endpoints

### **Repository Management**
### **Review History**
- `GET /api/reviews` - Get recent PR reviews

### **Webhooks**
- `POST /webhook` - GitHub webhook endpoint

### **Health Check**
- `GET /health` - Service health status

## 🎯 How It Works

1. **App Installation**: Install the GitHub App on your repositories
2. **PR Events**: GitHub automatically sends webhooks when PRs are created/updated
3. **AI Analysis**: Service analyzes changed files using:
   - Rule-based security and quality checks
   - OpenRouter's Deepseek R1 LLM for intelligent insights
   - Pattern matching for vulnerabilities and best practices
4. **GitHub Comments**: Detailed review posted as PR comment
5. **History**: Review stored in database for tracking

## 🔍 Analysis Features

### **Security Checks**
- Hardcoded credentials detection
- SQL injection vulnerability patterns
- Dangerous function usage (eval, exec)
- File permission issues

### **AI-Enhanced Analysis**
- Context-aware code review
- Logic and architectural suggestions
- Best practice recommendations
- Intelligent issue prioritization

### **Code Quality**
- TODO/FIXME comment detection
- Debug statement identification
- Large file warnings
- Import style suggestions

### **Language-Specific Analysis**

**Python:**
- Wildcard import detection
- Exception handling best practices
- PEP 8 style suggestions

**JavaScript/TypeScript:**
- var vs let/const recommendations
- Strict equality suggestions
- Modern syntax recommendations

## 📊 Dashboard Features

### **Review History**
- Recent PR review results
- Security scores and issue counts
- AI-powered insights and recommendations
- Direct links to reviewed PRs

## 🔒 Security

- GitHub App authentication with installation tokens
- Webhook signature verification
- Environment variable configuration
- Database query parameterization
- Input validation and sanitization

## 🚀 Next.js Integration

This service integrates with the Next.js backend through proxy endpoints:
- `/api/pr-review/reviews` - Review history
- `/api/pr-review/health` - Health check

## 📝 Example Workflow

1. Install GitHub App on repository
2. Developer opens PR
3. GitHub automatically sends webhook
4. Service performs AI-enhanced analysis
5. Detailed review comment posted to PR
6. Review stored in database with scoring
7. Team can view history in dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

---

*🚀 Built for LabLab.ai Hackathon 2025 - Making code reviews intelligent and automated with AI!*

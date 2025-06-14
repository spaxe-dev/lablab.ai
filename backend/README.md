# LabLab.ai Hackathon - Next.js Backend

A Next.js API backend that connects all AI tool applications to the frontend, providing a unified interface for the hackathon project.

## 🎯 Purpose

This backend serves as the **integration layer** between:
- **Frontend**: React application for user interface
- **AI Services**: FastAPI applications (dependency-health, auto-tests, pr-review)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React         │    │   Next.js        │    │   FastAPI       │
│   Frontend      │───▶│   Backend        │───▶│   Services      │
│   (Port 3001)   │    │   (Port 3000)    │    │   (8000-8002)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📡 API Endpoints

### System Status
- `GET /api/status` - Check all services health and get endpoint overview

### 🛡️ Dependency Health Service (Port 8000)
- `POST /api/dependency-health/check-file` - Upload dependency files
- `POST /api/dependency-health/check-github` - Analyze GitHub repositories  
- `POST /api/dependency-health/check-text` - Analyze text content
- `GET /api/dependency-health/health` - Service health check

### 🧪 Auto Tests Service (Port 8001) 
- `POST /api/auto-tests/generate` - Generate test cases
- `GET /api/auto-tests/health` - Service health check

### 📋 PR Review Service (Port 8002)
- `POST /api/pr-review/review` - Review pull requests
- `GET /api/pr-review/health` - Service health check

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The backend will be available at: **http://localhost:3000**

### 3. Check API Status
Visit: **http://localhost:3000/api/status**

## 📋 Response Format

All API endpoints return a consistent format:

```json
{
  "success": true,
  "data": {
    // Service-specific response data
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information"
}
```

## 🔧 Configuration

Service URLs are configured in `/src/app/api/config.ts`:

```typescript
export const API_CONFIG = {
  services: {
    dependencyHealth: {
      baseUrl: 'http://localhost:8000',
      name: 'dependency-health'
    },
    autoTests: {
      baseUrl: 'http://localhost:8001', 
      name: 'auto-tests'
    },
    prReview: {
      baseUrl: 'http://localhost:8002',
      name: 'pr-review'
    }
  }
};
```

## 🌐 Frontend Integration

### React Frontend Usage Example:

```javascript
// Check dependency vulnerabilities
const checkDependencies = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/dependency-health/check-file', {
    method: 'POST',
    body: formData,
  });

  const result = await response.json();
  return result;
};

// Check all services status
const checkSystemStatus = async () => {
  const response = await fetch('/api/status');
  const status = await response.json();
  return status;
};
```

## 📊 Service Monitoring

The backend automatically monitors all connected services and provides:

- **Health checks** for each service
- **Service availability** status  
- **Error handling** and fallbacks
- **Timeout management** (30 seconds default)

## 🛠️ Development

### Project Structure

```
backend/
├── src/app/
│   ├── api/
│   │   ├── dependency-health/
│   │   │   ├── check-file/route.ts
│   │   │   ├── check-github/route.ts
│   │   │   ├── check-text/route.ts
│   │   │   └── health/route.ts
│   │   ├── auto-tests/
│   │   │   ├── generate/route.ts
│   │   │   └── health/route.ts
│   │   ├── pr-review/
│   │   │   ├── review/route.ts
│   │   │   └── health/route.ts
│   │   ├── config.ts
│   │   └── status/route.ts
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── package.json
└── README.md
```

### Adding New Services

1. Create new directory in `/src/app/api/`
2. Add service configuration to `config.ts`
3. Create route handlers following the existing pattern
4. Update the status endpoint to include the new service

## 🔒 Error Handling

All routes include comprehensive error handling:

- **Service availability checks**
- **Request validation**
- **Timeout handling**
- **Detailed error messages**
- **Graceful fallbacks**

## 🎯 Integration Status

- ✅ **Dependency Health**: Fully integrated and tested
- ⏳ **Auto Tests**: Routes ready, waiting for service implementation
- ⏳ **PR Review**: Routes ready, waiting for service implementation

## 📝 Notes

- Each service runs on a different port (8000, 8001, 8002)
- The backend handles CORS and request forwarding
- All responses are normalized for consistent frontend consumption
- Services are designed to be independent and scalable

---

**Ready to connect with your React frontend!** 🎉

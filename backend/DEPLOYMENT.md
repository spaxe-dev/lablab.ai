# Next.js Backend Deployment Guide

## 🚀 Deploy Next.js Backend to Render

### **Step 1: Create a New Web Service on Render**

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `spaxe-dev/lablab.ai`
4. Configure the service:

### **Step 2: Service Configuration**

```
Name: lablab-backend
Environment: Node
Region: Oregon (US West)
Branch: main
Root Directory: backend
Build Command: ./build.sh
Start Command: npm start
```

### **Step 3: Environment Variables**

Add these environment variables in Render dashboard:

```
DEPENDENCY_HEALTH_URL=https://dependency-health.onrender.com
AUTO_TESTS_URL=https://your-auto-tests-service.onrender.com
PR_REVIEW_URL=https://your-pr-review-service.onrender.com
NODE_ENV=production
```

### **Step 4: Deployment Process**

1. **Make build.sh executable** (Render will do this automatically)
2. **Deploy**: Render will automatically:
   - Run `npm ci` to install dependencies
   - Run `npm run build` to build the Next.js app
   - Start the service with `npm start`

### **Step 5: Test Your Deployed Backend**

Once deployed, your backend will be available at:
`https://your-backend-name.onrender.com`

**Test endpoints:**
- `GET /api/status` - System status
- `GET /` - Dashboard page
- `POST /api/dependency-health/check-github` - Proxy to FastAPI service

### **Step 6: Update Frontend (if needed)**

Update your frontend configuration to point to the deployed backend:
```javascript
const BACKEND_URL = 'https://your-backend-name.onrender.com';
```

## 🔧 **Current Service URLs**

- **FastAPI (Dependency Health)**: https://dependency-health.onrender.com
- **Next.js Backend**: Will be your new service URL
- **Frontend**: To be deployed separately

## 🎯 **Expected Result**

Your Next.js backend will act as an API gateway, providing:
- Unified API endpoints for all AI services
- CORS handling for frontend access
- Service health monitoring
- Error handling and retries

## 🐞 **Troubleshooting**

**Build fails?**
- Check that `build.sh` has executable permissions
- Verify all dependencies are in `package.json`

**Runtime errors?**
- Check environment variables are set correctly
- Verify service URLs are accessible
- Check Render logs for detailed error messages

**CORS issues?**
- Ensure Next.js API routes include proper CORS headers
- Check that frontend origin is allowed

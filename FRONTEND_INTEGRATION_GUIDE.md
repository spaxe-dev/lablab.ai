# Frontend Integration Guide - Dependency Health Checker

## 🎯 Overview
This guide helps frontend developers integrate and display the Dependency Health Checker API results in a beautiful, user-friendly interface.

## 🔗 API Endpoints

### Base URL
- **Production**: `https://lablab-ai-backend.onrender.com`

*Note: All requests should go through the backend API gateway. Direct FastAPI access is not needed for frontend integration.*

### Available Endpoints

#### 1. Health Check
```
GET /api/dependency-health/health
```
**Response:**
```json
{
  "success": true,
  "service": "dependency-health",
  "status": "healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2025-06-14T08:00:00Z"
  }
}
```

#### 2. GitHub Repository Analysis
```
POST /api/dependency-health/check-github
Content-Type: application/json

{
  "github_url": "https://github.com/owner/repo"
}
```

#### 3. File Upload Analysis
```
POST /api/dependency-health/check-file
Content-Type: multipart/form-data

FormData with file: requirements.txt or package.json
```

## 📊 API Response Structure

### Success Response Format
```json
{
  "total_dependencies": 9,
  "vulnerable_dependencies": 9,
  "vulnerabilities_found": 61,
  "risk_summary": {
    "CRITICAL": 2,
    "HIGH": 0,
    "MEDIUM": 7,
    "LOW": 0,
    "UNKNOWN": 0
  },
  "dependency_risk_summary": {
    "CRITICAL": ["pipreqs", "PyYAML"],
    "HIGH": [],
    "MEDIUM": ["PyJWT", "Flask", "urllib3", "pydantic", "tensorflow", "numpy", "requests"],
    "LOW": [],
    "UNKNOWN": [],
    "NONE": []
  },
  "dependency_risk_details": {
    "CRITICAL": [
      {
        "name": "pipreqs",
        "version": "0.4.11",
        "risk_level": "CRITICAL",
        "vulnerability_count": 1,
        "critical_cves": ["CVE-2023-31543"],
        "high_cves": [],
        "medium_cves": [],
        "low_cves": []
      }
    ]
  },
  "results": [
    {
      "dependency": {
        "name": "PyJWT",
        "version": "2.4.0",
        "type": "python"
      },
      "vulnerabilities": [
        {
          "cve_id": "CVE-2017-11424",
          "description": "Vulnerability description...",
          "severity": "MEDIUM",
          "published_date": "2017-08-24T16:29:00.197",
          "affected_versions": [],
          "fixed_versions": []
        }
      ],
      "is_vulnerable": true,
      "risk_level": "MEDIUM"
    }
  ],
  "scan_timestamp": "2025-06-14T08:00:00Z"
}
```

## 🎨 UI Design Recommendations

### 1. Summary Dashboard
Create a dashboard showing:
```javascript
// Example data extraction
const { 
  total_dependencies, 
  vulnerable_dependencies, 
  vulnerabilities_found, 
  risk_summary 
} = response;

// Key metrics to display
const metrics = {
  totalDeps: total_dependencies,
  vulnerableDeps: vulnerable_dependencies,
  totalVulns: vulnerabilities_found,
  criticalCount: risk_summary.CRITICAL,
  highCount: risk_summary.HIGH,
  mediumCount: risk_summary.MEDIUM,
  lowCount: risk_summary.LOW
};
```

**Visual Elements:**
- 📊 **Progress bars** for vulnerability distribution
- 🔴 **Color-coded risk levels** (Critical=Red, High=Orange, Medium=Yellow, Low=Green)
- 📈 **Charts/graphs** for risk breakdown
- ⚡ **Quick stats cards** with large numbers

### 2. Risk Level Color Scheme
```css
.risk-critical { 
  background: linear-gradient(135deg, #ff4757, #c44569);
  color: white;
}
.risk-high { 
  background: linear-gradient(135deg, #ff6348, #ff4757);
  color: white;
}
.risk-medium { 
  background: linear-gradient(135deg, #ffa502, #ff6348);
  color: white;
}
.risk-low { 
  background: linear-gradient(135deg, #7bed9f, #2ed573);
  color: white;
}
.risk-none { 
  background: linear-gradient(135deg, #70a1ff, #5352ed);
  color: white;
}
```

### 3. Dependency List Layout
```javascript
// Group dependencies by risk level
const groupedDeps = {
  CRITICAL: dependency_risk_details.CRITICAL || [],
  HIGH: dependency_risk_details.HIGH || [],
  MEDIUM: dependency_risk_details.MEDIUM || [],
  LOW: dependency_risk_details.LOW || [],
  NONE: dependency_risk_details.NONE || []
};

// Display structure for each dependency
const dependencyCard = {
  name: "package-name",
  version: "1.0.0",
  riskLevel: "CRITICAL",
  vulnerabilityCount: 3,
  cveIds: ["CVE-2023-1234", "CVE-2023-5678"],
  description: "Brief vulnerability summary"
};
```

### 4. Vulnerability Details Modal
For each CVE, show:
```javascript
const vulnerabilityDetail = {
  cveId: "CVE-2023-1234",
  severity: "CRITICAL",
  description: "Full description...",
  publishedDate: "2023-01-01",
  affectedVersions: ["1.0.0", "1.1.0"],
  fixedVersions: ["1.2.0+"]
};
```

## 🛠️ Implementation Examples

### React Component Structure
```jsx
function DependencyHealthDashboard({ data }) {
  return (
    <div className="dependency-dashboard">
      <SummaryCards metrics={data.risk_summary} />
      <RiskChart data={data.risk_summary} />
      <DependencyList 
        dependencies={data.dependency_risk_details}
        vulnerabilities={data.results}
      />
    </div>
  );
}

function SummaryCards({ metrics }) {
  return (
    <div className="metrics-grid">
      <MetricCard 
        title="Total Dependencies" 
        value={metrics.total_dependencies}
        icon="📦"
      />
      <MetricCard 
        title="Vulnerable" 
        value={metrics.vulnerable_dependencies}
        icon="🚨"
        color="risk-critical"
      />
      <MetricCard 
        title="Critical Issues" 
        value={metrics.CRITICAL}
        icon="🔴"
        color="risk-critical"
      />
    </div>
  );
}
```

### API Integration
```javascript
// Fetch and display results
async function analyzeDependencies(githubUrl) {
  try {
    const response = await fetch('/api/dependency-health/check-github', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ github_url: githubUrl })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      displayResults(data);
    } else {
      showError(data.error);
    }
  } catch (error) {
    showError('Network error: ' + error.message);
  }
}

function displayResults(data) {
  // Update summary dashboard
  updateSummaryCards(data.risk_summary);
  
  // Render dependency list
  renderDependencyList(data.dependency_risk_details);
  
  // Show vulnerability details
  renderVulnerabilityTable(data.results);
}
```

### File Upload Handler
```javascript
function handleFileUpload(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  fetch('/api/dependency-health/check-file', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => displayResults(data))
  .catch(error => showError(error));
}
```

## 🎨 UI Components to Build

### 1. **Input Section**
- GitHub URL input field
- File upload dropzone
- Analyze button with loading state

### 2. **Summary Dashboard**
- Total dependencies count
- Vulnerable dependencies count
- Risk level breakdown (pie chart or bar chart)
- Overall security score

### 3. **Dependency Grid/List**
- Filterable by risk level
- Sortable by name, risk, vulnerability count
- Search functionality
- Expandable cards showing CVE details

### 4. **Vulnerability Details**
- Modal or side panel for CVE information
- Links to official CVE databases
- Severity indicators
- Affected/fixed version information

### 5. **Export/Share Features**
- Download report as PDF
- Share results via link
- Export to JSON/CSV

## 🎯 User Experience Tips

1. **Progressive Disclosure**: Show summary first, details on demand
2. **Loading States**: Display progress during analysis
3. **Empty States**: Handle repositories with no vulnerabilities gracefully
4. **Error Handling**: Clear error messages for invalid URLs/files
5. **Responsive Design**: Works on mobile and desktop
6. **Accessibility**: Proper ARIA labels and keyboard navigation

## 🔧 Testing URLs

Use these for testing your UI:
- **Vulnerable repo**: `https://github.com/spaxe-dev/checks`
- **Clean repo**: `https://github.com/facebook/react`
- **Invalid repo**: `https://github.com/nonexistent/repo`

## 📱 Mobile Considerations

- Stack cards vertically on small screens
- Use collapsible sections for vulnerability details
- Implement swipe gestures for navigation
- Ensure touch-friendly button sizes

This structure provides everything a frontend developer needs to create a beautiful, functional interface for the dependency health checker! 🚀

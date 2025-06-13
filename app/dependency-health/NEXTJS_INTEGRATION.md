# Integration Example for Next.js Backend

This document shows how to integrate the Dependency Health Monitor API with your Next.js backend.

## Next.js API Route Example

Create a file in your Next.js project at `pages/api/scan-dependencies.js` (or `app/api/scan-dependencies/route.js` for App Router):

### Pages Router Example

```javascript
// pages/api/scan-dependencies.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { requirements } = req.body;

    if (!requirements) {
      return res.status(400).json({ error: 'Requirements content is required' });
    }

    // Call the Dependency Health Monitor API
    const response = await fetch('http://localhost:5000/api/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        requirements_content: requirements
      })
    });

    if (!response.ok) {
      throw new Error(`API responded with status ${response.status}`);
    }

    const data = await response.json();
    
    // Process and return the results
    res.status(200).json({
      success: true,
      data: {
        scanTimestamp: data.scan_timestamp,
        totalDependencies: data.total_dependencies,
        vulnerablePackages: data.severity_summary.vulnerable_packages,
        totalVulnerabilities: data.severity_summary.total_vulnerabilities,
        severityBreakdown: data.severity_summary,
        dependencies: data.dependencies,
        vulnerabilities: data.vulnerability_results
      }
    });
  } catch (error) {
    console.error('Error scanning dependencies:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to scan dependencies',
      details: error.message 
    });
  }
}
```

### App Router Example

```javascript
// app/api/scan-dependencies/route.js
import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { requirements } = await request.json();

    if (!requirements) {
      return NextResponse.json(
        { error: 'Requirements content is required' },
        { status: 400 }
      );
    }

    // Call the Dependency Health Monitor API
    const response = await fetch('http://localhost:5000/api/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        requirements_content: requirements
      })
    });

    if (!response.ok) {
      throw new Error(`API responded with status ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: {
        scanTimestamp: data.scan_timestamp,
        totalDependencies: data.total_dependencies,
        vulnerablePackages: data.severity_summary.vulnerable_packages,
        totalVulnerabilities: data.severity_summary.total_vulnerabilities,
        severityBreakdown: data.severity_summary,
        dependencies: data.dependencies,
        vulnerabilities: data.vulnerability_results
      }
    });
  } catch (error) {
    console.error('Error scanning dependencies:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to scan dependencies',
        details: error.message 
      },
      { status: 500 }
    );
  }
}
```

## Frontend Usage

### React Component Example

```jsx
// components/DependencyScanner.jsx
import { useState } from 'react';

export default function DependencyScanner() {
  const [requirements, setRequirements] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScan = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/scan-dependencies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requirements }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to scan dependencies');
      }

      setResults(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'text-red-600';
      case 'HIGH': return 'text-orange-600';
      case 'MEDIUM': return 'text-yellow-600';
      case 'LOW': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dependency Health Scanner</h1>
      
      <form onSubmit={handleScan} className="mb-8">
        <div className="mb-4">
          <label htmlFor="requirements" className="block text-sm font-medium mb-2">
            Requirements.txt Content
          </label>
          <textarea
            id="requirements"
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="flask==2.3.3&#10;requests==2.31.0&#10;django==4.2.0"
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Scanning...' : 'Scan Dependencies'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Scan Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {results.totalDependencies}
                </div>
                <div className="text-sm text-gray-600">Total Dependencies</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {results.vulnerablePackages}
                </div>
                <div className="text-sm text-gray-600">Vulnerable Packages</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {results.totalVulnerabilities}
                </div>
                <div className="text-sm text-gray-600">Total Vulnerabilities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {results.severityBreakdown.CRITICAL}
                </div>
                <div className="text-sm text-gray-600">Critical Issues</div>
              </div>
            </div>
          </div>

          {/* Severity Breakdown */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Severity Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(results.severityBreakdown).filter(([key]) => 
                ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].includes(key)
              ).map(([severity, count]) => (
                <div key={severity} className="text-center">
                  <div className={`text-xl font-bold ${getSeverityColor(severity)}`}>
                    {count}
                  </div>
                  <div className="text-sm text-gray-600">{severity}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Vulnerabilities */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Vulnerabilities</h3>
            <div className="space-y-4">
              {results.vulnerabilities.map((pkg, index) => (
                pkg.vulnerabilities.length > 0 && (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-lg mb-2">
                      📦 {pkg.package_name} ({pkg.package_version || 'any version'})
                    </h4>
                    <div className="text-sm text-gray-600 mb-3">
                      {pkg.vulnerabilities.length} vulnerabilities found
                    </div>
                    <div className="space-y-2">
                      {pkg.vulnerabilities.slice(0, 3).map((vuln, vIndex) => (
                        <div key={vIndex} className="border-l-4 border-gray-300 pl-4">
                          <div className="flex items-center gap-2">
                            <span className={`font-medium ${getSeverityColor(vuln.severity)}`}>
                              {vuln.severity}
                            </span>
                            <span className="font-mono text-sm">{vuln.cve_id}</span>
                            {vuln.cvss_score && (
                              <span className="text-sm text-gray-600">
                                CVSS: {vuln.cvss_score}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-700 mt-1">
                            {vuln.description.substring(0, 200)}...
                          </p>
                        </div>
                      ))}
                      {pkg.vulnerabilities.length > 3 && (
                        <div className="text-sm text-gray-500 italic">
                          ... and {pkg.vulnerabilities.length - 3} more vulnerabilities
                        </div>
                      )}
                    </div>
                  </div>
                )
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Configuration

### Environment Variables

Add these to your Next.js `.env.local` file:

```env
# Dependency Health Monitor API URL
DEPENDENCY_HEALTH_API_URL=http://localhost:5000

# Optional: NVD API Key for higher rate limits
NVD_API_KEY=your_nvd_api_key_here
```

### Updated API Route with Environment Variables

```javascript
// pages/api/scan-dependencies.js
const API_URL = process.env.DEPENDENCY_HEALTH_API_URL || 'http://localhost:5000';

export default async function handler(req, res) {
  // ... rest of the code
  
  const response = await fetch(`${API_URL}/api/scan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requirements_content: requirements
    })
  });
  
  // ... rest of the code
}
```

## Additional Endpoints

### Check Single Package

```javascript
// pages/api/check-package.js
export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { package: packageName, version } = req.query;

  if (!packageName) {
    return res.status(400).json({ error: 'Package name is required' });
  }

  try {
    const url = `${API_URL}/api/package/${packageName}${version ? `?version=${version}` : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`API responded with status ${response.status}`);
    }

    const data = await response.json();
    res.status(200).json({ success: true, data });
  } catch (error) {
    console.error('Error checking package:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to check package',
      details: error.message 
    });
  }
}
```

### Upload File

```javascript
// pages/api/upload-scan.js
import formidable from 'formidable';
import fs from 'fs';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const form = formidable({ multiples: false });
    const [fields, files] = await form.parse(req);
    
    const file = files.file[0];
    const fileContent = fs.readFileSync(file.filepath, 'utf8');

    const response = await fetch(`${API_URL}/api/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        requirements_content: fileContent
      })
    });

    if (!response.ok) {
      throw new Error(`API responded with status ${response.status}`);
    }

    const data = await response.json();
    res.status(200).json({ success: true, data });
  } catch (error) {
    console.error('Error uploading and scanning file:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to upload and scan file',
      details: error.message 
    });
  }
}
```

## Deployment Notes

1. **Development**: Run the Dependency Health Monitor on `localhost:5000`
2. **Production**: Deploy the Python API to a cloud service and update the API URL
3. **CORS**: The API already has CORS enabled for cross-origin requests
4. **Rate Limiting**: Consider implementing rate limiting on your Next.js API routes
5. **Caching**: Cache results to avoid redundant API calls for the same requirements

## Security Considerations

1. **API Key**: Store NVD API keys securely in environment variables
2. **Input Validation**: Validate requirements.txt content before processing
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Error Handling**: Don't expose sensitive error details to clients
5. **HTTPS**: Use HTTPS in production for secure communication

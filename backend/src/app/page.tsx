export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🚀 LabLab.ai Hackathon Backend
          </h1>
          <p className="text-xl text-gray-600">
            Next.js API Backend connecting all AI tools to the frontend
          </p>
        </header>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Dependency Health Service */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🛡️ Dependency Health
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Vulnerability scanning for Python and Node.js dependencies
            </p>
            <div className="space-y-2 text-sm">
              <div className="text-blue-600">Port: 8000</div>
              <div className="text-gray-500">Status: Ready</div>
            </div>
          </div>

          {/* Auto Tests Service */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🧪 Auto Tests
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Automatic test case generation for your code
            </p>
            <div className="space-y-2 text-sm">
              <div className="text-green-600">Port: 8001</div>
              <div className="text-gray-500">Status: Coming Soon</div>
            </div>
          </div>

          {/* PR Review Service */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              📋 PR Review
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              AI-powered pull request review and analysis
            </p>
            <div className="space-y-2 text-sm">
              <div className="text-purple-600">Port: 8002</div>
              <div className="text-gray-500">Status: Coming Soon</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📡 API Endpoints</h2>
          
          <div className="space-y-6">
            {/* System Status */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">System Status</h3>
              <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                <div className="text-blue-600">GET /api/status</div>
                <div className="text-gray-600 text-xs mt-1">Check all services status</div>
              </div>
            </div>

            {/* Dependency Health */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🛡️ Dependency Health</h3>
              <div className="space-y-2">
                <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                  <div className="text-blue-600">POST /api/dependency-health/check-file</div>
                  <div className="text-gray-600 text-xs mt-1">Upload requirements.txt or package.json</div>
                </div>
                <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                  <div className="text-blue-600">POST /api/dependency-health/check-github</div>
                  <div className="text-gray-600 text-xs mt-1">Analyze GitHub repository</div>
                </div>
                <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                  <div className="text-blue-600">POST /api/dependency-health/check-text</div>
                  <div className="text-gray-600 text-xs mt-1">Analyze text content</div>
                </div>
              </div>
            </div>

            {/* Auto Tests */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🧪 Auto Tests</h3>
              <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                <div className="text-green-600">POST /api/auto-tests/generate</div>
                <div className="text-gray-600 text-xs mt-1">Generate test cases for code</div>
              </div>
            </div>

            {/* PR Review */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">📋 PR Review</h3>
              <div className="bg-gray-50 rounded p-3 font-mono text-sm">
                <div className="text-purple-600">POST /api/pr-review/review</div>
                <div className="text-gray-600 text-xs mt-1">Review pull request or code diff</div>
              </div>
            </div>
          </div>
        </div>

        <footer className="text-center mt-12 text-gray-600">
          <p>🎯 Ready to connect with your React frontend!</p>
          <p className="text-sm mt-2">Next.js Backend • Port 3000</p>
        </footer>
      </div>
    </div>
  );
}

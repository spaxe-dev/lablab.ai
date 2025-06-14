import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Optimize for production deployment
  output: 'standalone',
  
  // Configure external packages for server components
  serverExternalPackages: [],
  
  // Configure environment variables
  env: {
    DEPENDENCY_HEALTH_URL: process.env.DEPENDENCY_HEALTH_URL,
    AUTO_TESTS_URL: process.env.AUTO_TESTS_URL,
    PR_REVIEW_URL: process.env.PR_REVIEW_URL,
  },
  
  // CORS and API configuration
  async headers() {
    return [
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },
};

export default nextConfig;

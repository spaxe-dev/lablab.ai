import { NextResponse } from 'next/server';
import { API_CONFIG } from '../config';

export async function GET() {
  const services = [
    { 
      name: 'dependency-health', 
      url: `${API_CONFIG.services.dependencyHealth.baseUrl}/health`, 
      port: new URL(API_CONFIG.services.dependencyHealth.baseUrl).port || '8000'
    },
    { 
      name: 'auto-tests', 
      url: `${API_CONFIG.services.autoTests.baseUrl}/health`, 
      port: new URL(API_CONFIG.services.autoTests.baseUrl).port || '8001'
    },
    { 
      name: 'pr-review', 
      url: `${API_CONFIG.services.prReview.baseUrl}/health`, 
      port: new URL(API_CONFIG.services.prReview.baseUrl).port || '8002'
    }
  ];

  const serviceStatuses = await Promise.allSettled(
    services.map(async (service) => {
      try {
        const response = await fetch(service.url, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        return {
          name: service.name,
          status: response.ok ? 'healthy' : 'unhealthy',
          port: service.port,
          available: response.ok
        };
      } catch (error) {
        return {
          name: service.name,
          status: 'unhealthy',
          port: service.port,
          available: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    })
  );

  const results = serviceStatuses.map((result) => 
    result.status === 'fulfilled' ? result.value : {
      name: 'unknown',
      status: 'error',
      available: false,
      error: 'Failed to check service'
    }
  );

  const healthyServices = results.filter(service => service.available).length;
  const totalServices = services.length;

  return NextResponse.json({
    success: true,
    backend_status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {
      healthy: healthyServices,
      total: totalServices,
      details: results
    },
    endpoints: {
      'dependency-health': {
        'check-file': '/api/dependency-health/check-file',
        'check-github': '/api/dependency-health/check-github', 
        'check-text': '/api/dependency-health/check-text',
        'health': '/api/dependency-health/health'
      },
      'auto-tests': {
        'generate': '/api/auto-tests/generate',
        'health': '/api/auto-tests/health'
      },
      'pr-review': {
        'review': '/api/pr-review/review',
        'health': '/api/pr-review/health'
      }
    }
  });
}

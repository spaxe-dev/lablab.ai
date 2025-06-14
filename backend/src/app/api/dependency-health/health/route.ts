import { NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const DEPENDENCY_HEALTH_API = API_CONFIG.services.dependencyHealth.baseUrl;

export async function GET() {
  try {
    // Check if the dependency health service is running
    const response = await fetch(`${DEPENDENCY_HEALTH_API}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Service unavailable: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      service: 'dependency-health',
      status: 'healthy',
      data: data
    });

  } catch (error) {
    console.error('Dependency health service check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        service: 'dependency-health',
        status: 'unhealthy',
        error: 'Service unavailable',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}

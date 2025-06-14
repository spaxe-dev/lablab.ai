import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const DEPENDENCY_HEALTH_API = API_CONFIG.services.dependencyHealth.baseUrl;

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // Forward the file upload to the FastAPI service
    const response = await fetch(`${DEPENDENCY_HEALTH_API}/check-file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`FastAPI service error: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error) {
    console.error('Dependency health check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to check dependencies',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

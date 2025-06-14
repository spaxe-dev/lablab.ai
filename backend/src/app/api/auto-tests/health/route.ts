import { NextResponse } from 'next/server';

const AUTO_TESTS_API = 'http://localhost:8001';

export async function GET() {
  try {
    // Check if the auto-tests service is running
    const response = await fetch(`${AUTO_TESTS_API}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Service unavailable: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      service: 'auto-tests',
      status: 'healthy',
      data: data
    });

  } catch (error) {
    console.error('Auto-tests service check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        service: 'auto-tests',
        status: 'unhealthy',
        error: 'Service unavailable',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}

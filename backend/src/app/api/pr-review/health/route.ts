import { NextResponse } from 'next/server';

const PR_REVIEW_API = 'http://localhost:8002';

export async function GET() {
  try {
    // Check if the PR review service is running
    const response = await fetch(`${PR_REVIEW_API}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Service unavailable: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      service: 'pr-review',
      status: 'healthy',
      data: data
    });

  } catch (error) {
    console.error('PR review service check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        service: 'pr-review',
        status: 'unhealthy',
        error: 'Service unavailable',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}

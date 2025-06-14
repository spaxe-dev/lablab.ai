import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const DEPENDENCY_HEALTH_API = API_CONFIG.services.dependencyHealth.baseUrl;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.repo_url) {
      return NextResponse.json(
        { success: false, error: 'Repository URL is required' },
        { status: 400 }
      );
    }

    // Forward the request to the FastAPI service
    const response = await fetch(`${DEPENDENCY_HEALTH_API}/check-github`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_url: body.repo_url,
        branch: body.branch || 'main'
      }),
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
    console.error('GitHub dependency check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to check GitHub repository',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

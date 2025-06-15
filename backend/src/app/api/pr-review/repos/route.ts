import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const PR_REVIEW_API = API_CONFIG.services.prReview.baseUrl;

export async function GET() {
  try {
    // Get watched repositories from PR review service
    const response = await fetch(`${PR_REVIEW_API}/api/repos`, {
      method: 'GET',
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
    console.error('PR review repos fetch error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch watched repositories',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.repo_name) {
      return NextResponse.json(
        { success: false, error: 'Repository name is required' },
        { status: 400 }
      );
    }

    // Forward the request to the FastAPI service
    const response = await fetch(`${PR_REVIEW_API}/api/repos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_name: body.repo_name,
        discord_channel_id: body.discord_channel_id
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `FastAPI service error: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error) {
    console.error('PR review repo add error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to add repository',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

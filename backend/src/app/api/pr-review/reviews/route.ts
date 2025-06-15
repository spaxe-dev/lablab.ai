import { NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const PR_REVIEW_API = API_CONFIG.services.prReview.baseUrl;

export async function GET() {
  try {
    // Get recent PR reviews from service
    const response = await fetch(`${PR_REVIEW_API}/api/reviews`, {
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
    console.error('PR review history fetch error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch PR review history',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from 'next/server';

const PR_REVIEW_API = 'http://localhost:8002'; // Assuming different port for each service

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.pr_url && !body.code_diff) {
      return NextResponse.json(
        { success: false, error: 'Either pr_url or code_diff is required' },
        { status: 400 }
      );
    }

    // Forward the request to the PR review service
    const response = await fetch(`${PR_REVIEW_API}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pr_url: body.pr_url,
        code_diff: body.code_diff,
        repository: body.repository,
        review_type: body.review_type || 'comprehensive'
      }),
    });

    if (!response.ok) {
      throw new Error(`PR review service error: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error) {
    console.error('PR review error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to review PR',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

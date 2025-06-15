import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '../../../config';

const PR_REVIEW_API = API_CONFIG.services.prReview.baseUrl;

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const repoId = params.id;
    
    if (!repoId) {
      return NextResponse.json(
        { success: false, error: 'Repository ID is required' },
        { status: 400 }
      );
    }

    // Forward the delete request to the FastAPI service
    const response = await fetch(`${PR_REVIEW_API}/api/repos/${repoId}`, {
      method: 'DELETE',
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
    console.error('PR review repo delete error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to remove repository',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

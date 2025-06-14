import { NextRequest, NextResponse } from 'next/server';
import { API_CONFIG } from '../../config';

const DEPENDENCY_HEALTH_API = API_CONFIG.services.dependencyHealth.baseUrl;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.content || !body.file_type) {
      return NextResponse.json(
        { success: false, error: 'Content and file_type are required' },
        { status: 400 }
      );
    }

    // Validate file type
    if (!['requirements.txt', 'package.json'].includes(body.file_type)) {
      return NextResponse.json(
        { success: false, error: 'Invalid file type. Must be requirements.txt or package.json' },
        { status: 400 }
      );
    }

    // Create form data for the FastAPI service
    const formData = new FormData();
    formData.append('content', body.content);
    formData.append('file_type', body.file_type);

    // Forward the request to the FastAPI service
    const response = await fetch(`${DEPENDENCY_HEALTH_API}/check-text`, {
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
    console.error('Text dependency check error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to check dependencies from text',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

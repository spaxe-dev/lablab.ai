import { NextRequest, NextResponse } from 'next/server';

const AUTO_TESTS_API = 'http://localhost:8001'; // Assuming different port for each service

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.code) {
      return NextResponse.json(
        { success: false, error: 'Code is required' },
        { status: 400 }
      );
    }

    // Forward the request to the auto-tests service
    const response = await fetch(`${AUTO_TESTS_API}/generate-tests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: body.code,
        language: body.language || 'python',
        test_type: body.test_type || 'unit'
      }),
    });

    if (!response.ok) {
      throw new Error(`Auto-tests service error: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      data: data
    });

  } catch (error) {
    console.error('Auto-tests generation error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to generate tests',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    message: 'StackHub Backend API is running',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    status: 'healthy'
  });
}

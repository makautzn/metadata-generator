/**
 * Catch-all API proxy route handler.
 *
 * Forwards all /api/v1/* requests to the backend FastAPI server.
 * Uses a generous timeout to support long-running Azure analysis operations.
 */

import { type NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';

/** Timeout for proxied requests (120 seconds) to handle long Azure analysis. */
const PROXY_TIMEOUT_MS = 120_000;

/** Headers that must not be forwarded through the proxy. */
const SKIP_HEADERS = new Set([
  'host',
  'connection',
  'keep-alive',
  'transfer-encoding',
  'te',
  'trailer',
  'upgrade',
  'expect',
]);

async function proxyRequest(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
): Promise<NextResponse> {
  const { path } = await params;
  const targetPath = `/api/v1/${path.join('/')}`;
  const url = new URL(targetPath, BACKEND_URL);

  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  // Build headers, skipping hop-by-hop and unsupported headers
  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!SKIP_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  // Read request body into a buffer so we can forward it reliably
  const body =
    request.method !== 'GET' && request.method !== 'HEAD' && request.body
      ? Buffer.from(await request.arrayBuffer())
      : undefined;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), PROXY_TIMEOUT_MS);

  try {
    const response = await fetch(url.toString(), {
      method: request.method,
      headers,
      body,
      signal: controller.signal,
    });

    // Forward response headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!SKIP_HEADERS.has(key.toLowerCase())) {
        responseHeaders.set(key, value);
      }
    });

    const responseBody = await response.arrayBuffer();
    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return NextResponse.json(
        { detail: 'Backend request timed out', error_code: 'PROXY_TIMEOUT' },
        { status: 504 },
      );
    }
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to reach backend', error_code: 'PROXY_ERROR' },
      { status: 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const PATCH = proxyRequest;

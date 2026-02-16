/**
 * Tests for the typed API client.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { buildUrl, get, post, put, del, uploadFile } from './api-client';

/* ------------------------------------------------------------------ */
/*  buildUrl                                                          */
/* ------------------------------------------------------------------ */

describe('buildUrl', () => {
  it('constructs a full URL from a relative path', () => {
    expect(buildUrl('/health')).toBe('http://localhost:8000/api/v1/health');
  });

  it('normalizes paths without leading slash', () => {
    expect(buildUrl('health')).toBe('http://localhost:8000/api/v1/health');
  });
});

/* ------------------------------------------------------------------ */
/*  HTTP methods                                                      */
/* ------------------------------------------------------------------ */

describe('API client HTTP methods', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    mockFetch.mockReset();
    vi.stubGlobal('fetch', mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('get() returns ok result on 200', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'healthy' }),
    });

    const result = await get<{ status: string }>('/health');
    expect(result).toEqual({ ok: true, data: { status: 'healthy' } });
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/health',
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('post() sends JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '1' }),
    });

    const result = await post<{ id: string }>('/items', { name: 'test' });
    expect(result).toEqual({ ok: true, data: { id: '1' } });

    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe('POST');
    expect(init.body).toBe(JSON.stringify({ name: 'test' }));
  });

  it('put() sends JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated: true }),
    });

    const result = await put<{ updated: boolean }>('/items/1', { name: 'updated' });
    expect(result).toEqual({ ok: true, data: { updated: true } });
  });

  it('del() sends DELETE request', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ deleted: true }),
    });

    const result = await del<{ deleted: boolean }>('/items/1');
    expect(result).toEqual({ ok: true, data: { deleted: true } });

    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe('DELETE');
  });

  it('returns error result on non-ok response with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: async () => ({ error_code: 'VALIDATION', message: 'Invalid input' }),
    });

    const result = await get('/bad');
    expect(result).toEqual({
      ok: false,
      error: { error_code: 'VALIDATION', message: 'Invalid input' },
    });
  });

  it('returns error result on non-ok response without JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: async () => {
        throw new Error('not json');
      },
    });

    const result = await get('/fail');
    expect(result).toEqual({
      ok: false,
      error: { error_code: 'HTTP_500', message: 'Internal Server Error' },
    });
  });

  it('returns NETWORK_ERROR on fetch failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network down'));

    const result = await get('/offline');
    expect(result).toEqual({
      ok: false,
      error: { error_code: 'NETWORK_ERROR', message: 'Network down' },
    });
  });
});

/* ------------------------------------------------------------------ */
/*  uploadFile                                                        */
/* ------------------------------------------------------------------ */

describe('uploadFile', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    mockFetch.mockReset();
    vi.stubGlobal('fetch', mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('sends FormData without explicit Content-Type', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'file-1' }),
    });

    const formData = new FormData();
    const result = await uploadFile<{ id: string }>('/upload', formData);

    expect(result).toEqual({ ok: true, data: { id: 'file-1' } });

    const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe('POST');
    expect(init.body).toBe(formData);
    // Should NOT have Content-Type header (browser sets boundary)
    expect(init.headers as Record<string, string> | undefined).toBeUndefined();
  });

  it('returns error on upload failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Upload failed'));

    const result = await uploadFile('/upload', new FormData());
    expect(result).toEqual({
      ok: false,
      error: { error_code: 'NETWORK_ERROR', message: 'Upload failed' },
    });
  });
});

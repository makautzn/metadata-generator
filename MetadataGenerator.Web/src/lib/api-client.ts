/**
 * Typed fetch wrapper for the Metadata Generator backend API.
 *
 * All requests are made against the base URL defined by the
 * NEXT_PUBLIC_API_URL environment variable.
 */

import type { ApiError, ApiResult } from './types';

/** Base URL for all API requests — configurable via env */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

/**
 * Build a full URL for the given API path.
 * Leading slashes on `path` are normalized.
 */
export function buildUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

/**
 * Parse an error response body into an `ApiError`.
 */
async function parseError(response: Response): Promise<ApiError> {
  try {
    const body: unknown = await response.json();
    if (typeof body === 'object' && body !== null && 'error_code' in body && 'message' in body) {
      return body as ApiError;
    }
  } catch {
    // response body is not JSON — fall through
  }

  return {
    error_code: `HTTP_${response.status}`,
    message: response.statusText || 'An unexpected error occurred',
  };
}

/**
 * Generic typed fetch helper.
 *
 * @param path  - API path relative to the base URL (e.g. `/health`).
 * @param init  - Standard `RequestInit` options.
 * @returns     - An `ApiResult<T>` discriminated union.
 */
async function request<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  const url = buildUrl(path);

  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    });

    if (!response.ok) {
      const error = await parseError(response);
      return { ok: false, error };
    }

    const data = (await response.json()) as T;
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      error: {
        error_code: 'NETWORK_ERROR',
        message: err instanceof Error ? err.message : 'Network request failed',
      },
    };
  }
}

/** HTTP GET */
export function get<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  return request<T>(path, { ...init, method: 'GET' });
}

/** HTTP POST */
export function post<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResult<T>> {
  return request<T>(path, {
    ...init,
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

/** HTTP PUT */
export function put<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResult<T>> {
  return request<T>(path, {
    ...init,
    method: 'PUT',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

/** HTTP DELETE */
export function del<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  return request<T>(path, { ...init, method: 'DELETE' });
}

/**
 * Upload a file via multipart/form-data POST.
 *
 * Does NOT set Content-Type — the browser adds the correct boundary.
 */
export async function uploadFile<T>(path: string, formData: FormData): Promise<ApiResult<T>> {
  const url = buildUrl(path);

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await parseError(response);
      return { ok: false, error };
    }

    const data = (await response.json()) as T;
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      error: {
        error_code: 'NETWORK_ERROR',
        message: err instanceof Error ? err.message : 'File upload failed',
      },
    };
  }
}

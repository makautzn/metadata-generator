"""Correlation ID middleware.

Attaches a unique correlation/request ID to every incoming request.
The ID is forwarded from the ``X-Correlation-ID`` header when present,
otherwise a new UUID4 is generated.  The ID is also set on the response.
"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware that ensures every request/response carries a correlation ID."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,  # type: ignore[type-arg]
    ) -> Response:
        """Extract or generate a correlation ID and attach it to the response."""
        correlation_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))
        # Store on request state so downstream code can access it
        request.state.correlation_id = correlation_id

        response: Response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response

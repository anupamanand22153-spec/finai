from collections import deque
import json
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Stores the most recent 20 live flow events for the dashboard
flow_event_history = deque(maxlen=20)


class FlowVisualizerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # Ignore polling requests so the visualizer doesn't trace itself
        if request.url.path.startswith("/flow"):
            return await call_next(request)

        start_time = time.time()
        client_host = request.client.host if request.client else "127.0.0.1"

        # Record incoming event start
        event_id = int(time.time() * 1000)
        current_event = {
            "id": event_id,
            "timestamp": time.strftime("%H:%M:%S"),
            "method": request.method,
            "path": request.url.path,
            "client": client_host,
            "status": "processing",
            "latency_ms": 0,
            "failed_at": None,
        }
        flow_event_history.append(current_event)

        print("\n" + "=" * 62)
        print(f"📡 [CLIENT -> API] {request.method} {request.url.path}")
        print(f"   Origin : {client_host}")
        print("-" * 62)

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            current_event["status"] = (
                "success" if response.status_code < 400 else "error"
            )
            current_event["status_code"] = response.status_code
            current_event["latency_ms"] = duration_ms

            if response.status_code == 422:
                current_event["failed_at"] = "pydantic"
            elif response.status_code == 404:
                current_event["failed_at"] = "router"
            elif response.status_code >= 500:
                current_event["failed_at"] = "database"

            symbol = "✅" if response.status_code < 400 else "⚠️️"
            print("-" * 62)
            print(f"{symbol} [API -> CLIENT] Dispatched ({response.status_code})")
            print(f"   Latency: {duration_ms} ms")
            print("=" * 62 + "\n")

            return response
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            current_event["status"] = "error"
            current_event["status_code"] = 500
            current_event["latency_ms"] = duration_ms
            current_event["failed_at"] = "middleware"

            print("-" * 62)
            print(f"❌ [CRASH DETECTED] {exc}")
            print("=" * 62 + "\n")
            raise exc
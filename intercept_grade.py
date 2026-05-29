"""mitmproxy demo script for manual request/response tampering.

Use with `mitmweb` or interactive `mitmproxy` so you can pause a flow,
edit the JSON body, then resume it.
"""

import json
from typing import Any

from mitmproxy import http

TARGET_ENDPOINTS = {
    "/api/student",
    "/api/admin/users",
    "/api/admin/policies",
    "/api/dashboard",
}


def pretty_json(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, sort_keys=True)
    except Exception:
        return str(value)


def parse_json_body(text: str):
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def is_target(flow: http.HTTPFlow) -> bool:
    return any(flow.request.path.startswith(endpoint) for endpoint in TARGET_ENDPOINTS)


def request(flow: http.HTTPFlow) -> None:
    if not is_target(flow):
        return

    flow.metadata["demo_target"] = True
    flow.intercept()

    payload = parse_json_body(flow.request.get_text() or "")
    print(f"\n[PAUSED REQUEST] {flow.request.method} {flow.request.path}")
    if payload is not None:
        print(pretty_json(payload))
    print("[ACTION] Edit the request in mitmweb/mitmproxy, then press 'a' to resume.")


def response(flow: http.HTTPFlow) -> None:
    if not flow.metadata.get("demo_target"):
        return

    flow.intercept()

    payload = parse_json_body(flow.response.get_text() or "") if flow.response else None
    print(f"\n[PAUSED RESPONSE] {flow.request.method} {flow.request.path} -> HTTP {flow.response.status_code if flow.response else '??'}")
    if payload is not None:
        print(pretty_json(payload))
    print("[ACTION] Edit the response in mitmweb/mitmproxy, then press 'a' to resume.")

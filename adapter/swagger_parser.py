from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from saltbox_sdk.discovery_client.schemas import OPAConfig, ServiceEndpoint

ALLOWED_METHODS = {'get', 'post', 'put', 'delete', 'patch'}

METHOD_TO_ACTION = {
    'get': 'read',
    'post': 'write',
    'put': 'write',
    'patch': 'write',
    'delete': 'write',
}

METHOD_TO_POLICY = {
    'get': 'public',
    'post': 'default',
    'put': 'default',
    'patch': 'default',
    'delete': 'default',
}

READ_CACHE_TTL = 60


def load_swagger(path: str) -> dict[str, Any]:
    with Path(path).open() as f:
        result: dict[str, Any] = yaml.safe_load(f)
        return result


def parse_endpoints(swagger: dict) -> list[ServiceEndpoint]:
    """Parse Swagger 2.0 paths into ServiceEndpoint list.

    Swagger 2.0 path-item can contain 'parameters' (a list) alongside
    HTTP method objects (dicts) — we skip non-dict entries.
    """
    endpoints = []
    for path, methods in swagger.get('paths', {}).items():
        for method, details in methods.items():
            if not isinstance(details, dict):
                continue
            if method.lower() not in ALLOWED_METHODS:
                continue

            method_lower = method.lower()
            action = METHOD_TO_ACTION.get(method_lower, 'read')
            policy = METHOD_TO_POLICY.get(method_lower, 'default')
            cache_ttl = READ_CACHE_TTL if action == 'read' else 0

            endpoints.append(
                ServiceEndpoint(
                    path=path,
                    method=method.upper(),
                    summary=details.get('summary', ''),
                    description=details.get('description', ''),
                    opa_config=OPAConfig(
                        policy=policy,
                        action=action,
                        is_partial=False,
                    ),
                    cache_ttl=cache_ttl,
                )
            )
    return endpoints

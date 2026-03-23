import asyncio
import logging

import httpx

from adapter.config import SETTINGS
from saltbox_sdk.discovery_client.schemas import (
    ProxyBalancingStrategy,
    ServiceEndpoint,
    ServiceFrontendConfig,
    ServiceFrontendEnv,
    ServiceInstance,
    ServiceSchema,
    ServiceType,
)

logger = logging.getLogger(__name__)

RETRY_INTERVAL_SEC = 5
MAX_RETRIES = 30


def build_service_schema(endpoints: list[ServiceEndpoint]) -> ServiceSchema:
    instance = ServiceInstance(
        id=SETTINGS.instance_id,
        host=SETTINGS.filebrowser_host,
        port=SETTINGS.filebrowser_port,
        base_route=SETTINGS.filebrowser_base_route,
        version=None,
        healthcheck_path=f'{SETTINGS.filebrowser_base_route}/health',
        docs_path=None,
        openapi_path=None,
        enabled=True,
        endpoints=endpoints,
    )

    api_url = f'{SETTINGS.server_scheme}://{SETTINGS.server_outer_socket.strip("/")}/api/{SETTINGS.service_name}'
    static_url = f'{SETTINGS.server_scheme}://{SETTINGS.server_outer_socket.strip("/")}/static/filebrowser'
    front_config = ServiceFrontendConfig(
        service_name=SETTINGS.service_name,
        url=static_url,
        static_host='saltbox-filesystem-frontend',
        env=ServiceFrontendEnv(
            api_base_path=api_url,
            ws_server_url=None,
        ),
    )

    return ServiceSchema(
        name=SETTINGS.service_name,
        title=SETTINGS.service_title,
        description=SETTINGS.service_description,
        vendor=SETTINGS.service_vendor,
        type=ServiceType.THIRD_PARTY,
        instances=[instance],
        enabled=True,
        load_balancing_strategy=ProxyBalancingStrategy.ROUND_ROBIN,
        front_config=front_config,
    )


async def check_gateway(client: httpx.AsyncClient) -> bool:
    try:
        response = await client.get(f'{SETTINGS.discovery_url}/health', timeout=2.0)
        return response.status_code == 200
    except Exception as e:
        logger.warning('Gateway unavailable: %s', e)
        return False


async def register(service: ServiceSchema) -> None:
    payload = service.model_dump()

    async with httpx.AsyncClient() as client:
        for attempt in range(1, MAX_RETRIES + 1):
            if not await check_gateway(client):
                logger.warning(
                    'Gateway not ready, retry in %ss... (attempt %d/%d)',
                    RETRY_INTERVAL_SEC,
                    attempt,
                    MAX_RETRIES,
                )
                await asyncio.sleep(RETRY_INTERVAL_SEC)
                continue
            try:
                response = await client.post(
                    f'{SETTINGS.discovery_url}/register',
                    json=payload,
                    timeout=5.0,
                    headers={'Content-Type': 'application/json'},
                )
                if response.status_code == 200:
                    logger.info(
                        'Service "%s" registered at %s:%s',
                        SETTINGS.service_name,
                        SETTINGS.filebrowser_host,
                        SETTINGS.filebrowser_port,
                    )
                    return
                logger.error('Registration failed (%s): %s', response.status_code, response.text)
            except Exception as e:
                logger.error('Registration error: %s', e)

            await asyncio.sleep(RETRY_INTERVAL_SEC)

        msg = f'Failed to register service "{SETTINGS.service_name}" after {MAX_RETRIES} attempts'
        raise RuntimeError(msg)

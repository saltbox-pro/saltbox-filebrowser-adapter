import asyncio
import logging

from adapter.config import SETTINGS
from adapter.registrar import build_service_schema, register
from adapter.swagger_parser import load_swagger, parse_endpoints

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info('Loading swagger from %s', SETTINGS.swagger_path)
    swagger = load_swagger(SETTINGS.swagger_path)

    endpoints = parse_endpoints(swagger)
    logger.info('Parsed %d endpoints from swagger', len(endpoints))

    service = build_service_schema(endpoints)
    logger.info('Registering service "%s" in gateway at %s', service.name, SETTINGS.discovery_url)

    await register(service)


if __name__ == '__main__':
    asyncio.run(main())

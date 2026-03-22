import os
from pathlib import Path
from uuid import uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(os.environ.get('ADAPTER_ENV_FILE', '.env'))


class AdapterSettings(BaseSettings):
    filebrowser_host: str
    filebrowser_port: int = 80
    filebrowser_base_route: str
    discovery_url: str

    service_name: str = 'filebrowser'
    service_title: str = 'FileBrowser'
    service_description: str = 'Third-party file browser service'
    service_vendor: str = 'FileBrowser'

    server_outer_socket: str = 'localhost'
    server_scheme: str = 'http'

    swagger_path: str = './swagger.yaml'

    instance_id: str = Field(default_factory=lambda: uuid4().hex)

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix='ADAPTER_', extra='ignore')


SETTINGS = AdapterSettings()

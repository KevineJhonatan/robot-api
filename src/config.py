import logging
import os
from typing import Any

from starlette.config import Config

from src.enums import Run_Modes

log = logging.getLogger(__name__)

def reload_env_config():
    """Recharge la configuration depuis le fichier .env"""
    global config, SNAPLOGIC_BASE_URL, SNAPLOGIC_UPLOAD_ENDPOINT, SNAPLOGIC_BEARER,SNAPLOGIC_NOTIFICATION_ENDPOINT,SNAPLOGIC_NOTIFICATION_BEARER
    
    RUN_MODE = os.environ.get('RUN_MODE', Run_Modes.dev)
    if RUN_MODE == Run_Modes.prod:
        config = Config()
    else:
        config = Config(".env")
    
    # Recharger les variables Snaplogic
    SNAPLOGIC_BASE_URL = config("SNAPLOGIC_BASE_URL", cast=str)
    SNAPLOGIC_UPLOAD_ENDPOINT = config("SNAPLOGIC_UPLOAD_ENDPOINT", cast=str)
    SNAPLOGIC_BEARER = config("SNAPLOGIC_BEARER", cast=str)
    SNAPLOGIC_NOTIFICATION_ENDPOINT = config("SNAPLOGIC_NOTIFICATION_ENDPOINT", default=None)
    SNAPLOGIC_NOTIFICATION_BEARER = config("SNAPLOGIC_NOTIFICATION_BEARER", default=None)

# Configuration initiale
RUN_MODE = os.environ.get('RUN_MODE', Run_Modes.dev)
if RUN_MODE == Run_Modes.prod:
    config = Config()
else:
    config = Config(".env")

ENTREPRISES_URL=config("ENTREPRISES_URL", default=None)
VERIFID_URL =   config("VERIFID_URL", default=None)
AVP_URL=        config("AVP_URL", default=None)
PDF_AVP_URL =   config("PDF_AVP_URL", default=None)
ALTS_URL =      config("ALTS_URL", default=None)
ALT_URL =       config("ALT_URL", default=None)
ALT_EDP_URL =   config("ALT_EDP_URL", default=None)

SNAPLOGIC_BASE_URL = config("SNAPLOGIC_BASE_URL", default=None)
SNAPLOGIC_UPLOAD_ENDPOINT = config("SNAPLOGIC_UPLOAD_ENDPOINT", default=None)
SNAPLOGIC_BEARER = config("SNAPLOGIC_BEARER", default=None)

SNAPLOGIC_NOTIFICATION_ENDPOINT = config("SNAPLOGIC_NOTIFICATION_ENDPOINT", default=None)
SNAPLOGIC_NOTIFICATION_BEARER = config("SNAPLOGIC_NOTIFICATION_BEARER", default=None)


# class CustomBaseSettings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env", env_file_encoding="utf-8", extra="ignore"
#     )


# class APIConfig(CustomBaseSettings):

#     ENVIRONMENT: Environment = Environment.PRODUCTION


#     CORS_ORIGINS: list[str] = ["*"]
#     CORS_ORIGINS_REGEX: str | None = None
#     CORS_HEADERS: list[str] = ["*"]

#     APP_VERSION: str = "0.1"

# settings = APIConfig()


# class BaseConfigurationModel(BaseModel):
#     """Base configuration model used by all config options."""

#     pass


# def get_env_tags(tag_list: List[str]) -> dict:
#     """Create dictionary of available env tags."""
#     tags = {}
#     for t in tag_list:
#         tag_key, env_key = t.split(":")

#         env_value = os.environ.get(env_key)

#         if env_value:
#             tags.update({tag_key: env_value})

#     return tags

# LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)
# ENV = config("ENV", default="local")

# ENV_TAG_LIST = config("ENV_TAGS", cast=CommaSeparatedStrings, default="")
# ENV_TAGS = get_env_tags(ENV_TAG_LIST)


# SYLAE_ENCRYPTION_KEY = config("SYLAE_ENCRYPTION_KEY", cast=Secret)


# SYLAE_JWT_SECRET = config("SYLAE_JWT_SECRET", default=None)
# SYLAE_JWT_ALG = config("SYLAE_JWT_ALG", default="HS256")
# SYLAE_JWT_EXP = config("SYLAE_JWT_EXP", cast=int, default=86400)  # Seconds



# metrics
# METRIC_PROVIDERS = config("METRIC_PROVIDERS", cast=CommaSeparatedStrings, default="")

# # database
# SYLAE_CREDENTIALS = config("SYLAE_CREDENTIALS", cast=Secret)
# # this will support special chars for credentials
# _SYLAE_CREDENTIAL_USER, _SYLAE_CREDENTIAL_PASSWORD = str(SYLAE_CREDENTIALS).split(":")
# _QUOTED_SYLAE_PASSWORD = parse.quote(str(_SYLAE_CREDENTIAL_PASSWORD))


# API Conf
app_configs: dict[str, Any] = {
    "title": "Robot Sylaé API",
    "description":"Welcome to Robot Sylaé's API documentation! Here you will able to discover all of the ways you can interact with the Robot Sylaé API.",
    "root_path":"/api/v1",
   "docs_url": "/swagger",
    "openapi_url": "/docs/openapi.json",
    "redoc_url": "/redoc",
    }

# # Cache la doc Swagger hors dev
# if not settings.ENVIRONMENT.is_debug:
#     app_configs["openapi_url"] = None  # hide docs

# # ajouter la version en Prod
# if settings.ENVIRONMENT.is_deployed:
#     app_configs["root_path"] = f"/v{settings.APP_VERSION}"

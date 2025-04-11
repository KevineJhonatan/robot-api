# Python Included
import logging
# from .logging import configure_logging

# FastAPI
from fastapi import FastAPI

# Middlewares
#from sentry_asgi import SentryMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .middlewares.exceptions import ExceptionMiddleware, exception_handlers
from .middlewares.metrics import MetricsMiddleware
from .middlewares.rate_limiter import limiter
#from .metrics import provider as metric_provider

# Imports
from .api import api_router
from .config import app_configs

from contextlib import asynccontextmanager
from typing import AsyncGenerator

log = logging.getLogger(__name__)
# configure_logging()

# we create the ASGI for the app
app = FastAPI(exception_handlers=exception_handlers, openapi_url="")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#app.add_middleware(GZipMiddleware, minimum_size=1000)

@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Code executed on the Startup
    yield
    # Code executed on the Shutdown


# we create the Web API framework
api = FastAPI(
    **app_configs,
    lifespan=lifespan,
    version="1.0.0-rc1"
)

#api.add_middleware(SentryMiddleware)

api.add_middleware(MetricsMiddleware)

api.add_middleware(ExceptionMiddleware)


# we install all the plugins
#install_plugins()

# we add all the plugin event API routes to the API router
#install_plugin_events(api_router)

# we add all API routes to the Web API framework
api.include_router(api_router)

# we mount the frontend and app
# if STATIC_DIR and path.isdir(STATIC_DIR):
#     frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/", app=api)
#app.mount("/", app=frontend)
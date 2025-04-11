"""Module pipeline pour le scraping et l'envoi des données à SnapLogic."""

from .views import router as pipeline_router

__all__ = ['pipeline_router']

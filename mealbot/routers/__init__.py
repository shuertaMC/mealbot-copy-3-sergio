"""FastAPI routers package for HTTP endpoint definitions."""

from mealbot.routers.organizations import router as organizations_router

__all__ = ["organizations_router"]

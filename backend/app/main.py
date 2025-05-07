from fastapi import FastAPI

from backend.app.api.v1.endpoints import auth
from backend.app.api.v1.endpoints import llm_configs
from backend.app.api.v1.endpoints import exchange_configs
from backend.app.api.v1.endpoints import websocket # Added WebSocket router import
# Potentially other endpoint routers would be imported here
# from backend.app.api.v1.endpoints import users
# etc.

app = FastAPI(title="VibeTrade API", version="0.1.0")

# API v1 Router
# It's a common practice to have a sub-router for each API version
# or even for different groups of endpoints.
# However, based on current findings, there isn't a central api_v1.py.
# If one were to be created (e.g., backend/app/api/v1/api.py or router.py),
# the individual endpoint routers (auth, llm_configs) would be included there,
# and then that central v1 router would be included here.

# For now, directly including endpoint routers into the main app,
# or creating a simple aggregation here.

# Option 1: Direct inclusion (if no central v1 router exists yet)
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(llm_configs.router, prefix="/api/v1/llm-configs", tags=["LLM Configurations"])

# Option 2: Creating a v1 aggregator router here if one doesn't exist elsewhere
# This is closer to what one might expect if a main.py is the central point.
from fastapi import APIRouter

api_router_v1 = APIRouter()

api_router_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router_v1.include_router(llm_configs.router, prefix="/llm-configs", tags=["LLM Configurations"])
api_router_v1.include_router(exchange_configs.router, prefix="/exchange-configs", tags=["Exchange Configurations"])
# Include other v1 endpoint routers here
# api_router_v1.include_router(users.router, prefix="/users", tags=["Users"])

app.include_router(api_router_v1, prefix="/api/v1")

# WebSocket Router
# WebSocket endpoints are typically not versioned under /api/v1
app.include_router(websocket.router, tags=["WebSocket"])

# Potentially add other global configurations, middleware, event handlers etc.

# Example root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to VibeTrade API"}

# If you are using Uvicorn to run, the command would be something like:
# uvicorn backend.app.main:app --reload
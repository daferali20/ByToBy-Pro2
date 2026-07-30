import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from loguru import logger

from backend.api import (
    auth_router,
    stock_router,
    portfolio_router,
    screener_router,
    ai_router,
    alerts_router
)
from backend.services import DataService, CacheService
from database import DatabaseManager
from scheduler import SchedulerManager

# Configure logging
logger.add("logs/app_{time}.log", rotation="500 MB", retention="10 days")

class ByToByApp:
    def __init__(self):
        self.app = FastAPI(
            title="ByToBy Pro2 AI",
            description="Advanced AI Stock Analysis Platform",
            version="2.0.0",
            lifespan=self.lifespan
        )
        self.setup_middleware()
        self.setup_routers()
        self.db_manager = DatabaseManager()
        self.cache_service = CacheService()
        self.data_service = DataService()
        self.scheduler = SchedulerManager()

    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routers(self):
        """Register API routers"""
        self.app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
        self.app.include_router(stock_router, prefix="/api/stocks", tags=["Stocks"])
        self.app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])
        self.app.include_router(screener_router, prefix="/api/screener", tags=["Screener"])
        self.app.include_router(ai_router, prefix="/api/ai", tags=["AI Analysis"])
        self.app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Lifespan context manager for startup/shutdown events"""
        # Startup
        logger.info("Starting ByToBy Pro2 AI Platform...")
        await self.db_manager.connect()
        await self.cache_service.connect()
        await self.scheduler.start()
        logger.info("Platform started successfully")
        
        yield
        
        # Shutdown
        logger.info("Shutting down ByToBy Pro2 AI Platform...")
        await self.scheduler.stop()
        await self.cache_service.disconnect()
        await self.db_manager.disconnect()
        logger.info("Platform shutdown complete")

app = ByToByApp().app

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": await app.db_manager.health_check(),
            "cache": await app.cache_service.health_check(),
            "scheduler": app.scheduler.health_check()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

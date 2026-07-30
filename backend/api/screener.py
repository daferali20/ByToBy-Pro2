from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.services import ScreenerService
from backend.schemas import ScreenerFilter, ScreenerResult

router = APIRouter()

class ScreenerRequest(BaseModel):
    filters: Dict[str, Any]
    sort_by: Optional[str] = "market_cap"
    sort_order: Optional[str] = "desc"
    limit: Optional[int] = 50

@router.post("/scan", response_model=List[ScreenerResult])
async def scan_stocks(request: ScreenerRequest):
    """Scan stocks based on filters"""
    screener_service = ScreenerService()
    results = await screener_service.scan(request.filters, request.sort_by, request.sort_order)
    return results[:request.limit]

@router.get("/presets/{preset_name}")
async def get_preset_screener(preset_name: str):
    """Get predefined screener presets"""
    presets = {
        "growth_stocks": {
            "filters": {
                "pe_ratio": {"max": 30},
                "revenue_growth": {"min": 20},
                "roic": {"min": 15},
                "debt_to_equity": {"max": 1}
            },
            "sort_by": "revenue_growth",
            "sort_order": "desc"
        },
        "value_stocks": {
            "filters": {
                "pe_ratio": {"max": 15},
                "pb_ratio": {"max": 1.5},
                "dividend_yield": {"min": 3},
                "debt_to_equity": {"max": 0.5}
            },
            "sort_by": "dividend_yield",
            "sort_order": "desc"
        },
        "momentum_stocks": {
            "filters": {
                "price_change_1m": {"min": 10},
                "volume": {"min": 1000000},
                "rsi": {"min": 50, "max": 70}
            },
            "sort_by": "price_change_1m",
            "sort_order": "desc"
        },
        "ai_high_confidence": {
            "filters": {
                "ai_confidence": {"min": 0.8},
                "predicted_return": {"min": 15},
                "sentiment_score": {"min": 0.6}
            },
            "sort_by": "predicted_return",
            "sort_order": "desc"
        }
    }
    
    if preset_name not in presets:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
    
    return presets[preset_name]

@router.get("/watchlist")
async def get_watchlist_screener(
    symbols: List[str] = Query(..., description="Comma-separated list of symbols")
):
    """Scan specific stocks in watchlist"""
    screener_service = ScreenerService()
    results = await screener_service.get_watchlist_analysis(symbols)
    return results

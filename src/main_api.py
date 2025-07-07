from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from src.data.data_manager import DataManager
from loguru import logger

app = FastAPI(title="Financial Research Intelligence API", version="0.1.0")
data_manager = DataManager()

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.get("/stock/price", tags=["Stock"])
def get_stock_price(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        df = data_manager.connectors['yahoo_finance'].get_stock_price(symbol)
        return JSONResponse(df.tail(30).to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Error fetching stock price: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/info", tags=["Stock"])
def get_company_info(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        info = data_manager.connectors['yahoo_finance'].get_company_info(symbol)
        return info
    except Exception as e:
        logger.error(f"Error fetching company info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/financials", tags=["Stock"])
def get_financials(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        df = data_manager.connectors['yahoo_finance'].get_financial_statements(symbol)
        return JSONResponse(df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Error fetching financials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/economic/indicator", tags=["Economic"])
def get_economic_indicator(series_id: str = Query(..., description="FRED series ID")):
    try:
        fred = data_manager.connectors.get('fred')
        if not fred:
            raise HTTPException(status_code=404, detail="FRED connector not available")
        import asyncio
        loop = asyncio.get_event_loop()
        df = loop.run_until_complete(fred._fetch_observations(series_id))
        return JSONResponse(df.tail(30).to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Error fetching economic indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
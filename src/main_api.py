from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from src.data.data_manager import FinancialDataManager as DataManager
from loguru import logger

app = FastAPI(title="Financial Research Intelligence API", version="0.1.0")
data_manager = DataManager()

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.get("/stock/price", tags=["Stock"])
async def get_stock_price(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        df = await data_manager.connectors['yahoo_finance'].get_stock_price(symbol)
        # Convert datetime objects to strings for JSON serialization
        df_copy = df.copy()
        
        # Convert index to string if it's datetime
        if hasattr(df_copy.index, 'strftime'):
            df_copy.index = df_copy.index.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert all object columns to strings
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                df_copy[col] = df_copy[col].astype(str)
        
        # Convert to records and ensure all values are JSON serializable
        records = df_copy.tail(30).to_dict(orient="records")
        
        # Convert any remaining non-serializable objects
        for record in records:
            for key, value in record.items():
                if hasattr(value, 'isoformat'):  # datetime objects
                    record[key] = value.isoformat()
                elif hasattr(value, 'strftime'):  # timestamp objects
                    record[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return JSONResponse(records)
    except Exception as e:
        logger.error(f"Error fetching stock price: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/info", tags=["Stock"])
async def get_company_info(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        info = await data_manager.connectors['yahoo_finance'].get_company_info(symbol)
        return info
    except Exception as e:
        logger.error(f"Error fetching company info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/financials", tags=["Stock"])
async def get_financials(symbol: str = Query(..., description="Stock ticker symbol")):
    try:
        df = await data_manager.connectors['yahoo_finance'].get_financial_statements(symbol)
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
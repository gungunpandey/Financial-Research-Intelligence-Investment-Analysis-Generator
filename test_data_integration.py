"""
Test script for data integration functionality.
"""

import asyncio
import pandas as pd
from datetime import datetime
import os

# Add src to path
import sys
sys.path.append('src')

from src.data.data_manager import FinancialDataManager
from src.data.connectors import YahooFinanceConnector

async def test_yahoo_finance():
    """Test Yahoo Finance connector."""
    print("🔍 Testing Yahoo Finance Connector...")
    
    try:
        connector = YahooFinanceConnector()
        
        # Test stock price data
        print("📈 Fetching AAPL stock price data...")
        price_data = await connector.get_stock_price('AAPL', period='1mo')
        print(f"✅ Successfully fetched {len(price_data)} price records")
        print(f"   Latest price: ${price_data.iloc[-1]['Close']:.2f}")
        
        # Test company info
        print("🏢 Fetching AAPL company info...")
        company_info = await connector.get_company_info('AAPL')
        if isinstance(company_info, dict):
            name = company_info.get('longName')
            if isinstance(name, pd.Series):
                name = name.iloc[0]
            print(f"✅ Company: {name}")
        else:
            print(f"✅ Company: {company_info}")
        
        # Test financial statements
        print("📊 Fetching AAPL financial statements...")
        financials = await connector.get_financial_statements('AAPL')
        print(f"✅ Successfully fetched financial statements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Yahoo Finance: {e}")
        return False

async def test_data_manager():
    """Test the data manager."""
    print("\n🔧 Testing Data Manager...")
    
    try:
        manager = FinancialDataManager()
        
        # Check available connectors
        connectors = manager.get_available_connectors()
        print(f"✅ Available connectors: {connectors}")
        
        # Check connector health
        health = manager.get_connector_health()
        print("🏥 Connector Health Status:")
        for name, status in health.items():
            print(f"   {name}: {status['status']}")
        
        # Test multi-source data
        print("\n📊 Testing multi-source data for AAPL...")
        multi_data = await manager.get_multi_source_data('AAPL')
        print(f"✅ Successfully fetched data from {len(multi_data['sources'])} sources")
        
        for source, data in multi_data['sources'].items():
            if 'error' not in data:
                print(f"   {source}: {len(data)} data types available")
            else:
                print(f"   {source}: Error - {data['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Data Manager: {e}")
        return False

async def test_stock_analysis():
    """Test comprehensive stock analysis."""
    print("\n📈 Testing Stock Analysis...")
    
    try:
        manager = FinancialDataManager()
        
        # Get comprehensive stock data
        symbol = 'AAPL'
        print(f"🔍 Analyzing {symbol}...")
        
        # Get price data
        price_data = await manager.get_stock_data(symbol, 'price', period='6mo')
        print(f"✅ Price data: {len(price_data)} records")
        
        # Calculate basic statistics
        if not price_data.empty:
            latest_price = price_data.iloc[-1]['Close']
            price_change = ((latest_price - price_data.iloc[0]['Close']) / price_data.iloc[0]['Close']) * 100
            volatility = price_data['Close'].pct_change().std() * 100
            
            print(f"   Current Price: ${latest_price:.2f}")
            print(f"   6-Month Change: {price_change:.2f}%")
            print(f"   Volatility: {volatility:.2f}%")
        
        # Get company info
        try:
            company_info = await manager.get_stock_data(symbol, 'info')
            if isinstance(company_info, dict):
                print(f"   Company: {company_info.get('longName', 'N/A')}")
                print(f"   Market Cap: ${company_info.get('marketCap', 0):,}")
        except Exception as e:
            print(f"   Company info: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing stock analysis: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Financial Research Intelligence - Data Integration Test")
    print("=" * 60)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Test individual components
    yf_success = await test_yahoo_finance()
    dm_success = await test_data_manager()
    analysis_success = await test_stock_analysis()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Yahoo Finance Connector: {'✅ PASS' if yf_success else '❌ FAIL'}")
    print(f"   Data Manager: {'✅ PASS' if dm_success else '❌ FAIL'}")
    print(f"   Stock Analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    
    if all([yf_success, dm_success, analysis_success]):
        print("\n🎉 All tests passed! Data integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs for details.")
    
    print("\n📁 Data files and logs are saved in:")
    print("   - logs/ (log files)")
    print("   - data/sec_edgar/ (SEC filings, if downloaded)")

if __name__ == "__main__":
    asyncio.run(main()) 
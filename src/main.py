"""
Main entry point for the Financial Research Intelligence application.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data.data_manager import FinancialDataManager
from src.config.settings import settings

async def analyze_stock(symbol: str, analysis_type: str = 'comprehensive'):
    """
    Analyze a stock using the data integration system.
    
    Args:
        symbol: Stock symbol to analyze
        analysis_type: Type of analysis ('basic', 'comprehensive', 'technical')
    """
    print(f"🔍 Analyzing {symbol.upper()}...")
    
    try:
        manager = FinancialDataManager()
        
        if analysis_type == 'basic':
            # Basic price and info analysis
            price_data = await manager.get_stock_data(symbol, 'price', period='1mo')
            company_info = await manager.get_stock_data(symbol, 'info')
            
            print(f"📈 {symbol.upper()} Analysis Results:")
            print(f"   Current Price: ${price_data.iloc[-1]['Close']:.2f}")
            print(f"   Company: {company_info.get('longName', 'N/A')}")
            print(f"   Market Cap: ${company_info.get('marketCap', 0):,}")
            
        elif analysis_type == 'comprehensive':
            # Comprehensive multi-source analysis
            multi_data = await manager.get_multi_source_data(symbol)
            
            print(f"📊 {symbol.upper()} Comprehensive Analysis:")
            print(f"   Data Sources: {list(multi_data['sources'].keys())}")
            
            # Validate cross-source data
            validation = await manager.validate_cross_source_data(symbol)
            if 'price_consistency' in validation['validations']:
                price_check = validation['validations']['price_consistency']
                if 'is_consistent' in price_check:
                    print(f"   Price Consistency: {'✅' if price_check['is_consistent'] else '❌'}")
            
        elif analysis_type == 'technical':
            # Technical analysis
            price_data = await manager.get_stock_data(symbol, 'price', period='6mo')
            
            # Calculate basic technical indicators
            price_data['SMA_20'] = price_data['Close'].rolling(window=20).mean()
            price_data['SMA_50'] = price_data['Close'].rolling(window=50).mean()
            price_data['Volatility'] = price_data['Close'].pct_change().rolling(window=20).std() * 100
            
            latest = price_data.iloc[-1]
            print(f"📈 {symbol.upper()} Technical Analysis:")
            print(f"   Current Price: ${latest['Close']:.2f}")
            print(f"   20-Day SMA: ${latest['SMA_20']:.2f}")
            print(f"   50-Day SMA: ${latest['SMA_50']:.2f}")
            print(f"   20-Day Volatility: {latest['Volatility']:.2f}%")
            
            # Trend analysis
            if latest['SMA_20'] > latest['SMA_50']:
                print("   Trend: 📈 Bullish (20-day SMA above 50-day SMA)")
            else:
                print("   Trend: 📉 Bearish (20-day SMA below 50-day SMA)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {e}")
        return False

async def health_check():
    """Check the health of all data connectors."""
    print("🏥 Checking System Health...")
    
    try:
        manager = FinancialDataManager()
        
        # Check available connectors
        connectors = manager.get_available_connectors()
        print(f"✅ Available Connectors: {connectors}")
        
        # Check health status
        health = manager.get_connector_health()
        print("\n📊 Health Status:")
        for name, status in health.items():
            emoji = "✅" if status['status'] == 'healthy' else "❌"
            print(f"   {emoji} {name}: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def demo():
    """Run a demonstration of the system capabilities."""
    print("🚀 Financial Research Intelligence - Demo")
    print("=" * 50)
    
    # Health check
    await health_check()
    
    print("\n" + "=" * 50)
    
    # Analyze multiple stocks
    stocks = ['AAPL', 'MSFT', 'GOOGL']
    
    for stock in stocks:
        print(f"\n📊 Analyzing {stock}...")
        await analyze_stock(stock, 'basic')
        await asyncio.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Research Intelligence & Investment Analysis Generator"
    )
    
    parser.add_argument(
        '--symbol', '-s',
        type=str,
        help='Stock symbol to analyze (e.g., AAPL)'
    )
    
    parser.add_argument(
        '--analysis', '-a',
        type=str,
        choices=['basic', 'comprehensive', 'technical'],
        default='basic',
        help='Type of analysis to perform'
    )
    
    parser.add_argument(
        '--health', '-H',
        action='store_true',
        help='Check system health'
    )
    
    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help='Run demonstration'
    )
    
    args = parser.parse_args()
    
    if args.health:
        asyncio.run(health_check())
    elif args.demo:
        asyncio.run(demo())
    elif args.symbol:
        asyncio.run(analyze_stock(args.symbol, args.analysis))
    else:
        print("Financial Research Intelligence & Investment Analysis Generator")
        print("=" * 60)
        print("Usage:")
        print("  python -m src.main --symbol AAPL --analysis comprehensive")
        print("  python -m src.main --health")
        print("  python -m src.main --demo")
        print("\nFor more information, run: python -m src.main --help")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Run Fast Cosmetic SEO App - Optimized version
"""

import uvicorn
import asyncio
import sys
import os
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup optimized logging"""
    logger.remove()  # Remove default handler
    
    # Console logging (reduced verbosity)
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File logging (errors only for performance)
    logger.add(
        "logs/fast_app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="7 days"
    )

async def startup_checks():
    """Perform startup checks"""
    print("🚀 FAST COSMETIC SEO SYSTEM")
    print("=" * 50)
    
    # Check data directories
    os.makedirs("data/web_results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("✅ Directories created")
    
    # Test fast workflow
    try:
        from fast_workflow import FastWorkflow
        workflow = FastWorkflow()
        print("✅ Fast workflow initialized")
    except Exception as e:
        print(f"❌ Fast workflow error: {e}")
        return False
    
    # Test web app
    try:
        from web_app import CosmeticSEOWebSystem
        system = CosmeticSEOWebSystem()
        print("✅ Web system initialized")
    except Exception as e:
        print(f"❌ Web system error: {e}")
        return False
    
    print("✅ All systems ready!")
    return True

def main():
    """Main entry point"""
    setup_logging()
    
    # Run startup checks
    startup_success = asyncio.run(startup_checks())
    
    if not startup_success:
        print("❌ Startup failed!")
        sys.exit(1)
    
    print("\n🌐 Starting web server...")
    print("📊 Performance Features:")
    print("   - ⚡ Sub-10 second processing")
    print("   - 🚀 Parallel URL discovery")
    print("   - 🧠 Smart caching system")
    print("   - 🎯 API-first scraping")
    print("   - 📈 Real-time metrics")
    
    print("\n🔗 Access URLs:")
    print("   - Main App: http://localhost:8000") 
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    
    # Start server with optimized settings
    try:
        uvicorn.run(
            "web_app:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable for performance
            access_log=False,  # Disable for performance
            workers=1,  # Single worker for simplicity
            loop="asyncio"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
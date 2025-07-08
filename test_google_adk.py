#!/usr/bin/env python3
"""
Test Google ADK installation and basic functionality
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

print("🧪 Testing Google ADK Installation")
print("=" * 50)

# Load environment
load_dotenv()

try:
    print("1. Testing Google ADK import...")
    import google.adk
    print("   ✅ google.adk imported successfully")
    
    print("\n2. Testing Google ADK version...")
    print(f"   ✅ Google ADK version: {getattr(google.adk, '__version__', 'unknown')}")
    
    print("\n3. Testing basic Agent import...")
    from google.adk.agents import Agent
    print("   ✅ Agent class imported successfully")
    
    print("\n4. Testing LlmAgent import...")
    from google.adk.agents import LlmAgent
    print("   ✅ LlmAgent class imported successfully")
    
    print("\n5. Testing Google Generative AI...")
    import google.generativeai as genai
    print("   ✅ Google Generative AI imported successfully")
    
    print("\n6. Checking environment variables...")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        print(f"   ✅ GOOGLE_API_KEY found: {google_api_key[:10]}...")
    else:
        print("   ⚠️ GOOGLE_API_KEY not found")
    
    print("\n7. Testing simple agent creation...")
    
    # Simple agent test
    class TestAgent(LlmAgent):
        def __init__(self):
            super().__init__(
                name="test_agent",
                description="Test agent for Google ADK"
            )
    
    test_agent = TestAgent()
    print("   ✅ Test agent created successfully")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Google ADK system is ready for full deployment")
    
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    print("\n💡 Try installing with: pip install google-adk")
    sys.exit(1)
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n🚀 Ready to run full Cosmetic SEO Extraction System!")
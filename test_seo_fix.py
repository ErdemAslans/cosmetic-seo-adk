#!/usr/bin/env python3
"""
Test script to verify the SEO agent temperature parameter fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_seo_agent_fix():
    """Test if the temperature parameter has been removed from SEOAgent"""
    try:
        # Read the SEO agent file
        with open('agents/seo_agent.py', 'r') as f:
            content = f.read()
        
        # Check for temperature parameter
        if 'temperature=' in content:
            print("❌ FAIL: Temperature parameter still present in seo_agent.py")
            # Show the lines containing temperature
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'temperature=' in line:
                    print(f"   Line {i+1}: {line.strip()}")
            return False
        else:
            print("✅ PASS: Temperature parameter successfully removed from seo_agent.py")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_gemini_model_update():
    """Test if Gemini model has been updated to 2.0-flash-exp"""
    try:
        with open('agents/seo_agent.py', 'r') as f:
            content = f.read()
        
        if 'gemini-2.0-flash-exp' in content:
            print("✅ PASS: Gemini model updated to 2.0-flash-exp")
            return True
        else:
            print("❌ FAIL: Gemini model not found or not updated")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing SEO Agent fixes...")
    print("=" * 50)
    
    success1 = test_seo_agent_fix()
    success2 = test_gemini_model_update()
    
    print("=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! SEO Agent is ready.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)
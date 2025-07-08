#!/usr/bin/env python3
"""
Test that all agent updates work correctly with the new LlmAgent constructor
"""

import asyncio
import sys

# Test imports
try:
    from agents.scout_agent import create_scout_agent
    from agents.scraper_agent import create_scraper_agent
    from agents.analyzer_agent import create_analyzer_agent
    from agents.seo_agent import create_seo_agent
    from agents.quality_agent import create_quality_agent
    from agents.storage_agent import create_storage_agent
    
    print("✅ All agent imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test agent instantiation
try:
    print("\n🧪 Testing agent instantiation...")
    
    scout = create_scout_agent()
    print("✅ Scout Agent created")
    
    scraper = create_scraper_agent()
    print("✅ Scraper Agent created")
    
    analyzer = create_analyzer_agent()
    print("✅ Analyzer Agent created")
    
    seo = create_seo_agent()
    print("✅ SEO Agent created")
    
    quality = create_quality_agent()
    print("✅ Quality Agent created")
    
    # Storage agent needs database URL
    storage = create_storage_agent("postgresql://test:test@localhost/test", "data")
    print("✅ Storage Agent created")
    
    print("\n🎉 All agents instantiated successfully!")
    print("✅ LlmAgent constructor updates completed successfully")
    
except Exception as e:
    print(f"❌ Error creating agents: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test that agents have correct attributes
try:
    print("\n🔍 Verifying agent configurations...")
    
    agents = [
        ("Scout", scout),
        ("Scraper", scraper),
        ("Analyzer", analyzer),
        ("SEO", seo),
        ("Quality", quality),
        ("Storage", storage)
    ]
    
    for agent_name, agent in agents:
        # Check required attributes
        assert hasattr(agent, 'name'), f"{agent_name} missing 'name' attribute"
        assert hasattr(agent, 'model'), f"{agent_name} missing 'model' attribute"
        assert hasattr(agent, 'tools'), f"{agent_name} missing 'tools' attribute"
        assert hasattr(agent, 'instruction'), f"{agent_name} missing 'instruction' attribute"
        
        # Verify no old attributes
        assert not hasattr(agent, 'system_instructions'), f"{agent_name} still has old 'system_instructions' attribute"
        assert not hasattr(agent, 'memory'), f"{agent_name} still has old 'memory' attribute"
        
        print(f"✅ {agent_name} Agent configuration verified")
    
    print("\n✅ All agent configurations are correct!")
    
except AssertionError as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🚀 All tests passed! Agent updates are complete and working correctly.")
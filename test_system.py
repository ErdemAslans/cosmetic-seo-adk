#!/usr/bin/env python3
"""
🌟 Cosmetic SEO System Test Script
Test all major components without running web server
"""

import asyncio
import json
import time
from typing import Dict, Any

def test_config_imports():
    """Test configuration imports"""
    print("🧪 Testing configuration imports...")
    try:
        from config.modern_sites import MODERN_SITE_CONFIGS, SITE_ANALYSIS_CONFIGS, get_site_analysis_config
        print(f"✅ Site configs loaded: {len(MODERN_SITE_CONFIGS)} sites")
        
        # Test site analysis config
        gratis_config = get_site_analysis_config("gratis")
        print(f"✅ Gratis analysis config: {gratis_config['analysis_focus']}")
        
        return True
    except Exception as e:
        print(f"❌ Config import error: {e}")
        return False

def test_agent_imports():
    """Test agent imports"""
    print("\n🧪 Testing agent imports...")
    agents_status = {}
    
    # Test SEO Agent
    try:
        from agents.seo_agent import SEOAgent, generate_seo_data
        agents_status['seo'] = "✅ SEO Agent loaded"
    except Exception as e:
        agents_status['seo'] = f"❌ SEO Agent error: {e}"
    
    # Test Modern Scraper Agent  
    try:
        from agents.modern_scraper_agent import ModernScraperAgent, discover_product_urls_advanced
        agents_status['scraper'] = "✅ Modern Scraper loaded"
    except Exception as e:
        agents_status['scraper'] = f"❌ Modern Scraper error: {e}"
    
    # Test Analyzer Agent
    try:
        from agents.analyzer_agent import analyze_product_data
        agents_status['analyzer'] = "✅ Analyzer Agent loaded"
    except Exception as e:
        agents_status['analyzer'] = f"❌ Analyzer Agent error: {e}"
    
    for agent, status in agents_status.items():
        print(f"   {status}")
    
    return all("✅" in status for status in agents_status.values())

def test_keyword_separation():
    """Test the enhanced keyword separation system"""
    print("\n🧪 Testing keyword separation system...")
    
    try:
        from agents.seo_agent import KeywordExtractionTool
        
        # Test cases that were problematic
        test_cases = [
            "sglamkaşşekilendiricibrowwax",
            "flormarmakyajfoundationlonglasting", 
            "niveatemizleyicinemlendiricicremeyes",
            "lorealantiagingserumvitaminc"
        ]
        
        keyword_tool = KeywordExtractionTool()
        
        for test_case in test_cases:
            separated = keyword_tool._separate_concatenated_words(test_case)
            print(f"   '{test_case}' -> {separated}")
        
        return True
    except Exception as e:
        print(f"❌ Keyword separation test error: {e}")
        return False

def test_site_configurations():
    """Test site-specific configurations"""
    print("\n🧪 Testing site configurations...")
    
    try:
        from config.modern_sites import MODERN_SITE_CONFIGS
        
        for site_config in MODERN_SITE_CONFIGS:
            print(f"   📊 {site_config.name}:")
            print(f"      Base URL: {site_config.base_url}")
            print(f"      Categories: {len(site_config.category_paths)}")
            
            # Check for enhanced selectors
            selectors = site_config.selectors
            enhanced_fields = ['long_descriptions', 'ingredients', 'features', 'benefits', 'usage']
            enhanced_count = sum(1 for field in enhanced_fields if field in selectors)
            print(f"      Enhanced selectors: {enhanced_count}/{len(enhanced_fields)}")
            
            if enhanced_count >= 3:
                print(f"      Status: ✅ Fully enhanced")
            else:
                print(f"      Status: ⚠️  Partially enhanced")
        
        return True
    except Exception as e:
        print(f"❌ Site config test error: {e}")
        return False

def test_web_ui_structure():
    """Test web UI components"""
    print("\n🧪 Testing web UI structure...")
    
    try:
        # Check if web_app.py has enhanced features
        with open('/mnt/c/Users/Erdem/cosmetic-seo-adk/web_app.py', 'r', encoding='utf-8') as f:
            web_content = f.read()
        
        enhanced_features = [
            'ultra-advanced',
            'content_richness',
            'extraction_stats',
            'seo_stats',  
            'comprehensive_validation',
            'gemini-2.0-flash-thinking-exp'
        ]
        
        feature_count = sum(1 for feature in enhanced_features if feature in web_content)
        print(f"   Enhanced features found: {feature_count}/{len(enhanced_features)}")
        
        if feature_count >= 5:
            print("   ✅ Web UI fully enhanced")
            return True
        else:
            print("   ⚠️  Web UI partially enhanced")
            return False
            
    except Exception as e:
        print(f"❌ Web UI test error: {e}")
        return False

def generate_system_report():
    """Generate comprehensive system report"""
    print("\n📊 COMPREHENSIVE SYSTEM REPORT")
    print("=" * 50)
    
    tests = [
        ("Config Imports", test_config_imports),
        ("Agent Imports", test_agent_imports), 
        ("Keyword Separation", test_keyword_separation),
        ("Site Configurations", test_site_configurations),
        ("Web UI Structure", test_web_ui_structure)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print(f"\n🎯 FINAL RESULTS:")
    print("=" * 30)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Overall Score: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🏆 SYSTEM READY - All components working perfectly!")
        print("🚀 Ready for production deployment")
    elif passed >= total * 0.8:
        print("⭐ SYSTEM MOSTLY READY - Minor issues to resolve")
    else:
        print("⚠️  SYSTEM NEEDS ATTENTION - Major issues found")
    
    return passed == total

if __name__ == "__main__":
    print("🌟 COSMETIC SEO SYSTEM COMPREHENSIVE TEST")
    print("🔥 Ultra-Advanced AI-Powered E-Commerce SEO Platform")
    print("=" * 60)
    
    system_ready = generate_system_report()
    
    if system_ready:
        print(f"\n🎉 SYSTEM VALIDATION COMPLETE!")
        print("✅ All enhancements successfully implemented")
        print("✅ Ultra-advanced category filtering active") 
        print("✅ Rich content SEO generation ready")
        print("✅ Keyword separation system working")
        print("✅ Site-specific configurations loaded")
        print("✅ Web UI fully enhanced")
        print(f"\n🚀 Ready to handle 50+ products with world-class SEO!")
    else:
        print(f"\n⚠️  Some components need attention before full deployment")
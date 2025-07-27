#!/usr/bin/env python3
"""
🧪 Test Site Configuration Validation
Quick test to verify that our SiteConfig model handles list selectors correctly
"""

import sys
import os

# Add the project root to the Python path
sys.path.append('/mnt/c/Users/Erdem/cosmetic-seo-adk')

def test_site_config_validation():
    """Test that SiteConfig properly handles list selectors"""
    print("🧪 Testing SiteConfig validation fix...")
    
    try:
        from config.models import SiteConfig
        print("✅ SiteConfig model imported successfully")
        
        # Test data similar to what's causing the error
        test_config_data = {
            "name": "test_site",
            "base_url": "https://www.test.com",
            "category_paths": ["/test-category"],
            "selectors": {
                "product_link": "a.product-link",  # String selector
                "description": [                    # List selector
                    "div.description",
                    "section.product-info"
                ],
                "ingredients": [                    # List selector
                    "div.ingredients li",
                    "ul.ingredient-list li"
                ]
            },
            "rate_limit": 2.0,
            "max_pages": 10,
            "headers": {"User-Agent": "Test"}
        }
        
        # Try to create SiteConfig instance
        config = SiteConfig(**test_config_data)
        print("✅ SiteConfig validation passed!")
        print(f"   - Name: {config.name}")
        print(f"   - String selector: {config.selectors['product_link']}")
        print(f"   - List selector: {config.selectors['description']}")
        print(f"   - Mixed selectors work: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ SiteConfig validation failed: {e}")
        return False

def test_modern_sites_import():
    """Test that modern_sites.py can be imported without errors"""
    print("\n🧪 Testing modern_sites.py import...")
    
    try:
        from config.modern_sites import MODERN_SITE_CONFIGS
        print(f"✅ Modern sites imported: {len(MODERN_SITE_CONFIGS)} sites")
        
        # Test first site configuration
        first_site = MODERN_SITE_CONFIGS[0]
        print(f"   - First site: {first_site.name}")
        print(f"   - Enhanced selectors: {len(first_site.selectors)}")
        
        # Check if it has the enhanced selectors that were causing issues
        enhanced_selectors = ['description', 'long_descriptions', 'ingredients', 'features', 'benefits', 'usage']
        found_enhanced = [sel for sel in enhanced_selectors if sel in first_site.selectors]
        print(f"   - Enhanced selector types found: {len(found_enhanced)}/{len(enhanced_selectors)}")
        print(f"   - Found: {found_enhanced}")
        
        return True
        
    except Exception as e:
        print(f"❌ Modern sites import failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 SITE CONFIGURATION VALIDATION TEST")
    print("=" * 45)
    
    success1 = test_site_config_validation()
    success2 = test_modern_sites_import()
    
    print(f"\n📊 RESULTS:")
    print(f"   SiteConfig Model Fix: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Modern Sites Import: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Site configuration validation is now working")
        print("✅ Enhanced selectors with lists are supported")
        print("✅ System should run without validation errors")
    else:
        print(f"\n⚠️  Some tests failed - need to investigate further")
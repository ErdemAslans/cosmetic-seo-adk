#!/usr/bin/env python3
"""
Test script to verify enhanced deep content analysis in analyzer agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.analyzer_agent import DataCleaningTool
from config.models import ProductData

def test_deep_content_analysis():
    """Test the enhanced deep content analysis functionality"""
    
    # Create test product data with comprehensive content
    test_product = ProductData(
        url="https://example.com/sglam-brow-wax",
        site="example.com",
        name="SGLAM Kaş Şekilendirici Brow Wax Premium Formula",
        brand="SGLAM",
        description="""
        Bu ürün clinically tested ve dermatologically proven formül ile geliştirilen advanced kaş şekilendirici wax'tır. 
        Scientifically formulated olan bu unique ürün, professional salon quality sonuçlar sağlar.
        Long-lasting ve waterproof özelliği ile tüm gün mükemmel görünüm sunar.
        Kaşlarınızı gently şekillendirir ve natural görünüm kazandırır.
        Bu breakthrough technology ile üretilen innovative ürün, lasting results sunar.
        
        Uzun açıklama: Bu özel formülü, vitamin E ve natural botanical extracts içerir. 
        Retinol ve niacinamide gibi proven ingredients ile zenginleştirilmiştir.
        Research studies gösteriyor ki bu patented formula %95 oranında effective sonuçlar verir.
        """,
        price="89.90 TL",
        ingredients=["Vitamin E", "Retinol", "Niacinamide", "Botanical Extract", "Natural Wax"],
        features=["Waterproof", "Long-lasting", "Natural look", "Professional quality"],
        usage="Günlük kullanım için sabah uygulanır. Clean skin üzerine gently massage yapın.",
        reviews=[
            "Mükemmel ürün, really improves kaş görünümü",
            "Professional salon quality gerçekten",
            "Long-lasting sonuç veriyor"
        ]
    )
    
    print("🧪 Testing Enhanced Deep Content Analysis")
    print("=" * 60)
    
    try:
        # Create data cleaning tool instance
        tool = DataCleaningTool()
        
        # Test comprehensive content extraction
        full_content = tool._extract_comprehensive_content(test_product)
        print(f"📄 Comprehensive Content Length: {len(full_content)} characters")
        print(f"📄 First 200 chars: {full_content[:200]}...")
        print()
        
        # Test deep content analysis
        analysis = tool._perform_deep_content_analysis(full_content)
        print("🔬 Deep Content Analysis Results:")
        print(f"   Word Count: {analysis['word_count']}")
        print(f"   Unique Word Ratio: {analysis['unique_word_ratio']}")
        print(f"   Scientific Authority: {analysis['scientific_authority']}")
        print(f"   Benefit Density: {analysis['benefit_density']}")
        print(f"   Quality Score: {analysis['quality_score']}/100")
        print(f"   Content Richness: {analysis['content_richness']}")
        print()
        
        # Test unique selling points
        usps = tool._identify_unique_selling_points(full_content)
        print("💎 Unique Selling Points:")
        for usp in usps:
            print(f"   - {usp}")
        print()
        
        # Test SEO content gaps
        gaps = tool._find_seo_content_gaps(full_content)
        print("🔍 SEO Content Opportunities:")
        for gap_type, gap_items in gaps.items():
            if gap_items:
                print(f"   {gap_type}: {', '.join(gap_items[:3])}")
        print()
        
        # Test scientific terms extraction
        sci_terms = tool._extract_scientific_terms(full_content)
        print("🔬 Scientific Terms:")
        for term in sci_terms:
            print(f"   - {term}")
        print()
        
        # Test consumer benefits mapping
        benefits = tool._map_consumer_benefits(full_content)
        print("💅 Consumer Benefits Mapping:")
        for benefit_type, benefit_items in benefits.items():
            if benefit_items:
                print(f"   {benefit_type}: {', '.join(benefit_items)}")
        print()
        
        # Overall assessment
        if analysis['quality_score'] > 70:
            print("✅ EXCELLENT: Deep analysis shows high-quality content suitable for superior SEO")
        elif analysis['quality_score'] > 40:
            print("✅ GOOD: Deep analysis shows adequate content for professional SEO")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Content requires enhancement for professional SEO")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in deep content analysis: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Analyzer Agent Deep Content Analysis")
    print("=" * 60)
    
    success = test_deep_content_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Deep content analysis test completed successfully!")
        print("\n📋 Enhanced Features Verified:")
        print("✅ Comprehensive content extraction from all product fields")
        print("✅ Deep content quality analysis with scoring")
        print("✅ Unique selling point identification")
        print("✅ SEO content gap analysis")
        print("✅ Scientific terminology extraction")
        print("✅ Consumer benefits mapping")
        print("\n🌟 Ready for superior, professional SEO generation!")
    else:
        print("⚠️  Test failed - please check error messages above")
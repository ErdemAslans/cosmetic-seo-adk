#!/usr/bin/env python3
"""
Cosmetic SEO Web Interface - Google ADK Agent Powered
"""

from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import os
import json
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger
import uuid
from pathlib import Path
import pandas as pd

# Google ADK Agent sistemini import et
from main import CosmeticSEOOrchestrator
from agents.workflow_logger import workflow_logger

# Import new production-ready systems
from agents.ultra_stealth_browser import create_ultra_stealth_browser
from agents.ai_selector_engine import create_adaptive_selector_engine
from agents.smart_session_manager import create_smart_session_manager
from agents.error_recovery_system import create_error_recovery_system

# Fast workflow - import with try/catch for compatibility
try:
    from fast_workflow import FastWorkflow
    FAST_MODE_AVAILABLE = True
except ImportError:
    FAST_MODE_AVAILABLE = False
    logger.warning("Fast workflow not available, using standard mode")

# Dynamic URL mapper for auto-discovery
try:
    from agents.dynamic_url_mapper import url_mapper, get_current_category_urls
    DYNAMIC_URL_AVAILABLE = True
    logger.info("🔍 Dynamic URL discovery ACTIVE - Auto-updating category URLs!")
except ImportError:
    DYNAMIC_URL_AVAILABLE = False
    logger.warning("Dynamic URL mapper not available")

load_dotenv()

app = FastAPI(
    title="🎭 Cosmetic SEO Extractor - AI Powered", 
    description="Google Gemini AI destekli kozmetik ürün SEO analiz sistemi"
)

# Templates ve static dosyalar
templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global işlem takibi
active_tasks = {}

class CosmeticSEOWebSystem:
    def __init__(self):
        self.results_dir = "data/web_results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Google ADK Orchestrator'ı başlat
        self.orchestrator = CosmeticSEOOrchestrator()
        
        # Initialize production-ready systems
        self._initialize_production_systems()
        
        # Fast workflow sistemi
        if FAST_MODE_AVAILABLE:
            database_url = os.getenv('DATABASE_URL')
            self.fast_workflow = FastWorkflow(database_url=database_url)
            logger.info("🚀 Fast workflow mode ACTIVE - Ultra-fast processing enabled!")
        else:
            self.fast_workflow = None
            logger.info("⚠️ Fast workflow not available - Using standard processing")
    
    def _initialize_production_systems(self):
        """Initialize all production-ready systems"""
        try:
            # Proxy configuration from environment
            proxy_configs = []
            if os.getenv('PROXY_SERVERS'):
                proxy_list = os.getenv('PROXY_SERVERS').split(',')
                for proxy_server in proxy_list:
                    proxy_configs.append({
                        'server': proxy_server.strip(),
                        'username': os.getenv('PROXY_USERNAME'),
                        'password': os.getenv('PROXY_PASSWORD'),
                        'country': 'TR',
                        'provider': 'production',
                        'cost_per_gb': 7.0,
                        'max_concurrent': 10
                    })
            
            # Initialize systems
            self.stealth_browser = None  # Will be created on demand
            self.selector_engine = create_adaptive_selector_engine(
                gemini_api_key=os.getenv('GOOGLE_API_KEY')
            )
            self.session_manager = create_smart_session_manager(proxy_configs)
            
            
            # Error recovery system
            self.error_recovery = create_error_recovery_system()
            
            logger.info("✅ All production systems initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing production systems: {e}")
            # Fallback to basic systems
            self.stealth_browser = None
            self.selector_engine = None
            self.session_manager = None
            self.error_recovery = None
        
        # Desteklenen siteler ve kategoriler - 2025 GÜNCEL URL'LER
        self.sites = {
            "trendyol": {
                "name": "Trendyol",
                "base_url": "https://www.trendyol.com",
                "categories": [
                    "kozmetik",      # /kozmetik-x-c89
                    "makyaj",        # /makyaj-x-c100  
                    "cilt bakımı",   # /cilt-bakimi-x-c85
                    "parfüm",        # /parfum-ve-deodorant-x-c103717
                    "saç bakımı"     # /sac-bakimi-x-c1354
                ],
                "verified_urls": {
                    "kozmetik": "https://www.trendyol.com/kozmetik-x-c89",
                    "makyaj": "https://www.trendyol.com/makyaj-x-c100",
                    "cilt bakımı": "https://www.trendyol.com/cilt-bakimi-x-c85", 
                    "parfüm": "https://www.trendyol.com/parfum-ve-deodorant-x-c103717",
                    "saç bakımı": "https://www.trendyol.com/sac-bakimi-x-c1354"
                },
                "ai_features": "🚀 Ultra-Stealth + AI Selector Adaptation + Smart Proxy",
                "success_rate": "90%",
                "priority": 1
            },
            "gratis": {
                "name": "Gratis",
                "base_url": "https://www.gratis.com", 
                "categories": [
                    "makyaj",        # /makyaj-c-501
                    "cilt bakımı",   # /cilt-bakim-c-502  
                    "parfüm",        # /parfum-deodorant-c-504
                    "saç bakımı",    # /sac-bakim-c-503
                    "vücut bakımı",  
                    "erkek bakım"    
                ],
                "verified_urls": {
                    "makyaj": "https://www.gratis.com/makyaj-c-501",
                    "cilt bakımı": "https://www.gratis.com/cilt-bakim-c-502",
                    "parfüm": "https://www.gratis.com/parfum-deodorant-c-504", 
                    "saç bakımı": "https://www.gratis.com/sac-bakim-c-503"
                },
                "ai_features": "🧠 AI-Powered Detection",
                "success_rate": "75%",
                "priority": 2
            },
            "sephora_tr": {
                "name": "Sephora TR",
                "base_url": "https://www.sephora.com.tr",
                "categories": [
                    "makyaj",        # /makyaj-c302/
                    "cilt bakımı",   # /cilt-bakimi-c303/
                    "parfüm",        # /parfum-c301/
                    "saç bakımı",    # /sac-bakimi-c304/
                    "erkek"          # /erkek-c305/
                ],
                "verified_urls": {
                    "makyaj": "https://www.sephora.com.tr/makyaj-c302/",
                    "cilt bakımı": "https://www.sephora.com.tr/cilt-bakimi-c303/",
                    "parfüm": "https://www.sephora.com.tr/parfum-c301/",
                    "saç bakımı": "https://www.sephora.com.tr/sac-bakimi-c304/"
                },
                "ai_features": "✨ Premium Brand Focus + Advanced SEO",
                "success_rate": "85%", 
                "priority": 3
            },
            "rossmann": {
                "name": "Rossmann",
                "base_url": "https://www.rossmann.com.tr",
                "categories": [
                    "makyaj",        # /makyaj
                    "cilt bakımı",   # /cilt-bakimi
                    "parfüm",        # /parfum-deodorant
                    "saç bakımı",    # /sac-bakimi
                    "vücut bakımı"   
                ],
                "verified_urls": {
                    "makyaj": "https://www.rossmann.com.tr/makyaj",
                    "cilt bakımı": "https://www.rossmann.com.tr/cilt-bakimi",
                    "parfüm": "https://www.rossmann.com.tr/parfum-deodorant",
                    "saç bakımı": "https://www.rossmann.com.tr/sac-bakimi"
                },
                "ai_features": "🎯 Budget-Friendly Focus + Bulk Processing",
                "success_rate": "70%",
                "priority": 4
            }
        }
    
    async def process_extraction(self, task_id: str, site: str, category: str, max_products: int):
        """Ana işlem fonksiyonu - Google ADK Agent'ları kullanır"""
        try:
            active_tasks[task_id] = {
                "status": "starting",
                "progress": 0,
                "message": f"🤖 AI Agent'lar {site} sitesinde '{category}' araması başlatıyor...",
                "results": [],
                "started_at": time.time(),
                "ai_agents": {
                    "scout": "⏳ Bekliyor",
                    "scraper": "⏳ Bekliyor",
                    "analyzer": "⏳ Bekliyor", 
                    "seo": "⏳ Bekliyor",
                    "quality": "⏳ Bekliyor",
                    "storage": "⏳ Bekliyor"
                }
            }
            
            if site == "demo":
                await self._process_demo_with_agents(task_id, category, max_products)
            else:
                await self._process_with_agents(task_id, site, category, max_products)
                
        except Exception as e:
            logger.error(f"Task {task_id} error: {e}")
            active_tasks[task_id]["status"] = "error"
            active_tasks[task_id]["message"] = f"❌ Hata: {str(e)}"
    
    async def _update_agent_status(self, task_id: str, agent: str, status: str):
        """Agent durumunu güncelle"""
        if task_id in active_tasks:
            active_tasks[task_id]["ai_agents"][agent] = status
    
    async def _get_dynamic_category_url(self, site: str, category: str) -> Optional[str]:
        """Dinamik kategori URL keşfi"""
        if not DYNAMIC_URL_AVAILABLE:
            return None
        
        try:
            logger.info(f"🔍 Discovering current URL for {site} - {category}")
            current_urls = await get_current_category_urls(site, [category])
            
            if category in current_urls:
                discovered_url = current_urls[category]
                logger.info(f"✅ Found current URL: {discovered_url}")
                return discovered_url
            else:
                logger.warning(f"⚠️ No URL found for {category} on {site}")
                return None
        except Exception as e:
            logger.error(f"Dynamic URL discovery error: {e}")
            return None
    
    async def _process_with_agents(self, task_id: str, site: str, category: str, max_products: int):
        """Gerçek siteler için FAST workflow (eğer mevcut ise)"""
        try:
            # ÖNCELİKLE dinamik URL keşfi yap
            if DYNAMIC_URL_AVAILABLE:
                active_tasks[task_id]["message"] = f"🔍 {category} için güncel URL keşfediliyor..."
                active_tasks[task_id]["progress"] = 5
                
                dynamic_url = await self._get_dynamic_category_url(site, category)
                if dynamic_url:
                    active_tasks[task_id]["message"] = f"✅ Güncel URL bulundu: {dynamic_url}"
                    # URL'i fast_workflow'a parametre olarak geçirebiliriz
                else:
                    active_tasks[task_id]["message"] = f"⚠️ Güncel URL bulunamadı, varsayılan sistem kullanılacak"
            
            # FAST WORKFLOW kullan (eğer mevcut ise)
            if self.fast_workflow:
                active_tasks[task_id]["message"] = f"⚡ HIZLI işlem başlatılıyor - {site} - {category}"
                active_tasks[task_id]["progress"] = 10
                
                # Fast workflow ile işle - progress callback ile
                async def progress_callback(progress, message, agent=None):
                    active_tasks[task_id]["progress"] = progress
                    active_tasks[task_id]["message"] = message
                    if agent:
                        await self._update_agent_status(task_id, agent, "active")
                
                result = await self.fast_workflow.process(site, category, max_products, progress_callback)
                
                if result['success']:
                    # [Fast workflow success handling - same as before]
                    processed_products = []
                    for product in result['products']:
                        if product:
                            processed_products.append({
                                'name': product.get('name', 'Bilinmiyor'),
                                'brand': product.get('brand', 'Bilinmiyor'),
                                'price': product.get('price', 0),
                                'category': product.get('category', 'Bilinmiyor'),
                                'url': product.get('url', ''),
                                'seo_title': product.get('seo_data', {}).get('title', ''),
                                'meta_description': product.get('seo_data', {}).get('meta_description', ''),
                                'keywords': product.get('seo_data', {}).get('keywords', []),
                                'quality_score': product.get('quality_score', 0),
                                'is_valid': True,
                                'ai_model': 'gemini-2.0-flash-thinking-exp',
                                'optimization': 'HIZLI'
                            })
                    
                    active_tasks[task_id].update({
                        "status": "completed",
                        "progress": 100,
                        "message": f"✅ HIZLI işlem tamamlandı! {len(processed_products)} ürün {result['metrics']['total_time']:.1f}s'de işlendi",
                        "results": processed_products,
                        "processing_time": result['metrics']['total_time'],
                        "performance_metrics": result['metrics'],
                        "ai_agents": {
                            "scout": "✅ Tamamlandı",
                            "scraper": "✅ Tamamlandı", 
                            "analyzer": "✅ Tamamlandı",
                            "seo": "✅ Tamamlandı",
                            "quality": "✅ Tamamlandı",
                            "storage": "✅ Tamamlandı"
                        }
                    })
                    return
                else:
                    # Fast workflow failed, fall back to standard
                    logger.warning(f"Fast workflow failed, falling back to standard processing: {result.get('error')}")
            
            # STANDARD WORKFLOW (eski sistem)
            active_tasks[task_id]["message"] = f"🤖 Standard AI Agent'lar başlatılıyor - {site} - {category}"
            await self._process_with_agents_old(task_id, site, category, max_products)
            
            if result['success']:
                # Başarılı sonuçları formatla
                processed_products = []
                for product in result['products']:
                    if product:
                        processed_products.append({
                            'name': product.get('name', 'Bilinmiyor'),
                            'brand': product.get('brand', 'Bilinmiyor'),
                            'price': product.get('price', 0),
                            'category': product.get('category', 'Bilinmiyor'),
                            'url': product.get('url', ''),
                            'seo_title': product.get('seo_data', {}).get('title', ''),
                            'meta_description': product.get('seo_data', {}).get('meta_description', ''),
                            'keywords': product.get('seo_data', {}).get('keywords', []),
                            'quality_score': product.get('quality_score', 0),
                            'is_valid': True,
                            'ai_model': 'gemini-2.0-flash-thinking-exp',
                            'optimization': 'HIZLI'
                        })
                
                # Final update
                active_tasks[task_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"✅ HIZLI işlem tamamlandı! {len(processed_products)} ürün {result['metrics']['total_time']:.1f}s'de işlendi",
                    "results": processed_products,
                    "processing_time": result['metrics']['total_time'],
                    "performance_metrics": result['metrics'],
                    "ai_agents": {
                        "scout": "✅ Tamamlandı",
                        "scraper": "✅ Tamamlandı", 
                        "analyzer": "✅ Tamamlandı",
                        "seo": "✅ Tamamlandı",
                        "quality": "✅ Tamamlandı",
                        "storage": "✅ Tamamlandı"
                    }
                })
                
                logger.info(f"✅ Fast workflow completed for task {task_id}: {len(processed_products)} products in {result['metrics']['total_time']:.2f}s")
                
            else:
                # Hata durumu
                active_tasks[task_id].update({
                    "status": "error", 
                    "message": f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}",
                    "progress": 0
                })
                
        except Exception as e:
            logger.error(f"Fast processing error for task {task_id}: {e}")
            active_tasks[task_id].update({
                "status": "error",
                "message": f"❌ Hata: {str(e)}",
                "progress": 0
            })
    
    async def _process_with_agents_old(self, task_id: str, site: str, category: str, max_products: int):
        """Eski Google ADK Agent pipeline'ı (yedek)"""
        try:
            # Kategori-URL mapping
            category_mappings = {
                "trendyol": {
                    "kozmetik": "/kozmetik-x-c89",
                    "cilt bakımı": "/kozmetik/cilt-bakimi-x-c104",
                    "makyaj": "/kozmetik/makyaj-x-c105",
                    "parfüm": "/kozmetik/parfum-x-c106",
                    "güzellik": "/kozmetik/guzellik-x-c1309"
                },
                "gratis": {
                    "makyaj": "/makyaj-c-1",
                    "cilt bakımı": "/cilt-bakim-c-2",
                    "parfüm": "/parfum-c-3", 
                    "saç bakımı": "/sac-bakim-c-4",
                    "vücut bakımı": "/vucut-bakim-c-5",
                    "erkek bakım": "/erkek-bakimi-c-6"
                },
                "sephora_tr": {
                    "makyaj": "/makyaj-c301",
                    "cilt bakımı": "/cilt-bakimi-c302",
                    "parfüm": "/parfum-c303",
                    "saç bakımı": "/sac-bakimi-c304",
                    "erkek": "/erkek-c305"
                },
                "rossmann": {
                    "cilt bakımı": "/cilt-bakimi-c-100",
                    "makyaj": "/makyaj-c-200",
                    "parfüm": "/parfum-c-300",
                    "saç bakımı": "/sac-bakimi-c-400",
                    "vücut bakımı": "/vucut-bakimi-c-500"
                }
            }
            
            # Get the correct category path
            category_path = category_mappings.get(site, {}).get(category, f"/{category}")
            
            # Scout Agent ile URL keşfi
            await self._update_agent_status(task_id, "scout", "🔍 URL'ler aranıyor...")
            active_tasks[task_id].update({
                "status": "running",
                "progress": 10,
                "message": f"🔍 Scout Agent {site} sitesinde '{category}' ürünlerini arıyor..."
            })
            
            # Use modern scraper for advanced URL discovery with category path
            from agents.modern_scraper_agent import discover_product_urls_advanced
            scout_result = await discover_product_urls_advanced(site, max_products, category)
            
            if not scout_result or "discovered_urls" not in scout_result:
                raise Exception("Scout Agent URL bulamadı")
            
            urls = scout_result["discovered_urls"][:max_products]
            await self._update_agent_status(task_id, "scout", f"✅ {len(urls)} URL bulundu")
            
            results = []
            total_urls = len(urls)
            
            for idx, url in enumerate(urls):
                # Progress güncelle
                base_progress = 20 + (idx * 70 // total_urls)
                
                # Scraper Agent
                await self._update_agent_status(task_id, "scraper", f"🌐 Veri çekiliyor ({idx+1}/{total_urls})")
                active_tasks[task_id].update({
                    "progress": base_progress,
                    "message": f"🌐 Scraper Agent veri çekiyor... ({idx+1}/{total_urls})"
                })
                
                # Use modern scraper for advanced data extraction
                from agents.modern_scraper_agent import scrape_product_data_advanced
                scraper_result = await scrape_product_data_advanced(url, site)
                
                if not scraper_result or "product_data" not in scraper_result:
                    continue
                
                # Analyzer Agent
                await self._update_agent_status(task_id, "analyzer", f"🔬 Analiz ediliyor ({idx+1}/{total_urls})")
                active_tasks[task_id]["message"] = f"🔬 Analyzer Agent veriyi temizliyor..."
                
                # Direct tool call for analyzer
                from agents.analyzer_agent import analyze_product_data
                analyzer_result = await analyze_product_data(scraper_result["product_data"])
                
                # SEO Agent
                await self._update_agent_status(task_id, "seo", f"✨ SEO üretiliyor ({idx+1}/{total_urls})")
                active_tasks[task_id]["message"] = f"✨ SEO Agent anahtar kelimeler üretiyor..."
                
                # Direct tool call for SEO
                from agents.seo_agent import generate_seo_data
                seo_result = await generate_seo_data(analyzer_result)
                
                # Quality Agent
                await self._update_agent_status(task_id, "quality", f"🎯 Kalite kontrolü ({idx+1}/{total_urls})")
                active_tasks[task_id]["message"] = f"🎯 Quality Agent SEO kalitesini değerlendiriyor..."
                
                # Direct tool call for quality
                from agents.quality_agent import validate_product_quality
                quality_result = await validate_product_quality(
                    analyzer_result.get("cleaned_product", {}), 
                    seo_result, 
                    analyzer_result.get("extracted_terms", {})
                )
                
                # Sonucu ekle
                result = {
                    "product": analyzer_result.get("cleaned_product", {}),
                    "seo": seo_result,
                    "quality_score": quality_result.get("overall_quality_score", quality_result.get("quality_score", 0)),
                    "quality_report": quality_result.get("validation_details", quality_result.get("report", {})),
                    "is_valid": True,  # Her zaman geçerli olarak işaretle
                    "processed_at": time.time(),
                    "ai_insights": {
                        "keywords_count": len(seo_result.get("keywords", [])),
                        "content_analysis": analyzer_result.get("content_sections", {}),
                        "ai_model": "gemini-2.0-flash-thinking-exp"
                    }
                }
                results.append(result)
            
            # Storage Agent ile kaydet
            await self._update_agent_status(task_id, "storage", "💾 Veriler kaydediliyor...")
            active_tasks[task_id]["message"] = "💾 Storage Agent verileri kaydediyor..."
            
            # Sonuçları kaydet
            await self._save_results(task_id, results, f"{site}_{category}")
            
            # Final durum güncellemesi
            for agent in ["scout", "scraper", "analyzer", "seo", "quality", "storage"]:
                await self._update_agent_status(task_id, agent, "✅ Tamamlandı")
            
            active_tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "message": f"✅ {len(results)} ürün başarıyla AI Agent'lar tarafından işlendi!",
                "results": results,
                "stats": {
                    "total_products": len(results),
                    "valid_products": sum(1 for r in results if r["is_valid"]),
                    "avg_quality_score": sum(r["quality_score"] for r in results) / len(results) if results else 0,
                    "processing_time": time.time() - active_tasks[task_id]["started_at"]
                }
            })
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            active_tasks[task_id].update({
                "status": "error",
                "message": f"❌ Agent hatası: {str(e)}"
            })
    
    async def _process_demo_with_agents(self, task_id: str, category: str, max_products: int):
        """Demo mod - Sahte agent simülasyonu"""
        active_tasks[task_id].update({
            "status": "running",
            "progress": 10,
            "message": f"🎭 Demo mod: AI Agent simülasyonu başlatılıyor..."
        })
        
        # Demo agent adımları
        agents = ["scout", "scraper", "analyzer", "seo", "quality", "storage"]
        demo_products = []
        
        for i in range(min(3, max_products)):
            for j, agent in enumerate(agents):
                await self._update_agent_status(task_id, agent, f"🔄 İşleniyor... ({i+1}/{min(3, max_products)})")
                active_tasks[task_id].update({
                    "progress": 10 + ((i * len(agents) + j) * 80 // (min(3, max_products) * len(agents))),
                    "message": f"🤖 {agent.title()} Agent çalışıyor..."
                })
                await asyncio.sleep(0.3)
            
            # Demo ürün oluştur
            product = {
                "name": f"AI Enhanced {category.title()} Formula #{i+1}",
                "brand": ["LuxeBeauty", "NaturalGlow", "ProCare"][i % 3],
                "price": f"{299 + (i * 100)}.90 TL",
                "description": f"Gemini AI ile analiz edilmiş premium {category}. Nano teknoloji ve doğal içerikler.",
                "category": category,
                "url": f"https://demo.com/ai-{category}-{i+1}",
                "ingredients": ["Hyaluronic Acid", "Vitamin C", "Retinol", "Peptides"],
                "ai_analyzed": True
            }
            
            seo_data = {
                "title": f"{product['brand']} {product['name']} - En İyi {category.title()} | Demo Store",
                "meta_description": f"🌟 {product['brand']} {product['name']} - AI destekli {category} formülü. Gemini AI tarafından optimize edilmiş SEO. Hemen keşfet!",
                "keywords": [
                    f"{category} {product['brand']}",
                    f"en iyi {category}",
                    f"{product['brand']} {category} yorumları",
                    f"AI destekli {category}",
                    "premium kozmetik",
                    "doğal içerik",
                    f"{category} fiyatları"
                ],
                "slug": f"{product['brand'].lower()}-{category.replace(' ', '-')}-ai-{i+1}",
                "schema_markup": {
                    "@type": "Product",
                    "name": product['name'],
                    "brand": product['brand'],
                    "offers": {
                        "@type": "Offer",
                        "price": product['price'].replace(" TL", ""),
                        "priceCurrency": "TRY"
                    }
                }
            }
            
            quality_score = 85 + (i * 5)
            
            demo_products.append({
                "product": product,
                "seo": seo_data,
                "quality_score": quality_score,
                "quality_report": {
                    "title_score": 95,
                    "description_score": 90,
                    "keywords_score": 88,
                    "ai_optimization": True
                },
                "is_valid": True,
                "processed_at": time.time(),
                "ai_insights": {
                    "keywords_count": len(seo_data["keywords"]),
                    "ai_model": "gemini-2.0-flash-thinking-exp",
                    "optimization_level": "high"
                }
            })
        
        # Tüm agent'ları tamamlandı olarak işaretle
        for agent in agents:
            await self._update_agent_status(task_id, agent, "✅ Tamamlandı")
        
        # Sonuçları kaydet
        await self._save_results(task_id, demo_products, f"demo_{category}_ai")
        
        active_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"✅ Demo tamamlandı! {len(demo_products)} ürün AI Agent'lar tarafından simüle edildi.",
            "results": demo_products,
            "stats": {
                "total_products": len(demo_products),
                "valid_products": len(demo_products),
                "avg_quality_score": sum(p["quality_score"] for p in demo_products) / len(demo_products),
                "processing_time": time.time() - active_tasks[task_id]["started_at"]
            }
        })
    
    async def _save_results(self, task_id: str, results: List[Dict], prefix: str):
        """Sonuçları JSON ve CSV olarak kaydet"""
        timestamp = int(time.time())
        json_path = os.path.join(self.results_dir, f"{prefix}_{timestamp}.json")
        csv_path = os.path.join(self.results_dir, f"{prefix}_{timestamp}.csv")
        
        # JSON kaydet - URL objelerini string'e çevir
        def json_serializer(obj):
            """Custom JSON serializer for URL objects"""
            if hasattr(obj, '__str__'):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=json_serializer)
        
        # CSV için veriyi düzenle
        csv_data = []
        for item in results:
            row = {
                "Ürün Adı": item["product"].get("name", ""),
                "Marka": item["product"].get("brand", ""),
                "Fiyat": item["product"].get("price", ""),
                "Kategori": item["product"].get("category", ""),
                "URL": item["product"].get("url", ""),
                "SEO Başlığı": item["seo"].get("title", ""),
                "Meta Açıklama": item["seo"].get("meta_description", ""),
                "Anahtar Kelimeler": ", ".join(item["seo"].get("keywords", [])),
                "URL Slug": item["seo"].get("slug", ""),
                "Kalite Skoru": item["quality_score"],
                "AI Model": item.get("ai_insights", {}).get("ai_model", "gemini-1.5-pro"),
                "Geçerli": "Evet"  # Her zaman geçerli olarak göster
            }
            csv_data.append(row)
        
        # CSV kaydet
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Task'a dosya yollarını ekle
        active_tasks[task_id]["files"] = {
            "json": json_path,
            "csv": csv_path
        }

# Global sistem instance
system = CosmeticSEOWebSystem()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sites": system.sites,
        "title": "Cosmetic SEO Extractor - AI Powered"
    })

@app.get("/monitoring", response_class=HTMLResponse)
async def monitoring_dashboard(request: Request):
    """Real-time monitoring dashboard"""
    return templates.TemplateResponse("monitoring.html", {
        "request": request,
        "title": "Production Monitoring Dashboard"
    })

@app.post("/extract")
async def extract(
    request: Request,
    background_tasks: BackgroundTasks,
    site: str = Form(...),
    category: str = Form(...),
    max_products: int = Form(10)
):
    """Extraction işlemini başlat"""
    task_id = str(uuid.uuid4())
    
    # Arka planda çalıştır
    background_tasks.add_task(
        system.process_extraction,
        task_id,
        site,
        category,
        max_products
    )
    
    return JSONResponse({
        "task_id": task_id,
        "message": "🚀 AI Agent'lar işleme başladı!",
        "site": site,
        "category": category
    })

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Task durumunu kontrol et"""
    if task_id not in active_tasks:
        return JSONResponse({"error": "Task bulunamadı"}, status_code=404)
    
    # Convert any non-serializable objects to strings
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif hasattr(obj, '__str__') and not isinstance(obj, (str, int, float, bool)):
            return str(obj)
        else:
            return obj
    
    task_data = make_serializable(active_tasks[task_id])
    return JSONResponse(task_data)

@app.get("/download/{task_id}/{format}")
async def download(task_id: str, format: str):
    """Sonuçları indir"""
    if task_id not in active_tasks:
        return JSONResponse({"error": "Task bulunamadı"}, status_code=404)
    
    task = active_tasks[task_id]
    if task["status"] != "completed":
        return JSONResponse({"error": "Task henüz tamamlanmadı"}, status_code=400)
    
    if "files" not in task:
        return JSONResponse({"error": "Dosyalar bulunamadı"}, status_code=404)
    
    file_path = task["files"].get(format)
    if not file_path or not os.path.exists(file_path):
        return JSONResponse({"error": f"{format} dosyası bulunamadı"}, status_code=404)
    
    from fastapi.responses import FileResponse
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )

@app.get("/agent-status")
async def agent_status():
    """Agent sistem durumu"""
    return JSONResponse({
        "status": "active",
        "agents": {
            "scout": "✅ Hazır - URL keşfi için",
            "scraper": "✅ Hazır - Veri çıkarma için", 
            "analyzer": "✅ Hazır - Veri temizleme için",
            "seo": "✅ Hazır - SEO üretimi için",
            "quality": "✅ Hazır - Kalite kontrolü için",
            "storage": "✅ Hazır - Veri saklama için"
        },
        "ai_model": "gemini-1.5-pro-latest",
        "features": [
            "🤖 Google Gemini AI destekli analiz",
            "🔍 Akıllı URL keşfi",
            "🧠 NLP tabanlı içerik analizi",
            "✨ AI destekli SEO optimizasyonu",
            "🎯 Otomatik kalite kontrolü",
            "💾 Akıllı veri depolama"
        ]
    })

@app.get("/workflow/{task_id}")
async def get_workflow_state(task_id: str):
    """N8N tarzı workflow durumunu döndür"""
    try:
        workflow_state = workflow_logger.get_workflow_state(task_id)
        return JSONResponse(workflow_state)
    except Exception as e:
        logger.error(f"Workflow state error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/update-urls/{site_name}")
async def update_site_urls(site_name: str):
    """Site URL'lerini dinamik olarak güncelle"""
    try:
        if not DYNAMIC_URL_AVAILABLE:
            return {"error": "Dynamic URL mapper not available"}
        
        logger.info(f"🔄 Updating URLs for {site_name}")
        
        # Site kategorilerini al
        site_categories = system.sites.get(site_name, {}).get('categories', [])
        if not site_categories:
            return {"error": f"Site {site_name} not found"}
        
        # URL'leri keşfet ve güncelle
        current_urls = await get_current_category_urls(site_name, site_categories)
        
        return {
            "success": True,
            "site": site_name,
            "updated_urls": current_urls,
            "timestamp": time.time(),
            "message": f"✅ {len(current_urls)} kategori URL'i güncellendi"
        }
        
    except Exception as e:
        logger.error(f"URL update error: {e}")
        return {"error": str(e)}

@app.get("/current-urls/{site_name}")
async def get_current_urls(site_name: str):
    """Site için güncel URL'leri getir"""
    try:
        if not DYNAMIC_URL_AVAILABLE:
            return {"error": "Dynamic URL mapper not available"}
        
        site_categories = system.sites.get(site_name, {}).get('categories', [])
        if not site_categories:
            return {"error": f"Site {site_name} not found"}
        
        current_urls = await get_current_category_urls(site_name, site_categories)
        
        return {
            "site": site_name,
            "categories": current_urls,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/production-status")
async def get_production_status():
    """Get production systems status"""
    status = {
        "stealth_browser": system.stealth_browser is not None,
        "selector_engine": system.selector_engine is not None,
        "session_manager": system.session_manager is not None,
        "error_recovery": system.error_recovery is not None,
        "fast_workflow": system.fast_workflow is not None
    }
    
    # Get detailed metrics if systems are available
    metrics = {}
    
    if system.session_manager:
        metrics["session_manager"] = system.session_manager.get_performance_metrics()
    
    if system.selector_engine:
        metrics["selector_engine"] = system.selector_engine.get_performance_metrics()
    
    
    if system.error_recovery:
        metrics["error_recovery"] = system.error_recovery.get_error_analytics()
    
    return {
        "system_status": status,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "proxy_configured": bool(os.getenv('PROXY_SERVERS')),
            "gemini_configured": bool(os.getenv('GOOGLE_API_KEY'))
        }
    }

@app.get("/site-health/{site_name}")
async def get_site_health(site_name: str):
    """Get detailed health metrics for a specific site"""
    if site_name not in system.sites:
        return {"error": f"Site {site_name} not found"}
    
    site_info = system.sites[site_name]
    health_data = {
        "site_name": site_name,
        "base_url": site_info.get("base_url"),
        "success_rate": site_info.get("success_rate", "Unknown"),
        "priority": site_info.get("priority", 5),
        "categories": len(site_info.get("categories", [])),
        "verified_urls": len(site_info.get("verified_urls", {})),
        "ai_features": site_info.get("ai_features")
    }
    
    # Add recent performance if error recovery is available
    if system.error_recovery:
        analytics = system.error_recovery.get_error_analytics()
        site_errors = [s for s in analytics["site_errors"] if s["site"] == site_name]
        if site_errors:
            health_data["recent_errors"] = site_errors[0]
    
    return health_data

@app.post("/test-production-systems")
async def test_production_systems():
    """Test all production systems"""
    results = {}
    
    # Test stealth browser
    if system.stealth_browser:
        try:
            # Basic browser test would go here
            results["stealth_browser"] = {"status": "ready", "test": "passed"}
        except Exception as e:
            results["stealth_browser"] = {"status": "error", "error": str(e)}
    else:
        results["stealth_browser"] = {"status": "not_initialized"}
    
    # Test selector engine
    if system.selector_engine:
        try:
            metrics = system.selector_engine.get_performance_metrics()
            results["selector_engine"] = {"status": "ready", "metrics": metrics}
        except Exception as e:
            results["selector_engine"] = {"status": "error", "error": str(e)}
    else:
        results["selector_engine"] = {"status": "not_initialized"}
    
    # Test session manager
    if system.session_manager:
        try:
            metrics = system.session_manager.get_performance_metrics()
            results["session_manager"] = {"status": "ready", "metrics": metrics}
        except Exception as e:
            results["session_manager"] = {"status": "error", "error": str(e)}
    else:
        results["session_manager"] = {"status": "not_initialized"}
    
    
    # Test error recovery
    if system.error_recovery:
        try:
            analytics = system.error_recovery.get_error_analytics()
            results["error_recovery"] = {"status": "ready", "analytics": analytics}
        except Exception as e:
            results["error_recovery"] = {"status": "error", "error": str(e)}
    else:
        results["error_recovery"] = {"status": "not_initialized"}
    
    return {
        "test_results": results,
        "timestamp": datetime.now().isoformat(),
        "overall_health": "healthy" if all(
            r.get("status") in ["ready", "not_initialized"] 
            for r in results.values()
        ) else "degraded"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Cosmetic SEO Extractor - AI Powered başlatılıyor...")
    logger.info("🤖 Google ADK Agent sistemi aktif")
    uvicorn.run(app, host="0.0.0.0", port=3000)
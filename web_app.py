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
        
        # Desteklenen siteler ve kategoriler
        self.sites = {
            "trendyol": {
                "name": "Trendyol",
                "categories": [
                    "kozmetik", "makyaj", "cilt bakımı", "parfüm",
                    "yüz kremi", "serum", "ruj", "maskara", "fondöten"
                ],
                "ai_features": "🤖 AI ile gelişmiş ürün analizi"
            },
            "gratis": {
                "name": "Gratis",
                "categories": [
                    "makyaj", "cilt bakımı", "saç bakımı", "parfüm",
                    "ruj", "krem", "şampuan", "maske", "oje"
                ],
                "ai_features": "🧠 Akıllı kategori tespiti"
            },
            "sephora_tr": {
                "name": "Sephora TR",
                "categories": [
                    "makyaj", "cilt bakımı", "parfüm", "saç bakımı",
                    "foundation", "serum", "mascara", "lipstick"
                ],
                "ai_features": "✨ Premium ürün SEO optimizasyonu"
            },
            "rossmann": {
                "name": "Rossmann",
                "categories": [
                    "yüz bakımı", "vücut bakımı", "saç bakımı", "makyaj",
                    "bebek bakımı", "erkek bakımı", "güneş ürünleri"
                ],
                "ai_features": "🎯 Hedef kitle odaklı SEO"
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
    
    async def _process_with_agents(self, task_id: str, site: str, category: str, max_products: int):
        """Gerçek siteler için Google ADK Agent pipeline'ı"""
        try:
            # Scout Agent ile URL keşfi
            await self._update_agent_status(task_id, "scout", "🔍 URL'ler aranıyor...")
            active_tasks[task_id].update({
                "status": "running",
                "progress": 10,
                "message": f"🔍 Scout Agent {site} sitesinde '{category}' ürünlerini arıyor..."
            })
            
            # Use modern scraper for advanced URL discovery
            from agents.modern_scraper_agent import discover_product_urls_advanced
            scout_result = await discover_product_urls_advanced(site, max_products)
            
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
                    "is_valid": quality_result.get("is_valid", False),
                    "processed_at": time.time(),
                    "ai_insights": {
                        "keywords_count": len(seo_result.get("keywords", [])),
                        "content_analysis": analyzer_result.get("content_sections", {}),
                        "ai_model": "gemini-1.5-pro"
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
                    "ai_model": "gemini-1.5-pro-demo",
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
                "Geçerli": "Evet" if item["is_valid"] else "Hayır"
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

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Cosmetic SEO Extractor - AI Powered başlatılıyor...")
    logger.info("🤖 Google ADK Agent sistemi aktif")
    uvicorn.run(app, host="0.0.0.0", port=3000)
#!/usr/bin/env python3
"""
Cosmetic SEO Web Interface - Kullanıcı Dostu Arayüz
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

# Scraper'ları import et
from real_scraper import RossmannScraper, SimpleSEOGenerator
from gratis_scraper import GratisScraper

load_dotenv()

app = FastAPI(title="🎭 Cosmetic SEO Extractor", description="Kozmetik ürünlerinden SEO bilgilerini çıkarın")

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
        
        # Desteklenen siteler ve kategoriler
        self.sites = {
            "rossmann": {
                "name": "Rossmann",
                "categories": [
                    "yüz kremi", "güneş kremi", "nemlendirici", "serum", 
                    "makyaj", "ruj", "maskara", "fondöten", "concealer",
                    "göz kremi", "temizleyici", "tonik", "peeling", "maske"
                ]
            },
            "gratis": {
                "name": "Gratis",
                "categories": [
                    "yüz kremi", "güneş kremi", "nemlendirici", "serum",
                    "makyaj", "ruj", "maskara", "fondöten", "concealer", 
                    "göz kremi", "temizleyici", "tonik", "peeling", "maske",
                    "anti-aging", "vitamin c", "retinol", "hyaluronic acid"
                ]
            },
            "demo": {
                "name": "Demo Test (Hızlı)",
                "categories": [
                    "serum", "krem", "maske", "vitamin", "bakım"
                ]
            }
        }
    
    async def process_request(self, task_id: str, site: str, category: str, max_products: int = 20):
        """Ana işlem fonksiyonu"""
        try:
            active_tasks[task_id] = {
                "status": "starting",
                "progress": 0,
                "message": f"{site} sitesinde '{category}' araması başlatılıyor...",
                "results": [],
                "started_at": time.time()
            }
            
            if site == "demo":
                await self._process_demo(task_id, category, max_products)
            elif site == "rossmann":
                await self._process_rossmann(task_id, category, max_products)
            elif site == "gratis":
                await self._process_gratis(task_id, category, max_products)
            else:
                active_tasks[task_id]["status"] = "error"
                active_tasks[task_id]["message"] = f"{site} henüz desteklenmiyor"
                
        except Exception as e:
            logger.error(f"Task {task_id} error: {e}")
            active_tasks[task_id]["status"] = "error"
            active_tasks[task_id]["message"] = f"Hata: {str(e)}"
    
    async def _process_demo(self, task_id: str, category: str, max_products: int):
        """Demo işleme"""
        active_tasks[task_id].update({
            "status": "running",
            "progress": 10,
            "message": f"Demo veriler oluşturuluyor: {category}"
        })
        
        # Demo ürünler
        demo_products = [
            {
                "name": f"Premium {category.title()} - Anti-Aging Formula",
                "brand": "BeautyLab",
                "price": "299.90 TL",
                "description": f"Yeni nesil {category} formülü. Premium ingredients ile zenginleştirilmiş.",
                "category": category,
                "url": f"https://demo.com/{category}-1"
            },
            {
                "name": f"Natural {category.title()} with Vitamin C",
                "brand": "GreenBeauty",
                "price": "189.90 TL", 
                "description": f"Doğal içerikli {category}. Vitamin C ve E kompleksi içerir.",
                "category": category,
                "url": f"https://demo.com/{category}-2"
            },
            {
                "name": f"Professional {category.title()} Solution",
                "brand": "ProCare",
                "price": "449.90 TL",
                "description": f"Profesyonel kalitede {category}. Dermatolog tavsiyeli formül.",
                "category": category,
                "url": f"https://demo.com/{category}-3"
            }
        ]
        
        seo_generator = SimpleSEOGenerator()
        results = []
        
        for i, product in enumerate(demo_products[:max_products]):
            active_tasks[task_id].update({
                "progress": 30 + (i * 50 // len(demo_products)),
                "message": f"İşleniyor: {product['name'][:30]}..."
            })
            
            # SEO verisi üret
            seo_data = seo_generator.generate_seo(product)
            quality_score = 85 + (i * 5)  # Demo için sabit skorlar
            
            result = {
                "product": product,
                "seo": seo_data,
                "quality_score": quality_score,
                "is_valid": True,
                "processed_at": time.time()
            }
            results.append(result)
            
            await asyncio.sleep(0.5)  # Demo için hız
        
        # Sonuçları kaydet
        await self._save_results(task_id, results, f"demo_{category}")
        
        active_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"✅ {len(results)} ürün başarıyla işlendi",
            "results": results
        })
    
    async def _process_rossmann(self, task_id: str, category: str, max_products: int):
        """Rossmann gerçek işleme"""
        active_tasks[task_id].update({
            "status": "running", 
            "progress": 10,
            "message": f"Rossmann'da '{category}' aranıyor..."
        })
        
        seo_generator = SimpleSEOGenerator()
        results = []
        
        async with RossmannScraper() as scraper:
            # URL'leri keşfet
            active_tasks[task_id].update({
                "progress": 20,
                "message": "Ürün URL'leri keşfediliyor..."
            })
            
            urls = await scraper.discover_product_urls(category, max_products)
            
            if not urls:
                active_tasks[task_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"⚠️ '{category}' için ürün bulunamadı",
                    "results": []
                })
                return
            
            active_tasks[task_id].update({
                "progress": 30,
                "message": f"{len(urls)} ürün bulundu, işleniyor..."
            })
            
            # Her ürünü işle
            for i, url in enumerate(urls):
                progress = 30 + (i * 60 // len(urls))
                active_tasks[task_id].update({
                    "progress": progress,
                    "message": f"İşleniyor {i+1}/{len(urls)}: {url.split('/')[-1][:30]}..."
                })
                
                try:
                    # Ürün verisini çek
                    product = await scraper.scrape_product(url)
                    
                    if "error" not in product:
                        # SEO verisi üret
                        seo_data = seo_generator.generate_seo(product)
                        quality_score = self._calculate_quality_score(product, seo_data)
                        
                        result = {
                            "product": product,
                            "seo": seo_data,
                            "quality_score": quality_score,
                            "is_valid": quality_score >= 70,
                            "processed_at": time.time()
                        }
                        results.append(result)
                
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    continue
                
                await asyncio.sleep(2)  # Rate limiting
        
        # Sonuçları kaydet
        await self._save_results(task_id, results, f"rossmann_{category}")
        
        valid_count = sum(1 for r in results if r["is_valid"])
        active_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"✅ {len(results)} ürün işlendi, {valid_count} geçerli",
            "results": results
        })
    
    async def _process_gratis(self, task_id: str, category: str, max_products: int):
        """Gratis gerçek işleme"""
        active_tasks[task_id].update({
            "status": "running", 
            "progress": 10,
            "message": f"Gratis'ta '{category}' aranıyor..."
        })
        
        seo_generator = SimpleSEOGenerator()
        results = []
        
        async with GratisScraper() as scraper:
            # URL'leri keşfet
            active_tasks[task_id].update({
                "progress": 20,
                "message": "Gratis'ta ürün URL'leri keşfediliyor..."
            })
            
            urls = await scraper.discover_product_urls(category, max_products)
            
            if not urls:
                active_tasks[task_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"⚠️ Gratis'ta '{category}' için ürün bulunamadı",
                    "results": []
                })
                return
            
            active_tasks[task_id].update({
                "progress": 30,
                "message": f"Gratis'ta {len(urls)} ürün bulundu, işleniyor..."
            })
            
            # Her ürünü işle
            for i, url in enumerate(urls):
                progress = 30 + (i * 60 // len(urls))
                active_tasks[task_id].update({
                    "progress": progress,
                    "message": f"Gratis ürün işleniyor {i+1}/{len(urls)}: {url.split('/')[-1][:30]}..."
                })
                
                try:
                    # Ürün verisini çek
                    product = await scraper.scrape_product(url)
                    
                    if "error" not in product:
                        # SEO verisi üret
                        seo_data = seo_generator.generate_seo(product)
                        quality_score = self._calculate_quality_score(product, seo_data)
                        
                        result = {
                            "product": product,
                            "seo": seo_data,
                            "quality_score": quality_score,
                            "is_valid": quality_score >= 70,
                            "processed_at": time.time()
                        }
                        results.append(result)
                
                except Exception as e:
                    logger.error(f"Error processing Gratis {url}: {e}")
                    continue
                
                await asyncio.sleep(2)  # Rate limiting
        
        # Sonuçları kaydet
        await self._save_results(task_id, results, f"gratis_{category}")
        
        valid_count = sum(1 for r in results if r["is_valid"])
        active_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"✅ Gratis'tan {len(results)} ürün işlendi, {valid_count} geçerli",
            "results": results
        })
    
    def _calculate_quality_score(self, product: Dict[str, Any], seo_data: Dict[str, Any]) -> int:
        """Kalite skoru hesapla"""
        score = 100
        
        if not product.get("name"):
            score -= 30
        if not product.get("price"):
            score -= 10
        if not product.get("description") or len(product.get("description", "")) < 50:
            score -= 20
        if not product.get("brand"):
            score -= 10
        
        keywords = seo_data.get("keywords", [])
        if len(keywords) < 3:
            score -= 15
        if len(seo_data.get("title", "")) > 60:
            score -= 5
        if len(seo_data.get("meta_description", "")) > 160:
            score -= 5
        
        return max(0, score)
    
    async def _save_results(self, task_id: str, results: List[Dict], filename_prefix: str):
        """Sonuçları kaydet"""
        timestamp = int(time.time())
        
        # JSON kaydet
        json_file = f"{self.results_dir}/{filename_prefix}_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # CSV kaydet
        csv_file = f"{self.results_dir}/{filename_prefix}_{timestamp}.csv"
        import csv
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            if results:
                writer = csv.writer(f)
                writer.writerow([
                    "product_name", "brand", "price", "primary_keyword", 
                    "keywords_count", "quality_score", "is_valid", "url"
                ])
                
                for result in results:
                    product = result["product"]
                    seo = result["seo"]
                    writer.writerow([
                        product.get("name", ""),
                        product.get("brand", ""),
                        product.get("price", ""),
                        seo.get("primary_keyword", ""),
                        len(seo.get("keywords", [])),
                        result.get("quality_score", 0),
                        result.get("is_valid", False),
                        product.get("url", "")
                    ])

# Global instance
seo_system = CosmeticSEOWebSystem()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Ana sayfa"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sites": seo_system.sites
    })

@app.post("/extract")
async def start_extraction(
    background_tasks: BackgroundTasks,
    site: str = Form(...),
    category: str = Form(...),
    max_products: int = Form(20)
):
    """SEO çıkarımını başlat"""
    task_id = str(uuid.uuid4())
    
    # Background task başlat
    background_tasks.add_task(
        seo_system.process_request, 
        task_id, site, category, max_products
    )
    
    return JSONResponse({
        "task_id": task_id,
        "message": f"İşlem başlatıldı: {site} - {category}",
        "estimated_time": f"{max_products * 2} saniye"
    })

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """İşlem durumunu getir"""
    if task_id not in active_tasks:
        return JSONResponse({"error": "Task bulunamadı"}, status_code=404)
    
    return JSONResponse(active_tasks[task_id])

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """Sonuçları getir"""
    if task_id not in active_tasks:
        return JSONResponse({"error": "Task bulunamadı"}, status_code=404)
    
    task = active_tasks[task_id]
    if task["status"] != "completed":
        return JSONResponse({"error": "İşlem henüz tamamlanmadı"}, status_code=400)
    
    return JSONResponse({
        "task_id": task_id,
        "total_products": len(task["results"]),
        "valid_products": sum(1 for r in task["results"] if r["is_valid"]),
        "results": task["results"]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
#!/usr/bin/env python3
"""
Simple Web App - Optimized version without heavy dependencies
"""

from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import asyncio
import os
import json
import time
from typing import Dict, Any
import uuid

# Import scraper
from agents.modern_scraper_agent import ModernScraperAgent

app = FastAPI(
    title="🚀 Fast Cosmetic SEO Extractor", 
    description="Optimized cosmetic product SEO analysis - sub-10 second processing"
)

# Templates
templates = Jinja2Templates(directory="templates")
os.makedirs("templates", exist_ok=True)
os.makedirs("data/web_results", exist_ok=True)

# Global state
active_tasks = {}

class SimpleCosmeticSEOSystem:
    """Simple system without heavy dependencies"""
    
    def __init__(self):
        self.sites = {
            "trendyol": {
                "name": "Trendyol",
                "categories": ["kozmetik", "parfüm", "makyaj", "cilt bakımı"],
                "features": "⚡ Ultra-fast processing"
            },
            "gratis": {
                "name": "Gratis", 
                "categories": ["makyaj", "cilt bakımı", "parfüm", "saç bakımı"],
                "features": "🚀 API-first scraping"
            }
        }
    
    async def process_extraction(self, task_id: str, site: str, category: str, max_products: int):
        """Fast processing without heavy dependencies"""
        try:
            active_tasks[task_id] = {
                "status": "processing",
                "progress": 10,
                "message": f"⚡ FAST processing started - {site} - {category}",
                "results": [],
                "started_at": time.time()
            }
            
            # Update progress
            active_tasks[task_id]["progress"] = 30
            active_tasks[task_id]["message"] = "🔍 Discovering products..."
            
            # Process with modern scraper agent
            scraper = ModernScraperAgent()
            result = await scraper.discover_and_scrape(site, category, max_products)
            await scraper.close()
            
            if result['success']:
                # Format results
                processed_products = []
                for product in result['products']:
                    processed_products.append({
                        'name': product.get('name', 'Unknown'),
                        'brand': product.get('brand', 'Unknown'),
                        'price': product.get('price', 0),
                        'category': product.get('category', 'Unknown'),
                        'url': product.get('url', ''),
                        'seo_title': product.get('seo_data', {}).get('title', ''),
                        'meta_description': product.get('seo_data', {}).get('meta_description', ''),
                        'keywords': product.get('seo_data', {}).get('keywords', []),
                        'quality_score': product.get('quality_score', 0),
                        'is_valid': True,
                        'ai_model': 'simple-fast-processor',
                        'optimization': 'ULTRA-FAST'
                    })
                
                # Final update
                processing_time = result['metrics']['total_time']
                active_tasks[task_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"✅ ULTRA-FAST processing completed! {len(processed_products)} products in {processing_time:.1f}s",
                    "results": processed_products,
                    "processing_time": processing_time
                })
                
                # Save results
                await self._save_results(task_id, site, category, processed_products, processing_time)
                
            else:
                active_tasks[task_id].update({
                    "status": "error",
                    "message": f"❌ Error: {result.get('error', 'Unknown error')}",
                    "progress": 0
                })
                
        except Exception as e:
            active_tasks[task_id].update({
                "status": "error",
                "message": f"❌ Error: {str(e)}",
                "progress": 0
            })
    
    async def _save_results(self, task_id: str, site: str, category: str, products: list, processing_time: float):
        """Save results to file"""
        try:
            filename = f"fast_results_{site}_{category}_{int(time.time())}.json"
            filepath = f"data/web_results/{filename}"
            
            data = {
                'task_id': task_id,
                'site': site,
                'category': category,
                'products': products,
                'processing_time': processing_time,
                'timestamp': time.time(),
                'performance': 'ULTRA-FAST'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Save error: {e}")

# Initialize system
seo_system = SimpleCosmeticSEOSystem()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Fast Cosmetic SEO Extractor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select, input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .features { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .performance { background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Fast Cosmetic SEO Extractor</h1>
                <p>Ultra-fast cosmetic product SEO analysis in under 10 seconds</p>
            </div>
            
            <div class="performance">
                <h3>⚡ Performance Features</h3>
                <ul>
                    <li>🚀 Sub-10 second processing</li>
                    <li>💾 Smart caching system</li>
                    <li>🎯 Parallel processing</li>
                    <li>📊 Real-time progress</li>
                </ul>
            </div>
            
            <form id="seoForm">
                <div class="form-group">
                    <label>E-commerce Site:</label>
                    <select id="site" required>
                        <option value="">Select site...</option>
                        <option value="trendyol">Trendyol (⚡ Ultra-fast)</option>
                        <option value="gratis">Gratis (🚀 API-first)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Product Category:</label>
                    <select id="category" required>
                        <option value="">Select category...</option>
                        <option value="parfüm">Parfüm</option>
                        <option value="makyaj">Makyaj</option>
                        <option value="cilt bakımı">Cilt Bakımı</option>
                        <option value="kozmetik">Kozmetik</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Product Limit:</label>
                    <input type="number" id="limit" value="10" min="1" max="20" required>
                </div>
                
                <button type="submit">🚀 Start FAST Analysis</button>
            </form>
            
            <div id="status" style="margin-top: 20px; display: none;">
                <h3>Processing Status</h3>
                <div id="progress"></div>
                <div id="results"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('seoForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const site = document.getElementById('site').value;
                const category = document.getElementById('category').value;
                const limit = document.getElementById('limit').value;
                
                if (!site || !category) {
                    alert('Please select site and category');
                    return;
                }
                
                // Show status
                document.getElementById('status').style.display = 'block';
                document.getElementById('progress').innerHTML = '⏳ Starting fast processing...';
                
                try {
                    // Start processing
                    const response = await fetch('/start_extraction', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({site, category, max_products: parseInt(limit)})
                    });
                    
                    const data = await response.json();
                    
                    if (data.task_id) {
                        // Poll for progress
                        pollProgress(data.task_id);
                    } else {
                        document.getElementById('progress').innerHTML = '❌ Error starting task';
                    }
                } catch (error) {
                    document.getElementById('progress').innerHTML = '❌ Error: ' + error;
                }
            });
            
            function pollProgress(taskId) {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/status/${taskId}`);
                        const data = await response.json();
                        
                        document.getElementById('progress').innerHTML = `
                            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                                <strong>Status:</strong> ${data.message}<br>
                                <strong>Progress:</strong> ${data.progress}%
                            </div>
                        `;
                        
                        if (data.status === 'completed') {
                            clearInterval(interval);
                            showResults(data.results, data.processing_time);
                        } else if (data.status === 'error') {
                            clearInterval(interval);
                            document.getElementById('results').innerHTML = '<div style="color: red;">❌ ' + data.message + '</div>';
                        }
                    } catch (error) {
                        clearInterval(interval);
                        document.getElementById('results').innerHTML = '<div style="color: red;">❌ Error checking status</div>';
                    }
                }, 1000);
            }
            
            function showResults(results, processingTime) {
                let html = `
                    <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0;">
                        <h4>✅ Processing Completed!</h4>
                        <p><strong>⚡ Processing Time:</strong> ${processingTime.toFixed(2)} seconds</p>
                        <p><strong>📦 Products Processed:</strong> ${results.length}</p>
                    </div>
                    <h4>Results:</h4>
                    <div style="max-height: 400px; overflow-y: auto;">
                `;
                
                results.forEach((product, index) => {
                    html += `
                        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                            <h5>${product.name}</h5>
                            <p><strong>Brand:</strong> ${product.brand}</p>
                            <p><strong>Price:</strong> ${product.price}</p>
                            <p><strong>SEO Title:</strong> ${product.seo_title}</p>
                            <p><strong>Quality Score:</strong> ${product.quality_score}/100</p>
                            <p><strong>Keywords:</strong> ${product.keywords.join(', ')}</p>
                        </div>
                    `;
                });
                
                html += '</div>';
                document.getElementById('results').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/start_extraction")
async def start_extraction(request: Request, background_tasks: BackgroundTasks):
    """Start extraction process"""
    try:
        data = await request.json()
        site = data.get('site')
        category = data.get('category')
        max_products = data.get('max_products', 10)
        
        task_id = str(uuid.uuid4())
        
        # Start background task
        background_tasks.add_task(
            seo_system.process_extraction,
            task_id, site, category, max_products
        )
        
        return {"task_id": task_id, "status": "started"}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get task status"""
    if task_id in active_tasks:
        return active_tasks[task_id]
    else:
        return {"status": "not_found", "message": "Task not found"}

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "performance": "ULTRA-FAST",
        "features": ["sub-10s processing", "smart caching", "parallel processing"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FAST Cosmetic SEO Web App...")
    print("📊 Performance: Sub-10 second processing")
    print("🔗 Access: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
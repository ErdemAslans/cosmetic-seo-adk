# Cosmetic SEO Extractor - Google ADK Edition

A sophisticated multi-agent system built with **Google Agent Development Kit (ADK)** for autonomous cosmetic product SEO extraction from e-commerce websites.

## 🚀 Features

### Multi-Agent Architecture
- **Scout Agent**: Discovers product URLs using intelligent crawling
- **Scraper Agent**: Extracts detailed product information with Selenium
- **Analyzer Agent**: Cleans data and extracts cosmetic-specific terms
- **SEO Agent**: Generates keywords and metadata using advanced NLP
- **Quality Agent**: Validates SEO data against industry standards
- **Storage Agent**: Persists data to multiple formats (PostgreSQL, CSV, JSON)

### Powered by Google ADK
- **Advanced AI Models**: Leverages Gemini 1.5 Pro for intelligent processing
- **Tool Integration**: Custom tools for each agent specialization
- **Memory Management**: PostgreSQL-backed agent memory
- **Orchestration**: Built-in parallel and sequential processing
- **Development UI**: ADK's built-in interface for testing and debugging

### Industry-Specific Intelligence
- **Cosmetic Terminology**: Recognizes ingredients, benefits, and product types
- **Skin Type Analysis**: Identifies compatibility with different skin types
- **Turkish Market Focus**: Optimized for Turkish e-commerce sites
- **Quality Scoring**: Industry-specific SEO validation

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Scout Agent │───▶│Scraper Agent│───▶│Analyzer Agt │
└─────────────┘    └─────────────┘    └─────────────┘
                                               │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│Storage Agent│◀───│Quality Agent│◀───│ SEO Agent   │
└─────────────┘    └─────────────┘    └─────────────┘
```

Each agent is powered by Gemini and uses specialized tools for their domain.

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Google Cloud Project with Gemini API access
- Chrome/Chromium for web scraping

### Quick Start with Docker

1. **Clone and configure:**
```bash
git clone <repository>
cd cosmetic-seo-adk
cp .env.example .env
# Edit .env with your Google API credentials
```

2. **Add your Google Service Account credentials:**
```bash
# Place your credentials.json file in the project root
```

3. **Start the system:**
```bash
docker-compose up -d
```

4. **Run a sample test:**
```bash
docker-compose exec cosmetic-seo-extractor python run_sample.py
```

5. **Access ADK Development UI:**
```bash
# Visit http://localhost:8000 for the ADK interface
```

### Manual Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m nltk.downloader stopwords punkt
```

2. **Setup PostgreSQL:**
```bash
# Create database
createdb cosmetic_seo
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the system:**
```bash
# Test with sample data
python run_sample.py

# Full extraction
python main.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Google Cloud & Gemini API
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=false
GOOGLE_API_KEY=your-gemini-api-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cosmetic_seo

# Processing settings
MAX_PRODUCTS=1000
RATE_LIMIT_SECONDS=3
TEST_MODE=false
LOG_LEVEL=INFO
```

### Site Configuration

Edit `config/sites.py` to add or modify e-commerce sites:

```python
SiteConfig(
    name="new_site",
    base_url="https://example.com",
    category_paths=["/cosmetics", "/skincare"],
    selectors={
        "product_link": "a.product",
        "name": "h1.title",
        "description": ".product-desc"
    },
    rate_limit=3.0
)
```

## 🎯 Usage

### Sample Test (Recommended for first run)
```bash
python run_sample.py
```
This processes 3 products to verify the system is working correctly.

### Full Extraction
```bash
python main.py
```
Processes products from all configured sites.

### Using ADK Development UI
```bash
# Start the development interface
python -m adk dev --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose up adk-ui
```

Visit `http://localhost:8000` to interact with agents directly.

## 📊 Output Formats

### 1. PostgreSQL Database
- **products**: Complete product information
- **seo_data**: SEO metadata and keywords  
- **quality_validations**: Quality scores and validation results

### 2. CSV Export
`data/exports/cosmetic_products_seo.csv`:
```csv
url,product_name,brand,primary_keyword,seo_keywords,seo_title,meta_description,quality_score
```

### 3. JSON Files
Individual files in `data/products/`:
```json
{
  "product": {...},
  "seo": {...},
  "validation": {...},
  "metadata": {...}
}
```

## 🤖 Agent Details

### Scout Agent
- **Model**: Gemini 1.5 Pro
- **Tools**: URL Discovery Tool
- **Function**: Finds cosmetic product URLs from category pages
- **Output**: List of product URLs for processing

### Scraper Agent  
- **Model**: Gemini 1.5 Pro
- **Tools**: Product Scraping Tool (Selenium-based)
- **Function**: Extracts comprehensive product data
- **Output**: Structured product information

### Analyzer Agent
- **Model**: Gemini 1.5 Pro
- **Tools**: Data Cleaning Tool, Cosmetic Analysis Tool
- **Function**: Cleans data and extracts cosmetic terms
- **Output**: Normalized data with cosmetic insights

### SEO Agent
- **Model**: Gemini 1.5 Pro
- **Tools**: Keyword Extraction Tool, SEO Metadata Tool
- **Function**: Generates SEO-optimized content
- **Output**: Keywords, titles, meta descriptions, slugs

### Quality Agent
- **Model**: Gemini 1.5 Pro
- **Tools**: SEO Quality Validation, Cosmetic Best Practices
- **Function**: Validates SEO quality and compliance
- **Output**: Quality scores and recommendations

### Storage Agent
- **Model**: Gemini 1.5 Pro
- **Tools**: Database Storage, File Storage, Reporting
- **Function**: Persists validated data to multiple formats
- **Output**: Stored data with confirmation

## 📈 Monitoring & Debugging

### ADK Development UI
The built-in ADK interface provides:
- Real-time agent interaction
- Tool testing and debugging
- Memory inspection
- Performance metrics

### Logging
```bash
# View logs
tail -f logs/cosmetic_seo.log

# Sample test logs
tail -f logs/sample_test.log
```

### Quality Metrics
- **SEO Quality Score**: 0-100 based on best practices
- **Validation Rate**: Percentage of products passing quality checks
- **Processing Success Rate**: Percentage of URLs successfully processed

## 🔍 Troubleshooting

### Common Issues

1. **Google API Errors**
   - Verify `GOOGLE_API_KEY` is correct
   - Check API quotas and billing
   - Ensure Gemini API is enabled

2. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check `DATABASE_URL` format
   - Ensure database exists

3. **Scraping Failures**
   - Check Chrome/Chromium installation
   - Verify site accessibility
   - Review rate limiting settings

4. **Agent Initialization Errors**
   - Install missing dependencies
   - Download required NLP models
   - Check Python version (3.9+ required)

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=DEBUG python main.py

# Test individual agents
python -c "
from agents.scout_agent import create_scout_agent
import asyncio
async def test(): 
    agent = create_scout_agent()
    result = await agent.process_discovery_request('trendyol', 1)
    print(result)
asyncio.run(test())
"
```

## 🚀 Deployment

### Production Deployment
1. **Use Docker for consistency**
2. **Set up proper monitoring**
3. **Configure log rotation**
4. **Set up database backups**
5. **Use environment-specific configurations**

### Scaling
- **Horizontal**: Run multiple instances with shared database
- **Vertical**: Increase resources for individual agents
- **Load Balancing**: Distribute sites across instances

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Google Agent Development Kit** for the powerful multi-agent framework
- **Gemini AI** for advanced language understanding
- **Turkish e-commerce sites** for product data (used ethically with rate limiting)

---

**Built with ❤️ using Google Agent Development Kit**
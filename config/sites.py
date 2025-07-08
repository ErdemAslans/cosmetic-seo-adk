from config.models import SiteConfig

SITE_CONFIGS = [
    SiteConfig(
        name="trendyol",
        base_url="https://www.trendyol.com",
        category_paths=[
            "/kozmetik-x-c40",
            "/cilt-bakimi-x-g-102422",
            "/makyaj-x-g-102424",
            "/parfum-deodorant-x-g-102425"
        ],
        selectors={
            "product_link": "div.p-card-wrppr a",
            "next_page": "a.pagination-next",
            "name": "h1.pr-new-br",
            "brand": "h1.pr-new-br a",
            "price": "span.prc-dsc",
            "description": "div.info-wrapper",
            "ingredients": "div.ingredient-list li",
            "features": "ul.detail-attr-list li",
            "reviews": "div.comment-text",
            "images": "img.detail-img"
        },
        rate_limit=3.0,
        max_pages=50,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    ),
    
    SiteConfig(
        name="sephora_tr",
        base_url="https://www.sephora.com.tr",
        category_paths=[
            "/cilt-bakimi-c-302",
            "/makyaj-c-301", 
            "/parfum-c-304"
        ],
        selectors={
            "product_link": "a.product-item-link",
            "next_page": "a.action.next",
            "name": "h1.page-title",
            "brand": "div.product-brand",
            "price": "span.price",
            "description": "div.product-description",
            "ingredients": "div.ingredients-content",
            "features": "div.product-features li",
            "reviews": "div.review-content",
            "images": "img.gallery-image"
        },
        rate_limit=3.0,
        max_pages=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    ),
    
    SiteConfig(
        name="gratis",
        base_url="https://www.gratis.com",
        category_paths=[
            "/kategori/makyaj",
            "/kategori/cilt-bakimi",
            "/kategori/sac-bakimi"
        ],
        selectors={
            "product_link": "a.product-box-image-link",
            "next_page": "li.pagination-next a",
            "name": "h1.product-name",
            "brand": "a.product-brand",
            "price": "span.total-price",
            "description": "div.product-detail-tab-content",
            "ingredients": "div.ingredients p",
            "features": "div.features-list li",
            "reviews": "div.comment-detail",
            "images": "img.product-image"
        },
        rate_limit=2.5,
        max_pages=40,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }
    )
]
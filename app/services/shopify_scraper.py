import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
import time

# Update imports to be relative
from ..core.models import Product, FAQ, SocialHandle, ContactInfo, Policy, ImportantLink, BrandContext, BrandInsights
from .gemini_service import GeminiService

class ShopifyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.gemini_service = GeminiService()
    
    def is_shopify_store(self, url: str) -> bool:
        """Check if the given URL is a Shopify store"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check for Shopify indicators
            shopify_indicators = [
                'Shopify.shop',
                'shopify-section',
                'cdn.shopify.com',
                'myshopify.com',
                'Shopify.theme',
                'shopify-features'
            ]
            
            content = response.text.lower()
            return any(indicator.lower() in content for indicator in shopify_indicators)
        except Exception as e:
            print(f"Error checking if Shopify store: {e}")
            return False
    
    def fetch_products_json(self, base_url: str) -> List[Dict[str, Any]]:
        """Fetch products from /products.json endpoint"""
        try:
            products_url = urljoin(base_url, '/products.json')
            response = self.session.get(products_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return data.get('products', [])
        except Exception as e:
            print(f"Error fetching products.json: {e}")
            return []
    
    def parse_product(self, product_data: Dict[str, Any], base_url: str) -> Product:
        """Parse product data into Product model"""
        try:
            images = []
            if 'images' in product_data:
                images = [img.get('src', '') for img in product_data['images']]
            
            variants = product_data.get('variants', [])
            price = None
            compare_at_price = None
            
            if variants:
                price = variants[0].get('price', '0')
                compare_at_price = variants[0].get('compare_at_price')
            
            return Product(
                id=product_data.get('id'),
                title=product_data.get('title', ''),
                handle=product_data.get('handle', ''),
                description=product_data.get('body_html', ''),
                price=price,
                compare_at_price=compare_at_price,
                vendor=product_data.get('vendor', ''),
                product_type=product_data.get('product_type', ''),
                tags=product_data.get('tags', []),
                images=images,
                variants=variants,
                available=any(variant.get('available', False) for variant in variants),
                url=urljoin(base_url, f"/products/{product_data.get('handle', '')}")
            )
        except Exception as e:
            print(f"Error parsing product: {e}")
            return None
    
    def fetch_page_content(self, url: str) -> Tuple[str, BeautifulSoup]:
        """Fetch and parse page content"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return response.text, soup
        except Exception as e:
            print(f"Error fetching page content from {url}: {e}")
            return "", None
    
    def extract_hero_products(self, soup: BeautifulSoup, all_products: List[Product]) -> List[Product]:
        """Extract hero products from homepage"""
        hero_products = []
        
        if not all_products:
            return []

        product_links = soup.find_all('a', href=re.compile(r'/products/'))
        hero_handles = {urlparse(link['href']).path.split('/')[-1] for link in product_links}
        
        for product in all_products:
            if product.handle in hero_handles:
                hero_products.append(product)
        
        # Fallback if no hero products found via links
        if not hero_products and all_products:
            return all_products[:5] # Return first 5 as a guess
            
        return hero_products

    def extract_policies(self, base_url: str) -> Dict[str, Policy]:
        """Extract various policies from the store"""
        policies = {}
        policy_paths = {
            'privacy_policy': '/policies/privacy-policy',
            'return_policy': '/policies/return-policy',
            'refund_policy': '/policies/refund-policy',
            'shipping_policy': '/policies/shipping-policy',
            'terms_of_service': '/policies/terms-of-service'
        }

        for name, path in policy_paths.items():
            try:
                policy_url = urljoin(base_url, path)
                html_content, soup = self.fetch_page_content(policy_url)
                
                if soup:
                    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else name.replace('_', ' ').title()
                    content = str(soup.find('div', class_='rte'))
                    
                    policies[name] = Policy(
                        title=title,
                        url=policy_url,
                        content=content
                    )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"Policy not found at {path}, which is common. Skipping.")
                else:
                    print(f"Error fetching policy {name}: {e}")
            except Exception as e:
                print(f"Error processing policy {name}: {e}")
        
        return policies

    def extract_important_links(self, soup: BeautifulSoup, base_url: str) -> List[ImportantLink]:
        """Extract important links from the website"""
        links = []
        # Common link locations: header, footer, nav
        nav_elements = soup.find_all(['nav', 'header', 'footer'])
        
        for element in nav_elements:
            for a in element.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                
                if not text or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                
                full_url = urljoin(base_url, href)
                
                # Avoid duplicates
                if not any(link.url == full_url for link in links):
                    links.append(ImportantLink(title=text, url=full_url))

        # Add common but potentially unlinked paths
        common_paths = ['/pages/about-us', '/pages/contact', '/blogs']
        for path in common_paths:
            full_url = urljoin(base_url, path)
            if not any(link.url == full_url for link in links):
                try:
                    res = self.session.head(full_url, timeout=5)
                    if res.status_code == 200:
                        links.append(ImportantLink(title=path.split('/')[-1].replace('-', ' ').title(), url=full_url))
                except Exception:
                    pass

        return links

    def scrape_store(self, store_url: str) -> BrandInsights:
        """Main method to scrape Shopify store"""
        errors = []
        start_time = time.time()
        
        try:
            # Validate and clean URL
            parsed_url = urlparse(store_url)
            if not parsed_url.scheme:
                store_url = 'https://' + store_url
            
            # Check if it's a Shopify store
            if not self.is_shopify_store(store_url):
                errors.append("URL does not appear to be a Shopify store")
            
            # Fetch homepage content
            html_content, soup = self.fetch_page_content(store_url)
            
            if not soup:
                errors.append("Failed to fetch homepage content")
                return BrandInsights(
                    store_url=store_url,
                    scraping_success=False,
                    errors=errors
                )
            
            # Extract store name
            store_name = None
            title_tag = soup.find('title')
            if title_tag:
                store_name = title_tag.get_text(strip=True)
            
            # Fetch products
            products_data = self.fetch_products_json(store_url)
            products = []
            
            for product_data in products_data:
                product = self.parse_product(product_data, store_url)
                if product:
                    products.append(product)
            
            # Extract hero products
            hero_products = self.extract_hero_products(soup, products)
            
            # Extract policies
            policies = self.extract_policies(store_url)
            
            # Extract important links
            important_links = self.extract_important_links(soup, store_url)
            
            # Use Gemini to extract structured data
            brand_context_data = self.gemini_service.extract_brand_context(html_content, store_url)
            brand_context = BrandContext(
                store_url=store_url,
                store_name=brand_context_data.get('store_name', store_name),
                brand_description=brand_context_data.get('brand_description'),
                about_us=brand_context_data.get('about_us'),
                mission_statement=brand_context_data.get('mission_statement'),
                founded_year=brand_context_data.get('founded_year'),
                headquarters=brand_context_data.get('headquarters')
            )
            
            # Extract FAQs using Gemini
            faqs_data = self.gemini_service.extract_faqs(html_content)
            faqs = [FAQ(**faq) for faq in faqs_data if isinstance(faq, dict)]
            
            # Extract contact info using Gemini
            contact_data = self.gemini_service.extract_contact_info(html_content)
            contact_info = ContactInfo(**contact_data) if contact_data else None
            
            # Extract social handles using Gemini
            social_data = self.gemini_service.extract_social_handles(html_content)
            social_handles = [SocialHandle(**social) for social in social_data if isinstance(social, dict) and social.get("url")]
            
            # Create BrandInsights object
            brand_insights = BrandInsights(
                store_url=store_url,
                store_name=store_name,
                brand_context=brand_context,
                product_catalog=products,
                hero_products=hero_products,
                total_products=len(products),
                privacy_policy=policies.get('privacy_policy'),
                return_policy=policies.get('return_policy'),
                refund_policy=policies.get('refund_policy'),
                shipping_policy=policies.get('shipping_policy'),
                terms_of_service=policies.get('terms_of_service'),
                faqs=faqs,
                contact_info=contact_info,
                social_handles=social_handles,
                important_links=important_links,
                scraping_success=True,
                errors=errors
            )
            
            return brand_insights
            
        except Exception as e:
            errors.append(f"Scraping failed: {str(e)}")
            return BrandInsights(
                store_url=store_url,
                scraping_success=False,
                errors=errors
            )

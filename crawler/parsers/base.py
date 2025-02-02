"""Base parser class for news crawlers"""

import aiohttp
from crawler.config.settings import SUPABASE_CONFIG
from supabase import create_client
import re
import hashlib

class BaseParser:
    def __init__(self, source_config):
        self.config = source_config
        self.supabase = create_client(SUPABASE_CONFIG['url'], SUPABASE_CONFIG['key'])

    def generate_hash(self, text):
        """Generate a normalized hash for text"""
        if not text:
            return None
        # Normalize: lowercase, remove punctuation, extra spaces
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    async def check_duplicate(self, title, url):
        """Check if article already exists in either table"""
        title_hash = self.generate_hash(title)
        url_hash = self.generate_hash(url)

        # First check source_articles table using hashes
        source_response = self.supabase.table('source_articles')\
            .select('id, title, source_url')\
            .or_(
                f'url_hash.eq.{url_hash},'
                f'title_hash.eq.{title_hash}'
            )\
            .execute()
        
        if source_response.data:
            matching_article = source_response.data[0]
            match_type = "URL" if url_hash == matching_article.get('url_hash') else "Title"
            return True, f"Already in source_articles ({match_type} match): {matching_article['title']}"

        # Then check articles table
        articles_response = self.supabase.table('articles')\
            .select('id, title')\
            .or_(f'url_hash.eq.{url_hash},title_hash.eq.{title_hash}')\
            .execute()

        if articles_response.data:
            return True, f"Already in articles: {articles_response.data[0]['title']}"

        return False, None

    async def save_raw_article(self, article_data):
        """Save raw article data to source_articles table"""
        try:
            # Check for duplicates first
            is_duplicate, message = await self.check_duplicate(
                article_data['title'],
                article_data['source_url']
            )

            if is_duplicate:
                print(f"Skipping duplicate: {article_data['title']}")
                print(f"Reason: {message}")
                return False

            data = {
                'title': article_data['title'],
                'excerpt': article_data.get('excerpt'),
                'content': article_data.get('content'),
                'raw_html': article_data.get('raw_html'),
                'raw_data': article_data,
                'source_url': article_data['source_url'],
                'source_name': article_data['source_name'],
                'source_language': article_data.get('language', 'en'),
                'published_at': article_data.get('published_at'),
                'status': 'pending',
                'url_hash': self.generate_hash(article_data['source_url']),
                'title_hash': self.generate_hash(article_data['title'])
            }
            
            result = self.supabase.table('source_articles').insert(data).execute()
            print(f"Saved new article: {data['title']}")
            return True

        except Exception as e:
            print(f"Error saving raw article: {e}")
            return False

    async def fetch_page(self, url):
        """Fetch page content with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None

    def parse_html(self, html):
        """Parse HTML and extract articles"""
        raise NotImplementedError("Subclasses must implement parse_html method") 
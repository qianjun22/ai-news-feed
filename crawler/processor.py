"""Process raw articles and transfer them to the articles table"""

import asyncio
from crawler.config.settings import SUPABASE_CONFIG
from supabase import create_client
from datetime import datetime
import re
import hashlib

class ArticleProcessor:
    def __init__(self):
        self.supabase = create_client(SUPABASE_CONFIG['url'], SUPABASE_CONFIG['key'])

    def generate_hash(self, text):
        """Generate a normalized hash for text"""
        if not text:
            return None
        # Normalize: lowercase, remove punctuation, extra spaces
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def normalize_url(self, url):
        """Normalize URL by removing tracking parameters and standardizing format"""
        if not url:
            return None
        # Remove protocol and www
        url = re.sub(r'^https?://(www\.)?', '', url.lower())
        # Remove query parameters and fragments
        url = re.sub(r'[?#].*$', '', url)
        # Remove trailing slashes
        url = re.sub(r'/+$', '', url)
        return url

    def normalize_title(self, title):
        """Normalize title by removing punctuation and standardizing format"""
        if not title:
            return None
        # Convert to lowercase, remove punctuation, normalize spaces
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def check_duplicate(self, title, url):
        """Check if article is duplicate based on either title or URL hash"""
        title_hash = self.generate_hash(title)
        url_hash = self.generate_hash(url)

        # Check if either hash exists
        response = self.supabase.table('articles')\
            .select('id, title, source_url, url_hash, title_hash')\
            .or_(f'url_hash.eq.{url_hash},title_hash.eq.{title_hash}')\
            .execute()
        
        if response.data:
            matching_article = response.data[0]
            match_type = "URL" if url_hash == matching_article.get('url_hash') else "Title"
            return True, f"{match_type} matches: {matching_article['title']} ({matching_article['source_url']})"

        return False, None

    def process_articles(self):
        """Process pending articles from source_articles table"""
        try:
            response = self.supabase.table('source_articles')\
                .select('*')\
                .eq('status', 'pending')\
                .execute()

            pending_articles = response.data
            print(f"Found {len(pending_articles)} pending articles")

            for article in pending_articles:
                try:
                    # Check for duplicates
                    is_duplicate, existing_title = self.check_duplicate(
                        article['title'], 
                        article['source_url']
                    )

                    if is_duplicate:
                        print(f"Skipping duplicate article: {article['title']}")
                        print(f"Matches existing article: {existing_title}")
                        
                        # Update source article status to ignored
                        self.supabase.table('source_articles')\
                            .update({'status': 'ignored', 'fetch_error': 'Duplicate article'})\
                            .eq('id', article['id'])\
                            .execute()
                        continue

                    # Basic processing
                    processed_data = {
                        'title': article['title'],
                        'excerpt': article['excerpt'],
                        'content': article.get('content', article.get('excerpt', '')),
                        'source_url': article['source_url'],
                        'source_name': article['source_name'],
                        'category': 'general',
                        'importance_score': 3,
                        'reading_time_minutes': 5,
                        'published_at': article['published_at'] or article['created_at'],
                        'raw_content': article.get('raw_data', {}),
                        'url_hash': self.generate_hash(article['source_url']),
                        'title_hash': self.generate_hash(article['title'])
                    }

                    # Insert into articles table
                    self.supabase.table('articles').insert(processed_data).execute()

                    # Update source article status
                    self.supabase.table('source_articles')\
                        .update({'status': 'processed'})\
                        .eq('id', article['id'])\
                        .execute()

                    print(f"Processed article: {article['title']}")

                except Exception as e:
                    print(f"Error processing article {article['id']}: {e}")
                    self.supabase.table('source_articles')\
                        .update({
                            'status': 'error',
                            'fetch_error': str(e)
                        })\
                        .eq('id', article['id'])\
                        .execute()

        except Exception as e:
            print(f"Error fetching pending articles: {e}")

def main():
    processor = ArticleProcessor()
    print("Starting article processing...")
    processor.process_articles()
    print("Processing complete")

if __name__ == "__main__":
    main() 
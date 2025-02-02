"""VentureBeat parser implementation"""

from bs4 import BeautifulSoup
from crawler.parsers.base import BaseParser
from crawler.utils.date_parser import parse_date

class VentureBeatParser(BaseParser):
    async def parse_html(self, html):
        """Parse VentureBeat HTML and extract articles"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        for article in soup.select(self.config['article_selector']):
            try:
                article_data = self._parse_article(article)
                if article_data:
                    await self.save_raw_article(article_data)
                    articles.append(article_data)
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue

        return articles

    def _parse_article(self, article):
        """Parse single article element"""
        title_elem = article.select_one(self.config['title_selector'])
        excerpt_elem = article.select_one(self.config['excerpt_selector'])
        time_elem = article.select_one(self.config['time_selector'])

        if not title_elem:
            return None

        # Use the datetime attribute for the published time
        published_time = time_elem['datetime'] if time_elem and time_elem.has_attr('datetime') else ''

        article_data = {
            'title': title_elem.text.strip(),
            'source_url': title_elem['href'] if title_elem.has_attr('href') else '',
            'excerpt': excerpt_elem.text.strip() if excerpt_elem else '',
            'source_name': 'VentureBeat',
            'raw_html': str(article),
            'published_at': published_time,
            'language': 'en'
        }
        
        #print(article_data)
        return article_data 
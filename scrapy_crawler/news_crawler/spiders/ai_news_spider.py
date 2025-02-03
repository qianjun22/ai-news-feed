import scrapy
import os
import shutil

class AINewsSpider(scrapy.Spider):
    name = 'ai_news'
    
    def __init__(self, *args, **kwargs):
        super(AINewsSpider, self).__init__(*args, **kwargs)
        self.clean_raw_html_directory()
        
    def clean_raw_html_directory(self):
        """Clean the raw_html directory before starting the spider."""
        raw_html_dir = "raw_html"
        if os.path.exists(raw_html_dir):
            shutil.rmtree(raw_html_dir)
        os.makedirs(raw_html_dir)
        self.logger.info("🧹 Cleaned raw_html directory")
    
    def start_requests(self):
        urls = [
            'https://news.qq.com/omn/author/5022548',
            'https://www.theverge.com/ai-artificial-intelligence',
            'https://www.technologyreview.com/topic/artificial-intelligence/',
            'https://www.thetimes.com/business-money/technology'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                headers=headers,
                callback=self.parse
            )

    def parse(self, response):
        """Extract raw HTML from news sites."""
        try:
            # Get source name from URL
            if 'theverge.com' in response.url:
                source = 'theverge'
            elif 'technologyreview.com' in response.url:
                source = 'techreview'
            elif 'qq.com' in response.url:
                source = 'qq'
            elif 'thetimes.com' in response.url:
                source = 'thetimes'
            else:
                source = 'unknown'
                
            yield {
                'url': response.url,
                'source': source,
                'raw_html': response.body.decode('utf-8', errors='ignore'),  # Handle encoding errors
                'timestamp': response.headers.get('Date', b'').decode('utf-8', errors='ignore')
            }
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")
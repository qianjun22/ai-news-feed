"""Main crawler script"""

import asyncio
from crawler.parsers.venturebeat import VentureBeatParser
from crawler.config.sources import SOURCES

async def main():
    """Main crawler function"""
    parser = VentureBeatParser(SOURCES['venturebeat'])
    print(f"Fetching articles from VentureBeat...")
    
    html = await parser.fetch_page(SOURCES['venturebeat']['url'])
    if html:
        articles = await parser.parse_html(html)
        print(f"Found and processed {len(articles)} articles")
        return articles
    
    print("Failed to fetch articles")
    return []

if __name__ == "__main__":
    asyncio.run(main()) 
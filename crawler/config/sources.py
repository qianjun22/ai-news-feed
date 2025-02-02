"""News source configurations"""

SOURCES = {
    'venturebeat': {
        'url': 'https://venturebeat.com/category/ai/',
        'article_selector': 'article.ArticleListing',
        'title_selector': 'h2 a',
        'excerpt_selector': 'p.ArticleListing__excerpt',
        'time_selector': 'time'
    }
} 
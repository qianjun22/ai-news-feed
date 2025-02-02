"""Category detection utilities"""

CATEGORIES = {
    'research': ['research', 'study', 'paper', 'algorithm', 'model'],
    'industry': ['launch', 'startup', 'company', 'business', 'market'],
    'ethics': ['ethics', 'bias', 'fairness', 'responsible', 'safety'],
    'funding': ['funding', 'raises', 'investment', 'million', 'billion'],
    'policy': ['policy', 'regulation', 'law', 'government', 'compliance']
}

def detect_category(title):
    """Detect article category based on keywords"""
    title = title.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in title for keyword in keywords):
            return category
    return 'general' 
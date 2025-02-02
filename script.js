let supabaseClient;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Supabase
    supabaseClient = supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.key);
    console.log('DOM loaded, checking Supabase connection...');
    console.log('Using Supabase URL:', SUPABASE_CONFIG.url);
    fetchNews();
});

async function fetchNews() {
    try {
        console.log('Fetching news from Supabase...');
        // Test connection first
        const { data: test, error: testError } = await supabaseClient
            .from('articles')
            .select('count');
        
        if (testError) {
            console.error('Connection test failed:', testError);
            throw testError;
        }
        console.log('Connection successful, fetching articles...');

        const { data: articles, error } = await supabaseClient
            .from('articles')
            .select('*')
            .order('published_at', { ascending: false })
            .limit(20);

        if (error) throw error;
        
        console.log('Fetched articles:', articles);
        renderNews(articles);
    } catch (error) {
        console.error('Error fetching news:', error);
        // Fall back to sample data if there's an error
        console.log('Falling back to sample data...');
        renderNews(getSampleNews());
    }
}

function formatTimeAgo(date) {
    const now = new Date();
    const diff = Math.floor((now - new Date(date)) / 1000);
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    
    return new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function groupArticlesByDate(articles) {
    const groups = {};
    
    articles.forEach(article => {
        const date = new Date(article.published_at);
        const now = new Date();
        const diff = Math.floor((now - date) / (1000 * 60 * 60));
        
        let key;
        if (diff < 24) {
            key = 'TODAY';
        } else if (diff < 48) {
            key = 'YESTERDAY';
        } else {
            key = date.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'short',
                day: 'numeric'
            }).toUpperCase();
        }
        
        if (!groups[key]) groups[key] = [];
        groups[key].push(article);
    });
    
    return groups;
}

function renderNews(articles) {
    const newsContent = document.getElementById('news-content');
    
    if (articles.length === 0) {
        newsContent.innerHTML = '<p>No news articles available.</p>';
        return;
    }
    
    const groupedArticles = groupArticlesByDate(articles);
    
    // Helper function to get emoji based on category and age
    function getNewsIndicator(article) {
        const hoursSincePublished = (new Date() - new Date(article.published_at)) / (1000 * 60 * 60);
        
        if (hoursSincePublished < 12) {
            return '🔥'; // Breaking/Hot
        }
        
        switch (article.category.toLowerCase()) {
            case 'research': return '🔬';
            case 'industry': return '🏢';
            case 'ethics': return '⚖️';
            case 'analysis': return '📊';
            case 'funding': return '💰';
            case 'policy': return '📜';
            default: return '📰';
        }
    }

    const newsHTML = Object.entries(groupedArticles).map(([date, dateArticles]) => `
        <div class="news-date-group" role="region" aria-label="${date} news">
            <h2 class="date-header">${date}</h2>
            ${dateArticles.map((article, index) => `
                <div class="news-card" role="article">
                    <span class="news-indicator" role="img" aria-label="${article.category}">${getNewsIndicator(article)}</span>
                    <div class="news-main">
                        <div>
                            <h3 title="${article.title}" onclick="toggleSummary(this)" data-article-id="${article.id}">
                                ${index + 1}. ${article.title} - ${formatTimeAgo(article.published_at)}
                            </h3>
                            <div class="news-summary">
                                <p>${article.excerpt}</p>
                                <div class="news-summary-meta">
                                    <span>${article.source_name}</span>
                                    <a href="${article.source_url}" target="_blank" rel="noopener noreferrer">Read full article →</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `).join('');

    newsContent.innerHTML = newsHTML;
}

function getSampleNews() {
    return [
        {
            title: "DeepSeek: Separating fact from hype",
            excerpt: "An in-depth analysis of DeepSeek's capabilities and market position",
            published_at: new Date(Date.now() - 9 * 60 * 60 * 1000), // 9 hours ago
            category: "Analysis",
            source_name: "AI Research Daily"
        },
        {
            title: "AI agents could birth the first one-person unicorn — but at what societal cost?",
            excerpt: "Examining the implications of AI-driven solo entrepreneurship",
            published_at: new Date(Date.now() - 10 * 60 * 60 * 1000), // 10 hours ago
            category: "Industry",
            source_name: "TechCrunch"
        },
        {
            title: "OpenAI used this subreddit to test AI persuasion",
            excerpt: "Investigation reveals OpenAI's testing grounds for persuasive AI",
            published_at: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            category: "Research",
            source_name: "AI Ethics Watch"
        },
        {
            title: "Sam Altman: OpenAI has been on the 'wrong side of history' concerning open source",
            excerpt: "OpenAI's CEO addresses criticism about the company's stance on open source",
            published_at: new Date(Date.now() - 24 * 60 * 60 * 1000),
            category: "Industry",
            source_name: "Tech Insider"
        }
    ];
}

function toggleSummary(element) {
    // Close any other open summaries
    const allSummaries = document.querySelectorAll('.news-summary.active');
    allSummaries.forEach(summary => {
        if (summary !== element.nextElementSibling) {
            summary.classList.remove('active');
        }
    });

    // Toggle the clicked summary
    const summary = element.nextElementSibling;
    summary.classList.toggle('active');
}
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
            .order('created_at', { ascending: false })
            .limit(10);

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
            key = 'Today';
        } else if (diff < 48) {
            key = 'Yesterday';
        } else {
            key = date.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'short',
                day: 'numeric'
            });
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
        
        if (hoursSincePublished < 24) {
            return '🔥'; // Breaking/New
        }
        
        switch (article.category.toLowerCase()) {
            case 'research': return '🔬';
            case 'industry': return '🏢';
            case 'ethics': return '⚖️';
            case 'healthcare': return '🏥';
            default: return '📰';
        }
    }

    const newsHTML = Object.entries(groupedArticles).map(([date, dateArticles]) => `
        <div class="news-date-group" role="region" aria-label="${date} news">
            <h2 class="date-header">${date}</h2>
            ${dateArticles.map(article => `
                <div class="news-card" role="article">
                    <span class="news-indicator" role="img" aria-label="${article.category}">${getNewsIndicator(article)}</span>
                    <div class="news-main">
                        <h3 title="${article.title}">${article.title}</h3>
                        <p title="${article.excerpt}">${article.excerpt}</p>
                    </div>
                    <div class="article-meta">
                        <a href="${article.source_url}" 
                           target="_blank" 
                           rel="noopener noreferrer"
                           aria-label="Read full article from ${article.source_name}">${article.source_name}</a>
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
            title: 'Latest AI Breakthrough in Natural Language Processing',
            excerpt: 'Researchers develop new transformer model that achieves state-of-the-art results...',
            image_url: 'https://picsum.photos/seed/ai1/400/300',
            category: 'Research'
        },
        {
            title: 'AI Ethics Guidelines Released',
            excerpt: 'Major tech companies collaborate on new AI ethics framework...',
            image_url: 'https://picsum.photos/seed/ai2/400/300',
            category: 'Industry'
        },
        {
            title: 'Machine Learning in Healthcare',
            excerpt: 'New AI system shows promising results in early disease detection...',
            image_url: 'https://picsum.photos/seed/ai3/400/300',
            category: 'Healthcare'
        }
    ];
}
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

function renderNews(articles) {
    const newsContent = document.getElementById('news-content');
    const highlightContent = document.getElementById('highlight-content');
    
    if (articles.length === 0) {
        newsContent.innerHTML = '<p>No news articles available.</p>';
        return;
    }
    
    // Render highlight
    const highlight = articles[0];
    highlightContent.innerHTML = `
        <div class="news-card featured">
            <img src="${highlight.image_url || 'https://picsum.photos/seed/default/400/300'}" alt="${highlight.title}">
            <div class="news-content">
                <span class="category">${highlight.category}</span>
                <h3>${highlight.title}</h3>
                <p>${highlight.excerpt}</p>
                <div class="article-meta">
                    <span class="source">Source: ${highlight.source_name}</span>
                    ${highlight.reading_time_minutes ? `<span class="reading-time">${highlight.reading_time_minutes} min read</span>` : ''}
                </div>
                <a href="${highlight.source_url}" target="_blank" rel="noopener noreferrer">Read more</a>
            </div>
        </div>
    `;

    // Render other news
    const newsHTML = articles.slice(1).map(article => `
        <div class="news-card">
            <img src="${article.image_url || 'https://picsum.photos/seed/default/400/300'}" alt="${article.title}">
            <div class="news-content">
                <span class="category">${article.category}</span>
                <h3>${article.title}</h3>
                <p>${article.excerpt}</p>
                <div class="article-meta">
                    <span class="source">Source: ${article.source_name}</span>
                    ${article.reading_time_minutes ? `<span class="reading-time">${article.reading_time_minutes} min read</span>` : ''}
                </div>
                <a href="${article.source_url}" target="_blank" rel="noopener noreferrer">Read more</a>
            </div>
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
let supabaseClient;
let currentOffset = 0;
const PAGE_SIZE = 20;
let isLoading = false;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Supabase
    supabaseClient = supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.key);
    console.log('DOM loaded, checking Supabase connection...');
    console.log('Using Supabase URL:', SUPABASE_CONFIG.url);
    fetchNews();

    // Add Load More button handler
    document.getElementById('load-more').addEventListener('click', async () => {
        if (!isLoading) {
            isLoading = true;
            currentOffset += PAGE_SIZE;
            await fetchNews(currentOffset);
        }
    });
});

async function fetchNews(offset = 0) {
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
            .select('id, title, excerpt, source_url, source_name, category, published_at')
            .order('published_at', { ascending: false })
            .range(offset, offset + PAGE_SIZE - 1);

        if (error) throw error;
        
        console.log('Fetched articles:', articles);
        renderNews(articles);
        
        // Show/hide load more button based on results
        const loadMoreButton = document.getElementById('load-more');
        loadMoreButton.classList.toggle('hidden', articles.length < PAGE_SIZE);
        isLoading = false;

    } catch (error) {
        console.error('Error fetching news:', error);
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
    const groupedArticles = groupArticlesByDate(articles);
    
    if (articles.length === 0) {
        newsContent.innerHTML = '<p>No news articles available.</p>';
        return;
    }
    
    const newsHTML = Object.entries(groupedArticles).map(([date, dateArticles]) => `
        <div class="news-date-group" role="region" aria-label="${date} news">
            <h2 class="date-header">${date}</h2>
            ${dateArticles.map((article) => `
                <div class="news-card" role="article">
                    <span class="news-indicator" role="img" aria-label="${article.category}">${getNewsIndicator(article)}</span>
                    <div class="news-main">
                        <div>
                            <h3 title="${article.title}" onclick="toggleSummary(this)" data-article-id="${article.id}">
                                ${article.title} - ${formatTimeAgo(article.published_at)}
                            </h3>
                            <div class="news-summary">
                                <p>${article.excerpt}</p>
                                <div class="news-summary-meta">
                                    <span>${article.source_name}</span>
                                    <a href="${article.source_url}" target="_blank" rel="noopener noreferrer">Read full article →</a>
                                </div>
                            </div>
                        </div>
                        <div class="news-source">
                            Source: ${article.source_name}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `).join('');

    if (currentOffset === 0) {
        newsContent.innerHTML = newsHTML;
    } else {
        newsContent.insertAdjacentHTML('beforeend', newsHTML);
    }
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

function appendNews(newArticles) {
    const newsContent = document.getElementById('news-content');
    const groupedArticles = groupArticlesByDate(newArticles);

    Object.entries(groupedArticles).forEach(([date, dateArticles]) => {
        let dateGroup = newsContent.querySelector(`[aria-label="${date} news"]`);
        
        if (!dateGroup) {
            dateGroup = document.createElement('div');
            dateGroup.className = 'news-date-group';
            dateGroup.setAttribute('role', 'region');
            dateGroup.setAttribute('aria-label', `${date} news`);
            
            // Only add the date header if it's not "TODAY"
            if (date !== 'TODAY') {
                dateGroup.innerHTML = `<h2 class="date-header">${date}</h2>`;
            }
            
            newsContent.appendChild(dateGroup);
        }

        const articlesHTML = dateArticles.map((article) => `
            <div class="news-card" role="article">
                <span class="news-indicator" role="img" aria-label="${article.category}">${getNewsIndicator(article)}</span>
                <div class="news-main">
                    <div>
                        <h3 title="${article.title}" onclick="toggleSummary(this)" data-article-id="${article.id}">
                            ${article.title} - ${formatTimeAgo(article.published_at)}
                        </h3>
                        <div class="news-summary">
                            <p>${article.excerpt}</p>
                            <div class="news-summary-meta">
                                <span>${article.source_name}</span>
                                <a href="${article.source_url}" target="_blank" rel="noopener noreferrer">Read full article →</a>
                            </div>
                        </div>
                    </div>
                    <div class="news-source">
                        Source: ${article.source_name}
                    </div>
                </div>
            </div>
        `).join('');

        dateGroup.insertAdjacentHTML('beforeend', articlesHTML);
    });
}

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
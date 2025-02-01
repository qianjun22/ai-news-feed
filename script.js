document.addEventListener('DOMContentLoaded', function() {
    // Sample news data - this would come from your Supabase database later
    const sampleNews = [
        {
            title: 'Latest AI Breakthrough in Natural Language Processing',
            excerpt: 'Researchers develop new transformer model that achieves state-of-the-art results...',
            image: 'https://picsum.photos/seed/ai1/400/300',
            category: 'Research'
        },
        {
            title: 'AI Ethics Guidelines Released',
            excerpt: 'Major tech companies collaborate on new AI ethics framework...',
            image: 'https://picsum.photos/seed/ai2/400/300',
            category: 'Industry'
        },
        {
            title: 'Machine Learning in Healthcare',
            excerpt: 'New AI system shows promising results in early disease detection...',
            image: 'https://picsum.photos/seed/ai3/400/300',
            category: 'Healthcare'
        }
    ];

    function renderNews(articles) {
        const newsContent = document.getElementById('news-content');
        const highlightContent = document.getElementById('highlight-content');
        
        // Render highlight
        const highlight = articles[0];
        highlightContent.innerHTML = `
            <div class="news-card featured">
                <img src="${highlight.image}" alt="${highlight.title}">
                <div class="news-content">
                    <span class="category">${highlight.category}</span>
                    <h3>${highlight.title}</h3>
                    <p>${highlight.excerpt}</p>
                </div>
            </div>
        `;

        // Render other news
        const newsHTML = articles.slice(1).map(article => `
            <div class="news-card">
                <img src="${article.image}" alt="${article.title}">
                <div class="news-content">
                    <span class="category">${article.category}</span>
                    <h3>${article.title}</h3>
                    <p>${article.excerpt}</p>
                </div>
            </div>
        `).join('');

        newsContent.innerHTML = newsHTML;
    }

    // Initialize the news feed
    renderNews(sampleNews);
}); 
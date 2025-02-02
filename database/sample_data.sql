-- Sample data for articles table
INSERT INTO articles (
    title,
    excerpt,
    content,
    source_url,
    source_name,
    category,
    importance_score,
    reading_time_minutes,
    published_at
) VALUES 
-- TODAY's news
(
    'DeepSeek: Separating fact from hype',
    'A comprehensive analysis of the new AI model''s capabilities and limitations',
    'Full article content here...',
    'https://airesearch.daily/deepseek-analysis',
    'AI Research Daily',
    'Analysis',
    4,
    5,
    NOW() - INTERVAL '9 HOURS'
),
(
    'AI agents could birth the first one-person unicorn — but at what societal cost?',
    'Exploring the potential and risks of AI-powered solo entrepreneurship',
    'Full article content here...',
    'https://techcrunch.com/ai-agents-unicorn',
    'TechCrunch',
    'Industry',
    5,
    8,
    NOW() - INTERVAL '10 HOURS'
),
-- YESTERDAY's news
(
    'Guo''s Conviction Partners adds Mike Vernal as GP, raises $230M fund',
    'Major funding news in AI venture capital space',
    'Full article content here...',
    'https://techcrunch.com/guos-conviction-partners',
    'TechCrunch',
    'Funding',
    4,
    5,
    NOW() - INTERVAL '1 DAY'
),
(
    'Meta turns to solar — again — in its data center-building boom',
    'Tech giant''s sustainable approach to AI infrastructure',
    'Full article content here...',
    'https://techcrunch.com/meta-solar-datacenter',
    'TechCrunch',
    'Industry',
    4,
    7,
    NOW() - INTERVAL '1 DAY'
),
(
    'Sam Altman''s ousting from OpenAI has entered the cultural zeitgeist',
    'Analysis of tech leadership drama''s broader cultural impact',
    'Full article content here...',
    'https://techculture.com/altman-openai-culture',
    'Tech Culture Daily',
    'Analysis',
    4,
    8,
    NOW() - INTERVAL '1 DAY'
),
(
    'OpenAI launches o3-mini, its latest ''reasoning'' model',
    'New AI model focuses on enhanced reasoning capabilities',
    'Full article content here...',
    'https://airesearchdaily.com/openai-o3-mini',
    'AI Research Daily',
    'Research',
    5,
    6,
    NOW() - INTERVAL '1 DAY'
),
(
    'Microsoft is forming a new unit to study AI''s impacts',
    'Tech giant establishes dedicated AI ethics research division',
    'Full article content here...',
    'https://techinsider.com/microsoft-ai-impact-unit',
    'Tech Insider',
    'Industry',
    4,
    5,
    NOW() - INTERVAL '1 DAY'
),
(
    'DeepSeek: Everything you need to know about the AI chatbot app',
    'Comprehensive guide to the new AI assistant',
    'Full article content here...',
    'https://aireviews.com/deepseek-guide',
    'AI Reviews',
    'Analysis',
    4,
    10,
    NOW() - INTERVAL '1 DAY'
),
(
    'AI startup Perplexity sued for alleged trademark infringement',
    'Legal challenges emerge in AI startup space',
    'Full article content here...',
    'https://techcrunch.com/perplexity-lawsuit',
    'TechCrunch',
    'Industry',
    3,
    5,
    NOW() - INTERVAL '1 DAY'
),
(
    'DeepSeek lights a fire under Silicon Valley',
    'Impact of new AI model on tech industry dynamics',
    'Full article content here...',
    'https://techinsider.com/deepseek-impact',
    'Tech Insider',
    'Analysis',
    4,
    7,
    NOW() - INTERVAL '1 DAY'
),
(
    'TechCrunch Disrupt 2025: Last 24 hours for 2-for-1 Pass',
    'Tech conference announcement and ticket sales',
    'Full article content here...',
    'https://techcrunch.com/disrupt-2025-passes',
    'TechCrunch',
    'Event',
    3,
    3,
    NOW() - INTERVAL '1 DAY'
),
(
    'Apple Intelligence will support more languages starting in April',
    'Expansion of AI features in Apple ecosystem',
    'Full article content here...',
    'https://techinsider.com/apple-intelligence-languages',
    'Tech Insider',
    'Industry',
    4,
    6,
    NOW() - INTERVAL '2 DAYS'
),
(
    'Intel has already received $2.2B in federal grants for chip production',
    'Government support for semiconductor industry',
    'Full article content here...',
    'https://techcrunch.com/intel-federal-grants',
    'TechCrunch',
    'Funding',
    5,
    7,
    NOW() - INTERVAL '2 DAYS'
); 
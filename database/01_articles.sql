-- Create articles table
CREATE TABLE articles (
    id uuid default uuid_generate_v4() primary key,
    
    -- Basic article info
    title text not null,
    excerpt text not null,
    content text not null,
    
    -- Media and sources
    image_url text,
    source_url text not null,
    source_name text not null,
    
    -- Classification
    category text not null,
    tags text[],
    ai_tools_mentioned text[],
    companies_mentioned text[],
    
    -- Metadata
    author text,
    reading_time_minutes integer,
    importance_score integer check (importance_score between 1 and 5),
    
    -- Timestamps
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    published_at timestamp with time zone not null
);

-- Enable RLS
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow public read access on articles"
    ON articles FOR SELECT TO anon USING (true);

-- Create indexes
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_importance ON articles(importance_score DESC); 
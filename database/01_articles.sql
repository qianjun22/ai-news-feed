-- Create articles table
CREATE TABLE articles (
    id uuid default uuid_generate_v4() primary key,
    
    -- Basic article info
    title text not null,
    excerpt text not null,
    content text,
    
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
    published_at timestamp with time zone not null,
    
    -- New columns
    raw_content jsonb,
    last_fetched_at timestamp with time zone,
    status text DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    
    -- Unique constraint
    CONSTRAINT unique_article_source UNIQUE (source_url, source_name)
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
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_last_fetched ON articles(last_fetched_at DESC);

-- Update RLS policies
CREATE POLICY "Enable read access for active articles"
    ON articles FOR SELECT
    USING (status = 'active');

-- Function to update last_fetched_at
CREATE OR REPLACE FUNCTION update_last_fetched_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_fetched_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update last_fetched_at
CREATE TRIGGER update_articles_last_fetched
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_last_fetched_at();

-- Function to check for duplicate articles
CREATE OR REPLACE FUNCTION check_duplicate_article()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if similar title exists within last 24 hours
    IF EXISTS (
        SELECT 1 FROM articles 
        WHERE title % NEW.title > 0.9  -- Using pg_trgm for similarity
        AND source_name = NEW.source_name
        AND published_at > NOW() - INTERVAL '24 hours'
        AND id != NEW.id
    ) THEN
        RETURN NULL;  -- Prevent insert/update
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to prevent duplicate articles
CREATE TRIGGER prevent_duplicate_articles
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION check_duplicate_article();

-- Remove language column and related index
ALTER TABLE articles 
DROP COLUMN IF EXISTS language;

DROP INDEX IF EXISTS idx_articles_language;

-- Add raw_content column if not exists
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS raw_content jsonb; 
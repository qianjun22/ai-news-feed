-- Create source_articles table for raw data
CREATE TABLE source_articles (
    id uuid default uuid_generate_v4() primary key,
    
    -- Basic article info from source
    title text not null,
    excerpt text,
    content text,
    raw_html text,  -- Store the original HTML
    raw_data jsonb, -- Store any additional raw data
    
    -- Source information
    source_url text not null,
    source_name text not null,
    source_language text not null default 'en',
    
    -- Metadata
    fetch_error text,  -- Store any fetch/parse errors
    last_fetched_at timestamp with time zone default timezone('utc'::text, now()),
    published_at timestamp with time zone,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
    -- Status tracking
    status text not null default 'pending' check (status in ('pending', 'processed', 'error', 'ignored')),
    processed_article_id uuid references articles(id),
    
    -- Constraints
    CONSTRAINT unique_source_article UNIQUE (source_url, source_name),
    
    -- Add hash columns for deduplication
    url_hash text,
    title_hash text
);

-- Enable RLS
ALTER TABLE source_articles ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX idx_source_articles_status ON source_articles(status);
CREATE INDEX idx_source_articles_last_fetched ON source_articles(last_fetched_at DESC);
CREATE INDEX idx_source_articles_source ON source_articles(source_name);
CREATE INDEX idx_source_articles_published ON source_articles(published_at DESC);

-- Create indexes for hash columns
CREATE INDEX IF NOT EXISTS idx_source_articles_url_hash ON source_articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_source_articles_title_hash ON source_articles(title_hash);

-- Update RLS policy for source_articles table
DROP POLICY IF EXISTS "Allow service role access to source_articles" ON source_articles;

-- Allow insert from crawler (using anon key)
CREATE POLICY "Allow insert from crawler"
    ON source_articles 
    FOR INSERT 
    TO anon 
    WITH CHECK (true);

-- Allow read access to all
CREATE POLICY "Allow read access to source_articles"
    ON source_articles 
    FOR SELECT 
    TO anon 
    USING (true);

-- Function to prevent duplicate articles within 24 hours
CREATE OR REPLACE FUNCTION check_duplicate_source_article()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM source_articles 
        WHERE source_name = NEW.source_name
        AND source_url = NEW.source_url
        AND created_at > NOW() - INTERVAL '24 hours'
        AND id != NEW.id
    ) THEN
        RETURN NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for duplicate prevention
CREATE TRIGGER prevent_duplicate_source_articles
    BEFORE INSERT OR UPDATE ON source_articles
    FOR EACH ROW
    EXECUTE FUNCTION check_duplicate_source_article();

-- Function to update articles table when source article is processed
CREATE OR REPLACE FUNCTION process_source_article()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'processed' AND OLD.status != 'processed' THEN
        INSERT INTO articles (
            title,
            excerpt,
            content,
            source_url,
            source_name,
            category,
            language,
            published_at,
            raw_content
        ) VALUES (
            NEW.title,
            NEW.excerpt,
            NEW.content,
            NEW.source_url,
            NEW.source_name,
            'general',  -- Will be updated by AI categorization
            NEW.source_language,
            COALESCE(NEW.published_at, NEW.created_at),
            NEW.raw_data
        ) RETURNING id INTO NEW.processed_article_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for processing
CREATE TRIGGER process_source_article_trigger
    BEFORE UPDATE ON source_articles
    FOR EACH ROW
    WHEN (NEW.status = 'processed' AND OLD.status != 'processed')
    EXECUTE FUNCTION process_source_article(); 
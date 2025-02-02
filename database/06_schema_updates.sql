-- Drop language column and index first
ALTER TABLE articles DROP COLUMN IF EXISTS language;
DROP INDEX IF EXISTS idx_articles_language;

-- Add raw_content column
ALTER TABLE articles ADD COLUMN IF NOT EXISTS raw_content jsonb;

-- Add status column if not exists
ALTER TABLE articles ADD COLUMN IF NOT EXISTS status text DEFAULT 'active';

-- Add status check constraint
ALTER TABLE articles ADD CONSTRAINT valid_status 
    CHECK (status IN ('active', 'archived', 'deleted'));

-- Make content column nullable
ALTER TABLE articles ALTER COLUMN content DROP NOT NULL;

-- Drop old content_hash if exists
ALTER TABLE articles DROP COLUMN IF EXISTS content_hash;
DROP INDEX IF EXISTS idx_articles_content_hash;

-- Add url_hash and title_hash columns
ALTER TABLE articles ADD COLUMN IF NOT EXISTS url_hash text;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS title_hash text;
CREATE INDEX IF NOT EXISTS idx_articles_url_hash ON articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_articles_title_hash ON articles(title_hash);

-- Update RLS policies
DROP POLICY IF EXISTS "Allow public read access on articles" ON articles;
DROP POLICY IF EXISTS "Enable read access for active articles" ON articles;

CREATE POLICY "Allow read access to articles"
    ON articles FOR SELECT
    TO anon
    USING (status = 'active' OR status IS NULL);

CREATE POLICY "Allow insert to articles"
    ON articles FOR INSERT
    TO anon
    WITH CHECK (true);

-- Refresh the schema cache for PostgREST
NOTIFY pgrst, 'reload schema';

-- Add hash columns to source_articles table
ALTER TABLE source_articles ADD COLUMN IF NOT EXISTS url_hash text;
ALTER TABLE source_articles ADD COLUMN IF NOT EXISTS title_hash text;

-- Create indexes for hash columns in source_articles
CREATE INDEX IF NOT EXISTS idx_source_articles_url_hash ON source_articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_source_articles_title_hash ON source_articles(title_hash);

-- Update existing records with hash values
UPDATE source_articles 
SET 
    url_hash = lower(regexp_replace(regexp_replace(source_url, '[^\w\s]', '', 'g'), '\s+', ' ', 'g')),
    title_hash = lower(regexp_replace(regexp_replace(title, '[^\w\s]', '', 'g'), '\s+', ' ', 'g'))
WHERE url_hash IS NULL OR title_hash IS NULL;

-- Refresh the schema cache for PostgREST
NOTIFY pgrst, 'reload schema'; 
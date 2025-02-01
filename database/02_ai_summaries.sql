-- Create AI summaries table
CREATE TABLE ai_summaries (
    id uuid default uuid_generate_v4() primary key,
    article_id uuid references articles(id) on delete cascade,
    
    -- Summary content
    summary_short text not null,
    summary_detailed text not null,
    key_points text[],
    
    -- AI metadata
    model_used text not null,
    prompt_used text,
    
    -- Timestamps
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
ALTER TABLE ai_summaries ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow public read access on summaries"
    ON ai_summaries FOR SELECT TO anon USING (true);

-- Create index
CREATE INDEX idx_summaries_article_id ON ai_summaries(article_id); 
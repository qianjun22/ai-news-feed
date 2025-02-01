-- Create audio content table
CREATE TABLE audio_content (
    id uuid default uuid_generate_v4() primary key,
    article_id uuid references articles(id) on delete cascade,
    
    -- Audio metadata
    duration_seconds integer not null,
    file_url text not null,
    file_size_bytes bigint not null,
    
    -- Publishing info
    spotify_url text,
    apple_podcasts_url text,
    google_podcasts_url text,
    
    -- Voice and generation info
    voice_actor text,
    tts_voice_id text,
    tts_provider text,
    
    -- Status tracking
    status text not null check (status in ('pending', 'processing', 'published', 'failed')),
    
    -- Timestamps
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    published_at timestamp with time zone
);

-- Enable RLS
ALTER TABLE audio_content ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Allow public read access on audio"
    ON audio_content FOR SELECT TO anon USING (true);

-- Create indexes
CREATE INDEX idx_audio_article_id ON audio_content(article_id);
CREATE INDEX idx_audio_status ON audio_content(status); 
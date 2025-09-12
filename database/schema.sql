-- Final Whistle AI Database Schema
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Fixtures table
CREATE TABLE IF NOT EXISTS fixtures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL,
    match_date DATE NOT NULL,
    match_time TIME,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(50) DEFAULT 'scheduled',
    venue VARCHAR(200),
    matchday INTEGER,
    round VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fixture processing status
CREATE TABLE IF NOT EXISTS fixture_processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    crew_execution_id VARCHAR(100),
    articles_generated INTEGER DEFAULT 0,
    topics_generated INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated articles
CREATE TABLE IF NOT EXISTS generated_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    processing_id UUID REFERENCES fixture_processing_status(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    article_type VARCHAR(100) DEFAULT 'match_report',
    word_count INTEGER DEFAULT 0,
    file_path VARCHAR(500),
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status);
CREATE INDEX IF NOT EXISTS idx_fixtures_teams ON fixtures(home_team, away_team);
CREATE INDEX IF NOT EXISTS idx_processing_status ON fixture_processing_status(processing_status);
CREATE INDEX IF NOT EXISTS idx_articles_fixture ON generated_articles(fixture_id);
CREATE INDEX IF NOT EXISTS idx_articles_type ON generated_articles(article_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_fixtures_updated_at BEFORE UPDATE ON fixtures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON generated_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE fixtures ENABLE ROW LEVEL SECURITY;
ALTER TABLE fixture_processing_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_articles ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Public read access for fixtures" ON fixtures
    FOR SELECT USING (true);

CREATE POLICY "Public read access for processing status" ON fixture_processing_status
    FOR SELECT USING (true);

CREATE POLICY "Public read access for articles" ON generated_articles
    FOR SELECT USING (true);

-- Create storage bucket for article images
INSERT INTO storage.buckets (id, name, public) 
VALUES ('article-images', 'article-images', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage policy for article images
CREATE POLICY "Public read access for article images" ON storage.objects
    FOR SELECT USING (bucket_id = 'article-images');

CREATE POLICY "Authenticated upload access for article images" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'article-images' AND auth.role() = 'authenticated');

CREATE POLICY "Authenticated update access for article images" ON storage.objects
    FOR UPDATE USING (bucket_id = 'article-images' AND auth.role() = 'authenticated');

CREATE POLICY "Authenticated delete access for article images" ON storage.objects
    FOR DELETE USING (bucket_id = 'article-images' AND auth.role() = 'authenticated');

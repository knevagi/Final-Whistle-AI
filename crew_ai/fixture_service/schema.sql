-- English Football Fixtures Database Schema
-- This schema is designed for Supabase and stores fixtures for the 2025/26 season

-- Enable UUID extension for Supabase
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Fixtures table to store all match information
CREATE TABLE fixtures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition VARCHAR(100) NOT NULL, -- Premier League, FA Cup, Carabao Cup, etc.
    season VARCHAR(10) NOT NULL, -- 2025/26
    match_date DATE NOT NULL,
    match_time TIME,
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, postponed, cancelled
    venue VARCHAR(200),
    matchday INTEGER, -- Matchday number for league competitions
    round VARCHAR(50), -- Round information for cup competitions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for efficient querying
    CONSTRAINT unique_fixture UNIQUE(competition, season, home_team, away_team, match_date)
);

-- Indexes for performance
CREATE INDEX idx_fixtures_date ON fixtures(match_date);
CREATE INDEX idx_fixtures_status ON fixtures(status);
CREATE INDEX idx_fixtures_competition ON fixtures(competition);
CREATE INDEX idx_fixtures_teams ON fixtures(home_team, away_team);

-- Fixture processing status table to track which fixtures have been processed
CREATE TABLE fixture_processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    error_message TEXT,
    crew_execution_id VARCHAR(100), -- To track crew AI execution
    articles_generated INTEGER DEFAULT 0,
    topics_generated INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_fixture_processing UNIQUE(fixture_id)
);

-- Indexes for processing status
CREATE INDEX idx_processing_status ON fixture_processing_status(processing_status);
CREATE INDEX idx_processing_date ON fixture_processing_status(processed_at);

-- Generated articles table to store the articles created by the crew
CREATE TABLE generated_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id UUID REFERENCES fixtures(id) ON DELETE CASCADE,
    processing_id UUID REFERENCES fixture_processing_status(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    article_type VARCHAR(100), -- match_report, player_analysis, tactical_analysis, etc.
    word_count INTEGER,
    file_path VARCHAR(500), -- Path to saved markdown file
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for articles
CREATE INDEX idx_articles_fixture ON generated_articles(fixture_id);
CREATE INDEX idx_articles_type ON generated_articles(article_type);
CREATE INDEX idx_articles_date ON generated_articles(created_at);

-- Teams table to store team information
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    short_name VARCHAR(10),
    league VARCHAR(100), -- Premier League, Championship, etc.
    city VARCHAR(100),
    stadium VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for teams
CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_league ON teams(league);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_fixtures_updated_at BEFORE UPDATE ON fixtures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_status_updated_at BEFORE UPDATE ON fixture_processing_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON generated_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get fixtures that need processing (completed matches that haven't been processed)
CREATE OR REPLACE FUNCTION get_unprocessed_completed_fixtures()
RETURNS TABLE (
    fixture_id UUID,
    competition VARCHAR(100),
    match_date DATE,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.competition,
        f.match_date,
        f.home_team,
        f.away_team,
        f.home_score,
        f.away_score,
        f.status
    FROM fixtures f
    LEFT JOIN fixture_processing_status fps ON f.id = fps.fixture_id
    WHERE f.status = 'completed'
    AND (fps.fixture_id IS NULL OR fps.processing_status != 'completed')
    ORDER BY f.match_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample teams for the 2025/26 Premier League season
INSERT INTO teams (name, short_name, league, city, stadium) VALUES
('Arsenal', 'ARS', 'Premier League', 'London', 'Emirates Stadium'),
('Aston Villa', 'AVL', 'Premier League', 'Birmingham', 'Villa Park'),
('Bournemouth', 'BOU', 'Premier League', 'Bournemouth', 'Vitality Stadium'),
('Brentford', 'BRE', 'Premier League', 'London', 'Gtech Community Stadium'),
('Brighton & Hove Albion', 'BHA', 'Premier League', 'Brighton', 'Amex Stadium'),
('Burnley', 'BUR', 'Premier League', 'Burnley', 'Turf Moor'),
('Chelsea', 'CHE', 'Premier League', 'London', 'Stamford Bridge'),
('Crystal Palace', 'CRY', 'Premier League', 'London', 'Selhurst Park'),
('Everton', 'EVE', 'Premier League', 'Liverpool', 'Goodison Park'),
('Fulham', 'FUL', 'Premier League', 'London', 'Craven Cottage'),
('Leicester City', 'LEI', 'Premier League', 'Leicester', 'King Power Stadium'),
('Liverpool', 'LIV', 'Premier League', 'Liverpool', 'Anfield'),
('Manchester City', 'MCI', 'Premier League', 'Manchester', 'Etihad Stadium'),
('Manchester United', 'MUN', 'Premier League', 'Manchester', 'Old Trafford'),
('Newcastle United', 'NEW', 'Premier League', 'Newcastle', 'St James'' Park'),
('Nottingham Forest', 'NFO', 'Premier League', 'Nottingham', 'City Ground'),
('Southampton', 'SOU', 'Premier League', 'Southampton', 'St Mary''s Stadium'),
('Tottenham Hotspur', 'TOT', 'Premier League', 'London', 'Tottenham Hotspur Stadium'),
('West Ham United', 'WHU', 'Premier League', 'London', 'London Stadium'),
('Wolverhampton Wanderers', 'WOL', 'Premier League', 'Wolverhampton', 'Molineux Stadium')
ON CONFLICT (name) DO NOTHING;

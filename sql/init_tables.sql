CREATE TABLE IF NOT EXISTS social_media_schema.social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255) NOT NULL,
    platform_author_id VARCHAR(255) NOT NULL,
    author_username VARCHAR(255),
    content TEXT,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    engagement_score INTEGER GENERATED ALWAYS AS (likes_count + comments_count + shares_count) STORED,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, platform_post_id)
);

CREATE TABLE IF NOT EXISTS social_media_schema.daily_stats (
    id SERIAL PRIMARY KEY,
    collection_date DATE DEFAULT CURRENT_DATE,
    platform VARCHAR(50) NOT NULL,
    posts_collected INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    avg_engagement DECIMAL(10,2) DEFAULT 0,
    max_engagement INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(collection_date, platform)
);

CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_media_schema.social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_posts_published_at ON social_media_schema.social_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_social_posts_engagement ON social_media_schema.social_posts(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_collected_at ON social_media_schema.social_posts(collected_at);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON social_media_schema.daily_stats(collection_date DESC);

CREATE OR REPLACE FUNCTION social_media_schema.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_social_posts_updated_at 
    BEFORE UPDATE ON social_media_schema.social_posts 
    FOR EACH ROW EXECUTE FUNCTION social_media_schema.update_updated_at_column();

CREATE VIEW social_media_schema.posts_summary AS
SELECT 
    platform,
    COUNT(*) as total_posts,
    AVG(engagement_score) as avg_engagement,
    MAX(engagement_score) as max_engagement,
    MIN(engagement_score) as min_engagement,
    DATE(collected_at) as collection_date
FROM social_media_schema.social_posts
GROUP BY platform, DATE(collected_at)
ORDER BY collection_date DESC, avg_engagement DESC;

CREATE VIEW social_media_schema.top_posts AS
SELECT 
    platform,
    content,
    engagement_score,
    likes_count,
    comments_count,
    shares_count,
    published_at,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY engagement_score DESC) as rank_in_platform
FROM social_media_schema.social_posts
ORDER BY engagement_score DESC;

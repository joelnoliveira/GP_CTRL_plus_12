-- Create database schema and seed data
-- This SQL file creates tables and populates them with initial data
-- SQLAlchemy will reflect these tables at runtime

-- This is an example for testing replace with the real values later
-- Create users table
-- CREATE TABLE IF NOT EXISTS users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR(50) UNIQUE NOT NULL,
--     email VARCHAR(100) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Create posts table
-- CREATE TABLE IF NOT EXISTS posts (
--     id SERIAL PRIMARY KEY,
--     user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
--     title VARCHAR(200) NOT NULL,
--     content TEXT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Create comments table (NEW)
-- CREATE TABLE IF NOT EXISTS comments (
--     id SERIAL PRIMARY KEY,
--     post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
--     user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
--     comment_text TEXT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Insert sample data
-- INSERT INTO users (username, email) VALUES
--     ('alice', 'alice@example.com'),
--     ('bob', 'bob@example.com'),
--     ('charlie', 'charlie@example.com')
-- ON CONFLICT (username) DO NOTHING;

-- INSERT INTO posts (user_id, title, content) VALUES
--     (1, 'First Post', 'This is Alice''s first post'),
--     (1, 'Second Post', 'Alice posting again'),
--     (2, 'Bob''s Post', 'Hello from Bob'),
--     (3, 'Charlie Here', 'Charlie''s thoughts')
-- ON CONFLICT DO NOTHING;

-- -- Insert sample comments
-- INSERT INTO comments (post_id, user_id, comment_text) VALUES
--     (1, 2, 'Great post, Alice!'),
--     (1, 3, 'I agree with Bob'),
--     (3, 1, 'Thanks for sharing, Bob'),
--     (4, 2, 'Interesting thoughts, Charlie')
-- ON CONFLICT DO NOTHING;

-- -- Insert sample comments (NEW)
-- INSERT INTO comments (post_id, user_id, comment_text) VALUES
--     (1, 2, 'Great post, Alice!'),
--     (1, 3, 'I agree with Bob'),
--     (3, 1, 'Thanks for sharing, Bob'),
--     (4, 2, 'Interesting thoughts, Charlie')
-- ON CONFLICT DO NOTHING;
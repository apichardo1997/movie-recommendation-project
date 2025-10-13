/*==============================================================================
 Create the raw tables corresponding to the csv files
==============================================================================*/

-- For the movies
DROP TABLE IF EXISTS movies_raw;
CREATE TABLE movies_raw (
    movieId INTEGER,
    title TEXT,
    genres TEXT
);

-- For the ratings
DROP TABLE IF EXISTS ratings_raw;
CREATE TABLE ratings_raw (
    userId INTEGER,
    movieId INTEGER,
    rating DECIMAL(2, 1),
	timestamp INTEGER
);

/*==============================================================================
 Ingest the data from the csv files
==============================================================================*/

\copy movies_raw (movieID, title, genres) FROM 'data/movies.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
\copy ratings_raw (userId, movieId, rating, timestamp) FROM 'data/ratings.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');


/*==============================================================================
Drop all tables if they exist
==============================================================================*/

DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS movies; 
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS users;

/*==============================================================================
Create and populate the users table
==============================================================================*/

-- Create table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY
);

-- Insert unique user IDs from ratings_raw
INSERT INTO users (user_id)
SELECT DISTINCT userId 
FROM (
    SELECT userId FROM ratings_raw
) AS all_users
ORDER BY userId;

/*==============================================================================
 Create and populate the movies table
==============================================================================*/

-- Create normalized movies table (without genres column)
CREATE TABLE movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

-- Populate movies table 
INSERT INTO movies (movie_id, title)
SELECT movieId, title
FROM movies_raw;

/*==============================================================================
 Create and populate genres table
==============================================================================*/


-- Create genres table 
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE NOT NULL
);

-- Extract and insert unique genres
INSERT INTO genres (genre_name)
SELECT DISTINCT TRIM(genre)
FROM (
    SELECT UNNEST(string_to_array(genres, '|')) AS genre
    FROM movies_raw
    WHERE genres != '(no genres listed)'
) AS split_genres;

/*==============================================================================
 Create and populate movies_genres junction table
==============================================================================*/

-- Create the movie_genres junction table (many-to-many)
CREATE TABLE movie_genres (
    movie_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Index for reverse genre lookups ("movies in genre X")
CREATE INDEX idx_movie_genres_genre_id ON movie_genres(genre_id);

-- Populate movie_genres junction table
INSERT INTO movie_genres (movie_id, genre_id)
SELECT DISTINCT 
    mr.movieId,
    g.genre_id
FROM movies_raw mr
CROSS JOIN LATERAL (
    SELECT UNNEST(string_to_array(mr.genres, '|')) AS genre_name
) AS split
JOIN genres g ON TRIM(split.genre_name) = g.genre_name
WHERE mr.genres != '(no genres listed)';

/*==============================================================================
 Create and populate ratings table
==============================================================================*/

-- Create normalized ratings table
CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    UNIQUE(user_id, movie_id)  -- Prevent duplicate ratings
);

-- Add indexes for foreign keys 
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id);

-- Populate from ratings_raw
INSERT INTO ratings (user_id, movie_id, rating, timestamp)
SELECT 
	userId, 
	movieId, 
	rating, 
	to_timestamp(timestamp)
FROM ratings_raw; 

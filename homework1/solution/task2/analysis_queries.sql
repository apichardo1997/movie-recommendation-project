/*==============================================================================
2.1
==============================================================================*/

SELECT 
  'movies' as table_name, 
  COUNT(*) as row_count 
FROM movies
UNION ALL
SELECT 
  'genres' as table_name, 
  COUNT(*) as row_count 
FROM genres
UNION ALL
SELECT 
  'movie_genres' as table_name, 
  COUNT(*) as row_count 
FROM movie_genres
UNION ALL
SELECT 
  'users' as table_name, 
  COUNT(*) as row_count 
FROM users
UNION ALL
SELECT 
  'ratings' as table_name, 
  COUNT(*) as row_count 
 FROM ratings

/*==============================================================================
2.2 (100 for small dataset)
==============================================================================*/


WITH RATING_AGGS AS (
	SELECT
		movie_id,
		AVG(rating) AS avg_rating, 
		COUNT(*) as n_ratings
	FROM public.ratings
	GROUP BY movie_id
	HAVING COUNT(*) >= 1000
	ORDER BY AVG(rating) DESC
	LIMIT 20
) 
SELECT 
	m.title, 
	ra.avg_rating,
	ra.n_ratings
FROM rating_aggs ra 
JOIN movies m 
ON ra.movie_id = m.movie_id;


/*==============================================================================
2.3
==============================================================================*/

SELECT 
    g.genre_name,
    COUNT(mg.movie_id) AS movie_count
FROM genres g
JOIN movie_genres mg ON g.genre_id = mg.genre_id
GROUP BY g.genre_id, g.genre_name
ORDER BY movie_count DESC;
/*==============================================================================
I was a bit skeptical about the implementation of the normalization process
of the genres, so I decided to verify it by comparing the normalized data with
the original raw data. The query below reconstructs the genres column from the
 normalized tables and compares it with the original movies_raw table. 
 If everything is correct, the result should be empty.

The query should be run twice; once to check for any discrepancies in one direction,
and then again in the opposite direction by swapping the two SELECT statements.
==============================================================================*/

WITH normalized_data as (
	SELECT 
	    m.movie_id, 
	    m.title,
	    COALESCE(
	        array_to_string(
	            array_agg(
	                g.genre_name 
	                ORDER BY 
	                    CASE WHEN g.genre_name = 'IMAX' THEN 1 ELSE 0 END,
	                    g.genre_name
	            ) FILTER (WHERE g.genre_name IS NOT NULL), 
	            '|'
	        ), 
	        '(no genres listed)'
	    ) as genres
	FROM public.movies m 
	LEFT JOIN public.movie_genres mg ON m.movie_id = mg.movie_id 
	LEFT JOIN public.genres g ON mg.genre_id = g.genre_id
	GROUP BY m.movie_id, m.title
	ORDER BY m.movie_id
)
(SELECT * FROM normalized_data)
EXCEPT
(SELECT * FROM movies_raw);
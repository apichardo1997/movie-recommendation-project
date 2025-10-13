## General approach 

This exemplary solution creates a normalized database with the following tables: 
1. `movies` 
2. `users` 
3. `genres` 
4. `movie_genres` (junction table for many-to-many relationship)
5. `ratings`

For data ingestion it uses a simple ETL-like approach, in which 
1. the raw data is ingested as it is into raw tables 
2. the data is then ingested and transformed into the final tables from the raw tables 


## Highlights 

### Normalization 
Two main normalizations: 
1. A separate `users` table with the `user_id` values 
2. A separate `genres` table with the genres, involving some string processing 


### Constraints 
1. Constraining `ratings.rating` to values between 0.5 and 5
2. Preventing duplicate ratings

### Performance 
1. Indexes on all foreign keys, beyond the default indexes on primary keys

### Other 
1. Filtering out the `(no genres listed)` when ingesting into `generes`
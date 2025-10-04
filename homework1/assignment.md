# Homework 1
You are tasked to build the data architecture for a movie recommendation product. As a start, you want to build an MVP based on the MovieLens dataset that allows you to: 
- Build a simple application 
- Do some analytics 
- Do some ML 

## Tasks

1. Build the database in postgres
    1. Download the [movielens](https://grouplens.org/datasets/movielens/latest/) dataset. Use the full dataset if you are comfortable; use the small version otherwise, particularly if you are experiencing performance issues. The choice here won't affect your grade. As a reference, full data ingestion costs me approx 6 min with the full version, the analytical queries a few seconds. 
    2. Design and implement a database in postgres that contains the data from the following 2 csv files: movies, ratings. Follow the best practices for relational database design in postgres that you have learned in the course so far. 
    3. Ingest the data from the 2 csv files into your database (e.g. via an SQL script, or the pgadmin import function)
2. Perform the following exploratory analyses: 
    1. Count the number of records in each table of your database.
    2. Identify the 20 most popular movies by average rating. Only include those that have received at least 1,000 ratings. Return, for each of the 20 movies, the movie title, the average rating and the number of ratings, in descending order of popularity. 
    3. Identify the most frequent genres. Return the genre names and the count of movies.

## Deliverables 
To be delivered in a PR in your forked repo in a directory `homework1/solution`: 
1. `task1/create_database.sql` - single SQL script that creates your database (and populates it if you populate via a script) 
2. `task1/explanation.md` - a brief markdown file explaining what you did. Bullet points are fine. If you perform any manual steps outside of the SQL scripts, please mention it.  
3. `task2/analysis_queries.sql` - one sql script with the 3 queries 
4. `task2/analysis_results.md` or `task_2/analysis_results.PDF` - the results of the 3 queries. Screenshots are fine. 

## Timeline 

To be submitted by Sunday, October 12, 23:59

## Additional information 

1. This is an individual assignment.  
2. If you get completely stuck at a particular step, run out of time and there are shortcuts, take the shortcut and make a note. It is better to submit something imperfect compared to not submitting anything. 
3. Evaluation will be based on 
    1. Database design quality (normalization, constraints, performance)
    2. Query correctness and efficiency
    3. Handling of data quality issues
    4. Clear documentation

If you have major concerns or anything is unclear, please get in touch. 

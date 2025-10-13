# Homework 2
You continue with the project from homework 1, leveraging the exemplary solution. After prototyping the database in raw SQL, you know want to implement it 
properly in SQLalchemy to prepare a production application on top of it. 

## Tasks

1. Create the database in sqlAlchemy + alembic: 
    1. Create the models 
    2. Create the necessary data migrations in Alembic to create the tables - you may want to get rid of the exemplary model first
    3. Implement a data ingestion ETL in a python script using SQLalchemy (ORM or core)
2. Perform the following exploratory analyses using SQLalchemy (ORM or core) 
    1. Identify the top 10 highest-ranking genres by average rating. Show the genre name and the average rating in descending order
    2. Find the 10 most polarizing movies, defined by the standard deviation of their ratings. Consider only movies with at least 1000 ratings (100 for small dataset).
    3. Build a time series with the total monthly count of ratings. 

## Deliverables 
To be delivered in a PR in your forked repo:
1. `server/models/*` - the models/tables in SQLalchemy 
2. `alembic/versions/*` - the alembic migration(s) 
3. `scripts/populate_database.py` - the data ingestion script using SQLalchemy (ORM or core)
4. `scripts/run_analysis_queries.py` - the analytics queries using SQLalchemy (ORM or core)
5. `homework2/solution/analysis_queries_result.md / pdf` - the results of your queries. Screenshots are fine. 


## Timeline 

To be submitted by Saturday, October 18, 20:00

## Additional information 

1. This is an individual assignment.  
2. If you get completely stuck at a particular step, run out of time and there are shortcuts, take the shortcut and make a note. It is better to submit something imperfect compared to not submitting anything. 
3. Evaluation will be based on 
    1. Code organization and readibility
    2. Correctness and completeness
    3. Handling of data quality issues
    4. Clear documentation

If you have major concerns or anything is unclear, please get in touch. 

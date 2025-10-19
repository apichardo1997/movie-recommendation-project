# Final assignment
Now that you have successfully designed a datamodel and implemented it in python and built a data ingestion ETL, you want to build a simple first REST API, such that a simple prototype can be built. You have aligned with the project's FE developer and have agreed on the first endpoints to build. The FE developer will develop a FE against the specified backend.

As previously, you can either use the small or the big dataset for this task.

## Tasks

1. Build a fastAPI REST API. Structure the API according to [this](https://viktorsapozhok.github.io/fastapi-oauth2-postgres/) article. Details outlined in deliverables.
2. Implement the following endpoints:
    1. Movies
        1. `GET api/rest/v1/movies`. The listing endpoint for movies. This endpoint shall support the following query parameters:
            1. `limit` and `page` for pagination, e.g. `GET api/rest/v1/movies?limit=10&page=1`, with defaults as seen in example path (10, 1)
            2. `search` (optional), e.g. `GET api/rest/v1/movies?limit=10&page=1&search=thriller`, in which the search parameter performs a text search across `Movie.title` and `Genre.genre_name`. Design the search according to what you think works best in a movie search page.
            3. Response schema:
            ```json
            {
                "movies": [...],
                "total": 150,
                "page": 1,
                "limit": 10
            }
            ```
        2. `GET api/rest/v1/movies/{id}/avg-rating`. An endpoint to get the avg-rating of each movie. Response schema:
        ```json
            {
                "movie_id": 1,
                "title": "title",
                "avg_rating": 4.2,
                "total_ratings": 10
            }
        ```
    2. Ratings
        1. `POST api/rest/v1/ratings`. An endpoint to add a rating to the database. The body shall have the following schema: `{"user_id": 1, "movie_id": 1, "rating": 2.0}`. It should return the created resource:
        ```json
            {
                "rating_id": 1,
                "user_id": 1,
                "movie_id": 1,
                "rating": 2.5,
                "timestamp": "2024-10-30T14:30:00"
            }
        ```
    3. Recommendation engine
        1. `POST api/rest/v1/recommendation-engine`. The endpoint to train a recommendation model based on the latest user data in the DB. Empty response.
            1. For the simple prototype, use something quick and simple that works, e.g non-negative matrix factorization in the sklearn implementation. Do not spend any time on model optimization unless you are adventerous.
            2. This endpoint should train and store the latest model somewhere (e.g. in a new database table, in a local directory in your application to mock a datalake, or similar). In the future we may want to support versioning, so this endpoint should not just overwrite the previous model.
        2. `GET api/rest/v1/user/{id}/recommended-movies`. The endpoint to get the recommended movies for each user:
            1. This endpoint shall support the query parameter `n`, e.g. `GET api/rest/v1/user/{id}/recommended-movies?n=10`, for the amount of movies, defaulting to `10`.
            2. We neglect for now that in a production setting, we will want to filter out those movies that the user has already seen.
            3. It should return an array of ids of the movies with highest probability that the user will like them, starting with the highest one:
            ```json
                {
                    "movie_ids": [1, 2, ...],
                    "probabilities": [0.1, 0.8, ...]
                }
            ```
3. Bonus:
    1. Implement automatic tests in pytest on the service level.
    2. Implement automatic tests on the router-level, mocking out the services.
    3. `POST api/rest/v1/recommendation-engine` can take a longer time in the future when data grows and the recommendation engine becomes more complex. Move this to an async workload via fastAPI background tasks.


## Deliverables
To be delivered in a PR in your forked repo:
1. A fully working prototype in the style of previous homeworks. This includes but may not be limited to the following:
    1. `server/app.py` - the fastAPI app.
    2. `server/routers/*` - the routers corresponding to the endpoints to be implemented. One python module for each top-level route, so `server/routers/movies.py`, `server/routers/ratings.py`, ...
    3. `server/services/*` - the service modules containing the services and the datamanagers, following the structure of the routers.
    4. `server/schemas/*` - the pydantic schemas corresponding to the models that your services and routers use, so `Movie`, `Genre`, ...
2. A short explanation explaining what you did in `final_project/solution/explanation.md`

## Timeline

To be submitted by Thursday, Octobre 30, 14:00 - 2.5h before the start of the first presentations.

## Additional information

1. This is a group assignment completed in groups of no more than 4. Please communicate the group composition to me asap (one email per group) - I need to know the amount of groups for scheduling reasons.
2. The presentation will be a meeting in which I will be the FE developer and tech lead of the project. You will be expected to guide me through your implementation and run some tests. Please have [Postman](https://www.postman.com/) or something similar installed on the machine from which you will be presenting.
3. Evaluation will be based on
    1. Code organization and readability
    2. Correctness and completeness
    3. Clear documentation
    4. Presentation and answering of questions

If you have major concerns or anything is unclear, please get in touch.

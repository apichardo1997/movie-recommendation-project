📁 Movie Recommendation API

  📁 DEMO 
    ✓ 1. Get Movies (default)
    ✓ 2. Search Movies
    ✓ 3. Get Movie Rating
    ✓ 4. Create Rating
    ✓ 5. Train Recommendation Model
    ✓ 6. Get User Recommendations
    
  📁 Movies - List & Search
    ✓ Get Movies (default)
    ✓ Get Movies (with pagination)
    ✓ Get Movies (with search)
    ✓ Get Movies (with sorting)
    ✓ Get Movies (combined: search + sort + pagination)
    ✓ [EDGE] Invalid limit (too high)
    ✓ [EDGE] Invalid page (negative)
    ✓ [EDGE] Empty search results
    
  📁 Movies - Average Rating
    ✓ Get Rating (valid movie)
    ✓ Get Rating (movie with no ratings)
    ✓ [ERROR] Movie not found
    ✓ [ERROR] Invalid movie ID (negative)
    
  📁 Ratings - Create/Update
    ✓ Create Rating (first time)
    ✓ Update Rating (same user/movie)
    ✓ [ERROR] User not found
    ✓ [ERROR] Movie not found
    ✓ [ERROR] Rating too high (>5.0)
    ✓ [ERROR] Rating too low (<0.5)
    
  📁 Recommend1ations
    ✓ Train Model
    ✓ Get User Recommendations (valid user)
    ✓ Get User Recommendations (with custom n)
    ✓ [ERROR] User not found
    ✓ [EDGE] Get recommendations before training model (optional)
    ✓ [EDGE] New user with no ratings (optional)
    
  📁 System Health
    ✓ Health Check
    ✓ Root Endpoint
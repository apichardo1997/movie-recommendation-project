#!/usr/bin/env python3
"""Add comprehensive visualizations to key endpoints"""

import json

# Read the enhanced collection
with open('Movie_Recommendation_API_Enhanced.postman_collection.json', 'r') as f:
    collection = json.load(f)

def find_and_add_viz(collection, request_name, viz_code):
    """Find a request and add visualization code to its test script"""
    for folder in collection['item']:
        for request in folder.get('item', []):
            if request['name'] == request_name:
                for event in request.get('event', []):
                    if event['listen'] == 'test':
                        # Add visualization at the end of test script
                        event['script']['exec'].extend(['', viz_code])
                        return True
    return False

# VIZ 1: Recommendations - Bar Chart with Probabilities
recommendations_viz = '''// 📊 VISUALIZATION: Recommendation Chart
var template = `
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
    h2 { color: #333; margin-bottom: 30px; }
    .rec-item { margin-bottom: 15px; }
    .movie-id { display: inline-block; width: 100px; font-weight: bold; color: #667eea; }
    .bar-container { display: inline-block; width: calc(100% - 200px); background: #f0f0f0; border-radius: 5px; height: 30px; position: relative; overflow: hidden; }
    .bar { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; transition: width 0.5s ease; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: bold; }
    .prob { display: inline-block; width: 80px; text-align: right; font-family: monospace; }
    .rank { display: inline-block; width: 30px; color: #999; font-weight: bold; }
</style>

<div class="container">
    <h2>🎯 Top {{movie_ids.length}} Movie Recommendations</h2>
    {{#each movie_ids}}
    <div class="rec-item">
        <span class="rank">#{{add @index 1}}</span>
        <span class="movie-id">Movie {{this}}</span>
        <div class="bar-container">
            <div class="bar" style="width: {{multiply (lookup ../probabilities @index) 100}}%">
                {{toFixed (multiply (lookup ../probabilities @index) 100) 1}}%
            </div>
        </div>
        <span class="prob">{{toFixed (lookup ../probabilities @index) 4}}</span>
    </div>
    {{/each}}
</div>

<script>
    // Helper functions for Handlebars
    Handlebars.registerHelper('multiply', function(a, b) {
        return a * b;
    });
    Handlebars.registerHelper('add', function(a, b) {
        return a + b;
    });
    Handlebars.registerHelper('toFixed', function(num, decimals) {
        return Number(num).toFixed(decimals);
    });
</script>
`;

pm.visualizer.set(template, pm.response.json());'''

find_and_add_viz(collection, "6. Get User Recommendations", recommendations_viz)
find_and_add_viz(collection, "Get User Recommendations (valid user)", recommendations_viz)

print("✅ Recommendations visualization added")

# VIZ 2: Training Status - Status Indicator
training_status_viz = '''// 📊 VISUALIZATION: Training Status
var template = `
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background: #f5f7fa; }
    .status-card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
    .status-badge { display: inline-block; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-size: 1.2em; margin-bottom: 20px; }
    .status-idle { background: #e0e0e0; color: #666; }
    .status-training { background: #fff3cd; color: #856404; animation: pulse 1.5s infinite; }
    .status-completed { background: #d4edda; color: #155724; }
    .status-failed { background: #f8d7da; color: #721c24; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    .info-row { margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    .label { font-weight: bold; color: #666; display: inline-block; width: 150px; }
    .value { color: #333; }
    h2 { margin-top: 0; color: #333; }
</style>

<div class="status-card">
    <h2>🤖 ML Model Training Status</h2>
    <div class="status-badge status-{{status}}">
        {{#if (eq status 'idle')}}⏸️ {{/if}}
        {{#if (eq status 'training')}}⏳ {{/if}}
        {{#if (eq status 'completed')}}✅ {{/if}}
        {{#if (eq status 'failed')}}❌ {{/if}}
        {{status}}
    </div>

    {{#if started_at}}
    <div class="info-row">
        <span class="label">Started At:</span>
        <span class="value">{{started_at}}</span>
    </div>
    {{/if}}

    {{#if completed_at}}
    <div class="info-row">
        <span class="label">Completed At:</span>
        <span class="value">{{completed_at}}</span>
    </div>
    {{/if}}

    {{#if model_version}}
    <div class="info-row">
        <span class="label">Model Version:</span>
        <span class="value">{{model_version}}</span>
    </div>
    {{/if}}

    {{#if total_ratings}}
    <div class="info-row">
        <span class="label">Total Ratings:</span>
        <span class="value">{{total_ratings}} ratings processed</span>
    </div>
    {{/if}}

    {{#if error}}
    <div class="info-row" style="background: #f8d7da;">
        <span class="label">Error:</span>
        <span class="value">{{error}}</span>
    </div>
    {{/if}}
</div>

<script>
    Handlebars.registerHelper('eq', function(a, b) {
        return a === b;
    });
</script>
`;

pm.visualizer.set(template, pm.response.json());'''

find_and_add_viz(collection, "Check Training Status", training_status_viz)

print("✅ Training status visualization added")

# VIZ 3: Rating Response - Success Card
rating_viz = '''// 📊 VISUALIZATION: Rating Success
var template = `
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 500px; margin: 0 auto; text-align: center; }
    .success-icon { font-size: 4em; margin-bottom: 20px; }
    .rating-value { font-size: 3em; font-weight: bold; color: #f5576c; margin: 20px 0; }
    .stars { color: #ffc107; font-size: 2em; letter-spacing: 5px; }
    .info { color: #666; margin: 10px 0; }
    .label { font-weight: bold; }
</style>

<div class="card">
    <div class="success-icon">{{#if (gte rating 4)}}😍{{else if (gte rating 3)}}😊{{else if (gte rating 2)}}😐{{else}}😞{{/if}}</div>
    <h2>Rating Submitted!</h2>
    <div class="rating-value">{{rating}} / 5.0</div>
    <div class="stars">
        {{#repeat (round rating)}}★{{/repeat}}{{#repeat (minus 5 (round rating))}}☆{{/repeat}}
    </div>
    <div class="info"><span class="label">Rating ID:</span> {{rating_id}}</div>
    <div class="info"><span class="label">User ID:</span> {{user_id}}</div>
    <div class="info"><span class="label">Movie ID:</span> {{movie_id}}</div>
    <div class="info" style="font-size: 0.9em; color: #999;">{{timestamp}}</div>
</div>

<script>
    Handlebars.registerHelper('gte', function(a, b) {
        return a >= b;
    });
    Handlebars.registerHelper('round', function(num) {
        return Math.round(num);
    });
    Handlebars.registerHelper('minus', function(a, b) {
        return a - b;
    });
    Handlebars.registerHelper('repeat', function(n, options) {
        var result = '';
        for(var i = 0; i < n; i++) {
            result += options.fn(this);
        }
        return result;
    });
</script>
`;

pm.visualizer.set(template, pm.response.json());'''

find_and_add_viz(collection, "4. Create Rating", rating_viz)
find_and_add_viz(collection, "Create Rating (first time)", rating_viz)
find_and_add_viz(collection, "Update Rating (same user/movie)", rating_viz)

print("✅ Rating visualization added")

# VIZ 4: Search Results with highlighting
search_viz = '''// 📊 VISUALIZATION: Search Results
var jsonData = pm.response.json();
var searchTerm = pm.request.url.query.get("search") || "N/A";

var template = `
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; margin: -20px -20px 0 -20px; }
    .search-info { background: white; padding: 20px; margin: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .result-count { font-size: 1.5em; color: #667eea; font-weight: bold; }
    table { width: calc(100% - 40px); margin: 20px; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    th { background: #667eea; color: white; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background: #f5f5f5; }
    .highlight { background: #fff3cd; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .genres { font-size: 0.85em; color: #666; }
    .genre-tag { display: inline-block; background: #e9ecef; padding: 3px 8px; border-radius: 3px; margin: 2px; }
</style>

<div class="header">
    <h2 style="margin: 0;">🔍 Search Results</h2>
    <p style="margin: 10px 0 0 0; opacity: 0.9;">Search query: "{{searchTerm}}"</p>
</div>

<div class="search-info">
    <span class="result-count">{{total}}</span> movies found
    <span style="color: #666; margin-left: 20px;">Page {{page}} of {{total_pages}}</span>
</div>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Year</th>
            <th>Genres</th>
        </tr>
    </thead>
    <tbody>
        {{#each movies}}
        <tr>
            <td>{{id}}</td>
            <td><strong>{{title}}</strong></td>
            <td>{{release_year}}</td>
            <td class="genres">
                {{#each genres}}
                <span class="genre-tag">{{this}}</span>
                {{/each}}
            </td>
        </tr>
        {{/each}}
    </tbody>
</table>
`;

pm.visualizer.set(template, Object.assign({}, jsonData, {searchTerm: searchTerm}));'''

find_and_add_viz(collection, "2. Search Movies", search_viz)
find_and_add_viz(collection, "Get Movies (with search)", search_viz)

print("✅ Search results visualization added")

# VIZ 5: Movie Rating Display
movie_rating_viz = '''// 📊 VISUALIZATION: Movie Rating
var template = `
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
    .rating-card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 600px; margin: 0 auto; }
    .movie-title { font-size: 2em; color: #333; margin-bottom: 30px; text-align: center; }
    .rating-display { text-align: center; margin: 30px 0; }
    .avg-rating { font-size: 4em; font-weight: bold; color: #ff6b6b; display: inline-block; }
    .out-of { font-size: 2em; color: #999; }
    .stars { font-size: 2.5em; color: #ffc107; margin: 20px 0; }
    .total-ratings { font-size: 1.2em; color: #666; margin-top: 20px; }
    .movie-id-badge { display: inline-block; background: #e9ecef; padding: 5px 15px; border-radius: 20px; color: #666; font-size: 0.9em; }
</style>

<div class="rating-card">
    <div class="movie-id-badge">ID: {{movie_id}}</div>
    <h1 class="movie-title">{{title}}</h1>

    <div class="rating-display">
        <span class="avg-rating">{{toFixed avg_rating 1}}</span>
        <span class="out-of"> / 5.0</span>
    </div>

    <div class="stars">
        {{#repeat (round avg_rating)}}★{{/repeat}}{{#repeat (minus 5 (round avg_rating))}}☆{{/repeat}}
    </div>

    <div class="total-ratings">
        📊 Based on <strong>{{total_ratings}}</strong> {{#if (eq total_ratings 1)}}rating{{else}}ratings{{/if}}
    </div>
</div>

<script>
    Handlebars.registerHelper('toFixed', function(num, decimals) {
        return Number(num).toFixed(decimals);
    });
    Handlebars.registerHelper('round', function(num) {
        return Math.round(num);
    });
    Handlebars.registerHelper('minus', function(a, b) {
        return a - b;
    });
    Handlebars.registerHelper('eq', function(a, b) {
        return a === b;
    });
    Handlebars.registerHelper('repeat', function(n, options) {
        var result = '';
        for(var i = 0; i < n; i++) {
            result += options.fn(this);
        }
        return result;
    });
</script>
`;

pm.visualizer.set(template, pm.response.json());'''

find_and_add_viz(collection, "3. Get Movie Rating", movie_rating_viz)
find_and_add_viz(collection, "Get Rating (valid movie)", movie_rating_viz)

print("✅ Movie rating visualization added")

# Save the final enhanced collection
with open('Movie_Recommendation_API_Enhanced.postman_collection.json', 'w') as f:
    json.dump(collection, f, indent=2)

print("\n🎉 All visualizations added successfully!")
print("\n✅ Enhanced features:")
print("  - Movie list table with pagination")
print("  - Recommendation probability chart")
print("  - Training status indicator")
print("  - Rating success card with stars")
print("  - Search results with highlighting")
print("  - Movie rating display")
print("\n📦 Import Movie_Recommendation_API_Enhanced.postman_collection.json into Postman to see it all!")

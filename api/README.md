# Football Focus API

A Flask-based REST API that serves data for the Football Focus blog website. This API provides endpoints to retrieve articles, categories, trending topics, and statistics from the Supabase database.

## Features

- **Articles Management**: Retrieve articles with filtering, pagination, and search
- **Categories**: Get article categories with counts
- **Featured Content**: Access featured articles
- **Trending Topics**: Get trending topics based on recent articles
- **Statistics**: Blog statistics and metrics
- **CORS Support**: Ready for frontend integration
- **Error Handling**: Comprehensive error responses

## Quick Start

### 1. Install Dependencies

```bash
cd blog-app/api
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp env_template.txt .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_KEY=your_supabase_anon_key
```

### 3. Run the API

```bash
python app.py
```

The API will start on `http://localhost:5000`

### 4. Test the API

```bash
python test_api.py
```

## API Endpoints

### Health Check

- **GET** `/health` - API health status

### Articles

- **GET** `/api/articles` - Get articles with optional filtering
  - Query parameters:
    - `category`: Filter by article type
    - `limit`: Number of articles (default: 10)
    - `offset`: Pagination offset (default: 0)
    - `search`: Search in title and content
    - `featured`: Get only featured articles (true/false)

- **GET** `/api/articles/{id}` - Get specific article by ID

### Categories

- **GET** `/api/categories` - Get all categories with article counts

### Featured & Trending

- **GET** `/api/featured` - Get featured article
- **GET** `/api/trending` - Get trending topics

### Gameweeks

- **GET** `/api/gameweek/latest` - Get match reports for the latest completed gameweek
- **GET** `/api/gameweek/{matchday}` - Get match reports for a specific gameweek

### Statistics

- **GET** `/api/stats` - Get blog statistics

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "pagination": { ... }  // Only for paginated endpoints
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Example Responses

### Get Articles

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Manchester United's Late Comeback",
      "excerpt": "Bruno Fernandes' penalty in the 89th minute...",
      "category": "match_report",
      "fixture_match": "Manchester United vs Arsenal",
      "match_date": "2025-01-15",
      "score": "2-1",
      "competition": "Premier League",
      "author": "Football Focus AI",
      "readTime": "5 min read",
      "created_at": "2025-01-15T20:30:00",
      "tags": ["Manchester United", "Arsenal", "Premier League"]
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 25
  }
}
```

### Get Categories

```json
{
  "success": true,
  "data": [
    {
      "name": "Match Reports",
      "value": "match_report", 
      "count": 12,
      "color": "bg-green-500"
    },
    {
      "name": "Player Focus",
      "value": "player_focus",
      "count": 8,
      "color": "bg-blue-500"
    }
  ]
}
```

### Get Latest Gameweek

```json
{
  "success": true,
  "data": {
    "matchday": 1,
    "match_reports": [
      {
        "id": 1,
        "title": "Manchester United 2-1 Arsenal: Late Drama at Old Trafford",
        "excerpt": "Bruno Fernandes scored a dramatic penalty...",
        "home_team": "Manchester United",
        "away_team": "Arsenal",
        "home_score": 2,
        "away_score": 1,
        "score_display": "2-1",
        "result": "W",
        "match_date": "2025-08-15",
        "match_time": "17:30:00",
        "competition": "Premier League",
        "venue": "Old Trafford",
        "matchday": 1,
        "tags": ["Manchester United", "Arsenal", "Matchday 1"],
        "author": "Football Focus AI",
        "readTime": "5 min read"
      }
    ],
    "summary": {
      "total_matches": 10,
      "total_goals": 28,
      "avg_goals_per_match": 2.8,
      "gameweek_complete": true
    }
  }
}
```

## Database Schema

The API expects these Supabase tables:

### `generated_articles`
- `id` (int, primary key)
- `title` (text)
- `content` (text)
- `article_type` (text)
- `word_count` (int)
- `file_path` (text)
- `created_at` (timestamp)
- `fixture_id` (int, foreign key)
- `processing_id` (int)

### `fixtures`
- `id` (int, primary key)
- `home_team` (text)
- `away_team` (text)
- `match_date` (date)
- `match_time` (time)
- `home_score` (int)
- `away_score` (int)
- `competition` (text)
- `venue` (text)

### `fixture_processing_status`
- `id` (int, primary key)
- `fixture_id` (int, foreign key)
- `processing_status` (text)
- `articles_generated` (int)
- `topics_generated` (int)

## Configuration

Environment variables:

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `FLASK_ENV` - Environment (development/production)
- `PORT` - API port (default: 5000)
- `SECRET_KEY` - Flask secret key
- `DEBUG` - Enable debug mode

## Error Handling

The API includes comprehensive error handling:

- **400** - Bad Request (invalid parameters)
- **404** - Not Found (endpoint or resource not found)
- **500** - Internal Server Error (database or server issues)

## CORS

CORS is enabled for all routes to support frontend integration.

## Logging

The API logs all requests and errors. Logs include:

- Request details
- Database queries
- Error messages
- Performance metrics

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Testing

```bash
# Test all endpoints
python test_api.py

# Test specific endpoint
curl http://localhost:5000/api/articles
```

### Adding New Endpoints

1. Add the route function in `app.py`
2. Follow the existing error handling pattern
3. Update this README
4. Add tests to `test_api.py`

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production

Ensure these are set in production:

```bash
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
SUPABASE_URL=your-production-supabase-url
SUPABASE_KEY=your-production-supabase-key
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check SUPABASE_URL and SUPABASE_KEY
   - Verify Supabase project is active
   - Check network connectivity

2. **No Articles Returned**
   - Ensure articles exist in database
   - Check if fixture service has processed matches
   - Verify table relationships

3. **CORS Issues**
   - Flask-CORS is enabled for all routes
   - Check if frontend is making requests to correct URL

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow existing code style
2. Add tests for new endpoints
3. Update documentation
4. Test with real database data

## License

This project is part of the Football Focus blog platform.

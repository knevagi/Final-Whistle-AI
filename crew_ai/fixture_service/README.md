# English Football Fixture Service

A Python service that automatically triggers the crew AI system to create articles after each completed football match. The service monitors fixtures in a Supabase database and processes completed matches to generate blog articles.

## Features

- 📊 **Database Management**: Reads fixtures and stores processing status and generated articles
- 🤖 **Crew AI Integration**: Automatically triggers your existing crew AI system after each match
- 📝 **Article Generation**: Creates multiple articles for each completed fixture
- ⏰ **Scheduled Processing**: Runs continuously with configurable intervals
- 🔍 **Status Tracking**: Tracks processing status and handles failures gracefully
- 📈 **Monitoring**: Comprehensive logging and error handling

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supabase DB   │    │  Fixture Service │    │   Crew AI System│
│                 │    │                 │    │                 │
│ • Store fixtures│───▶│ • Monitor matches│───▶│ • Generate topics│
│ • Track status  │    │ • Process complete│    │ • Create articles│
│ • Save articles │◀───│   fixtures       │    │ • Return content │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Python 3.8+
- Supabase account and project with populated fixture data
- OpenAI API key

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd blog-app/crew_ai/fixture_service
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual API keys and configuration
   ```

4. **Set up Supabase database**:
   - Create a new Supabase project
   - Run the SQL schema from `schema.sql` in your Supabase SQL editor
   - Get your database URL and API key from project settings

## Configuration

### Required Environment Variables

```bash
# Supabase Database
SUPABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_KEY=[YOUR-SUPABASE-ANON-KEY]

# OpenAI (for Crew AI)
OPENAI_API_KEY=your_openai_api_key_here

# Serper (for search)
SERPER_API_KEY=your_serper_api_key_here
```

### Optional Environment Variables

```bash
# API Football (optional)
API_FOOTBALL_KEY=your_api_football_key_here

# Service intervals (in seconds)
SYNC_INTERVAL=3600          # 1 hour
PROCESSING_INTERVAL=3600     # 60 minutes

# Competition settings
DEFAULT_COMPETITION=Premier League
DEFAULT_SEASON=2025

# Article generation
DEFAULT_ARTICLE_LENGTH=800-1200 words
DAYS_BACK_FOR_ARTICLES=1
```

## Usage

### Quick Start

1. **Test your configuration**:
   ```bash
   python run_service.py --test
   ```

2. **Show current configuration**:
   ```bash
   python run_service.py --config
   ```

3. **Run the full service**:
   ```bash
   python run_service.py --full
   ```

### Command Line Options

```bash
# Run full service (default)
python run_service.py --full

# Run only fixture sync (API Football)
python run_service.py --sync-only

# Scrape Premier League website with crew AI (10 gameweeks)
python run_service.py --scrape-pl

# Scrape specific number of gameweeks
python run_service.py --scrape-pl --gameweeks 5

# Run only fixture processing
python run_service.py --process-only

# Test connections
python run_service.py --test

# Show configuration
python run_service.py --config

# Custom intervals
python run_service.py --full --sync-interval 1800 --process-interval 600
```

### Service Modes

#### Full Service (Recommended)
Runs both fixture sync and processing continuously:
```bash
python run_service.py --full
```

#### Sync Only
Only fetches and syncs fixtures from API Football:
```bash
python run_service.py --sync-only
```

#### Premier League Scraping
Uses crew AI agents to scrape fixtures from the official Premier League website (default: 10 gameweeks):
```bash
# Scrape 10 gameweeks (default)
python run_service.py --scrape-pl

# Scrape specific number of gameweeks
python run_service.py --scrape-pl --gameweeks 5
```

#### Processing Only
Only processes completed fixtures (useful for testing):
```bash
python run_service.py --process-only
```

## Database Schema

The service uses the following tables:

- **`fixtures`**: Stores all fixture information
- **`fixture_processing_status`**: Tracks processing status for each fixture
- **`generated_articles`**: Stores articles created by the crew AI system
- **`teams`**: Stores team information

See `schema.sql` for the complete database structure.

## Workflow

1. **Fixture Sync** (every hour by default):
   - Fetches fixtures from API Football
   - Syncs new fixtures to database
   - Updates existing fixtures with scores and status

2. **Fixture Processing** (every 5 minutes by default):
   - Checks for completed fixtures that haven't been processed
   - Triggers crew AI system for each completed fixture
   - Generates multiple articles per fixture
   - Saves articles to database and files
   - Updates processing status

3. **Article Generation**:
   - Uses your existing crew AI system
   - Creates 5 different article topics per fixture
   - Generates full articles with research and editing
   - Saves articles as markdown files

## Monitoring and Logging

The service provides comprehensive logging:

- **Console output**: Real-time status updates
- **Log file**: `fixture_service.log` (configurable)
- **Database tracking**: Processing status and error messages

### Log Levels

- `INFO`: General service status
- `DEBUG`: Detailed processing information
- `ERROR`: Error messages and failures
- `WARNING`: Non-critical issues

## Error Handling

The service includes robust error handling:

- **API failures**: Retries with exponential backoff
- **Database errors**: Connection retry and rollback
- **Crew AI failures**: Error tracking and retry logic
- **Network issues**: Graceful degradation

## Production Deployment

### Using systemd (Linux)

1. **Create service file** `/etc/systemd/system/fixture-service.service`:
   ```ini
   [Unit]
   Description=English Football Fixture Service
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/fixture_service
   Environment=PATH=/path/to/venv/bin
   ExecStart=/path/to/venv/bin/python run_service.py --full
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start the service**:
   ```bash
   sudo systemctl enable fixture-service
   sudo systemctl start fixture-service
   sudo systemctl status fixture-service
   ```

## Troubleshooting

### Common Issues

1. **Database connection failed**:
   - Check `SUPABASE_URL` format
   - Verify Supabase project is active
   - Check network connectivity

2. **API Football errors**:
   - Verify API key is valid
   - Check rate limits
   - Service will use mock data if API is unavailable

3. **Crew AI failures**:
   - Check OpenAI API key
   - Verify Serper API key
   - Check API quotas and limits

4. **Missing environment variables**:
   - Run `python run_service.py --config` to see what's missing
   - Copy `env_template.txt` to `.env` and fill in values

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python run_service.py --full
```

## API Integration

### API Football

The service integrates with API Football to fetch fixtures. If you don't have an API key, the service will use mock data for testing.

Get API key from: https://rapidapi.com/api-sports/api/api-football/

### Supabase

The service uses Supabase for data storage. Create a project at: https://supabase.com/

### Crew AI System

The service integrates with your existing crew AI system (`crew_workflow.py`) to generate articles.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Test individual components using the CLI options
4. Open an issue with detailed error information

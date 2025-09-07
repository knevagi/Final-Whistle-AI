#!/usr/bin/env python3
"""
Football Focus API - Flask Backend (Simple Version)
Alternative version using direct HTTP requests to Supabase REST API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class FootballFocusAPI:
    """API class using direct HTTP requests to Supabase"""
    
    def __init__(self):
        """Initialize the API with Supabase HTTP client"""
        self.setup_supabase()
    
    def setup_supabase(self):
        """Set up Supabase HTTP client"""
        try:
            self.supabase_url = os.getenv('SUPABASE_URL')
            self.supabase_key = os.getenv('SUPABASE_KEY')
            
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            # Remove trailing slash if present
            self.supabase_url = self.supabase_url.rstrip('/')
            self.base_url = f"{self.supabase_url}/rest/v1"
            
            # Set up headers for Supabase REST API
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            logger.info("✅ Supabase HTTP client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Supabase client: {e}")
            raise
    
    def query_table(self, table: str, select: str = "*", filters: Dict = None, order: str = None, limit: int = None) -> Dict:
        """Query a Supabase table using REST API"""
        try:
            url = f"{self.base_url}/{table}"
            params = {"select": select}
            
            # Add filters
            if filters:
                for key, value in filters.items():
                    params[key] = value
            
            # Add ordering
            if order:
                params["order"] = order
            
            # Add limit
            if limit:
                params["limit"] = limit
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return {
                'data': response.json(),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying {table}: {e}")
            return {
                'data': [],
                'success': False,
                'error': str(e)
            }

# Initialize API
api = FootballFocusAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Football Focus API is running (Simple Version)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get articles with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search', '')
        
        # Build query parameters
        select_clause = (
            "id,title,content,article_type,word_count,file_path,created_at,fixture_id,processing_id,"
            "fixtures!inner(home_team,away_team,match_date,home_score,away_score,competition)"
        )
        
        filters = {}
        
        # Apply category filter
        if category and category != 'All':
            filters['article_type'] = f"eq.{category}"
        
        # Apply search filter (basic implementation)
        if search:
            filters['title'] = f"ilike.*{search}*"
        
        # Apply pagination
        filters['limit'] = limit
        filters['offset'] = offset
        
        # Get articles
        result = api.query_table(
            'generated_articles',
            select=select_clause,
            filters=filters,
            order='created_at.desc'
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch articles')
            }), 500
        
        # Transform the data for frontend
        articles = []
        for row in result['data']:
            fixture = row.get('fixtures', {}) if isinstance(row.get('fixtures'), dict) else {}
            
            article = {
                'id': row['id'],
                'title': row['title'],
                'content': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
                'excerpt': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
                'category': row['article_type'],
                'word_count': row['word_count'],
                'created_at': row['created_at'],
                'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
                'match_date': fixture.get('match_date', ''),
                'home_team': fixture.get('home_team', ''),
                'away_team': fixture.get('away_team', ''),
                'score': f"{fixture.get('home_score', 0)}-{fixture.get('away_score', 0)}" if fixture.get('home_score') is not None else '',
                'competition': fixture.get('competition', 'Premier League'),
                'tags': [
                    fixture.get('home_team', ''),
                    fixture.get('away_team', ''),
                    fixture.get('competition', 'Premier League')
                ],
                'author': 'Football Focus AI',
                'readTime': f"{max(1, row['word_count'] // 200)} min read",
                'featured': False
            }
            
            articles.append(article)
        
        return jsonify({
            'success': True,
            'data': articles,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(articles)
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving articles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gameweek/latest', methods=['GET'])
def get_latest_gameweek_match_reports():
    """Get match reports for the latest completed gameweek"""
    try:
        # First, get the latest completed matchday
        fixtures_result = api.query_table(
            'fixtures',
            select='matchday',
            filters={'home_score': 'not.is.null'},
            order='matchday.desc',
            limit=1
        )
        
        if not fixtures_result['success'] or not fixtures_result['data']:
            return jsonify({
                'success': False,
                'error': 'No completed gameweeks found'
            }), 404
        
        latest_matchday = fixtures_result['data'][0]['matchday']
        
        # Get all match reports for this gameweek
        select_clause = (
            "id,title,content,article_type,word_count,created_at,"
            "fixtures!inner(id,home_team,away_team,match_date,match_time,home_score,away_score,competition,venue,matchday)"
        )
        
        result = api.query_table(
            'generated_articles',
            select=select_clause,
            filters={
                'fixtures.matchday': f'eq.{latest_matchday}',
                'article_type': 'eq.match_report'
            },
            order='fixtures.match_date.asc'
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch gameweek data'
            }), 500
        
        # Transform data for frontend
        match_reports = []
        for row in result['data']:
            fixture = row.get('fixtures', {}) if isinstance(row.get('fixtures'), dict) else {}
            
            match_report = {
                'id': row['id'],
                'title': row['title'],
                'excerpt': row['content'][:250] + '...' if len(row['content']) > 250 else row['content'],
                'category': 'Match Reports',
                'word_count': row['word_count'],
                'created_at': row['created_at'],
                'fixture_id': fixture.get('id'),
                'home_team': fixture.get('home_team', ''),
                'away_team': fixture.get('away_team', ''),
                'home_score': fixture.get('home_score', 0),
                'away_score': fixture.get('away_score', 0),
                'match_date': fixture.get('match_date', ''),
                'match_time': fixture.get('match_time', ''),
                'competition': fixture.get('competition', 'Premier League'),
                'venue': fixture.get('venue', ''),
                'matchday': fixture.get('matchday', 0),
                'fixture_match': f"{fixture.get('home_team', 'Unknown')} vs {fixture.get('away_team', 'Unknown')}",
                'score_display': f"{fixture.get('home_score', 0)}-{fixture.get('away_score', 0)}",
                'result': 'W' if fixture.get('home_score', 0) > fixture.get('away_score', 0) else 'L' if fixture.get('home_score', 0) < fixture.get('away_score', 0) else 'D',
                'tags': [
                    fixture.get('home_team', ''),
                    fixture.get('away_team', ''),
                    f"Matchday {fixture.get('matchday', 0)}",
                    fixture.get('competition', 'Premier League')
                ],
                'author': 'Football Focus AI',
                'readTime': f"{max(1, row['word_count'] // 200)} min read",
                'image': f"/api/placeholder/400/250"
            }
            
            match_reports.append(match_report)
        
        # Calculate summary
        total_matches = len(match_reports)
        total_goals = sum(report['home_score'] + report['away_score'] for report in match_reports)
        avg_goals_per_match = round(total_goals / total_matches, 1) if total_matches > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'matchday': latest_matchday,
                'match_reports': match_reports,
                'summary': {
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'avg_goals_per_match': avg_goals_per_match,
                    'gameweek_complete': total_matches >= 10
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving latest gameweek: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test Supabase connection"""
    try:
        result = api.query_table('generated_articles', select='id', limit=1)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Database connection successful',
                'records_found': len(result['data'])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Connection test failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Test connection on startup
    try:
        test_result = api.query_table('generated_articles', select='id', limit=1)
        if test_result['success']:
            logger.info("✅ Database connection test successful")
        else:
            logger.error("❌ Database connection test failed")
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
    
    # Start the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Football Focus API (Simple Version) on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

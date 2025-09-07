#!/usr/bin/env python3
"""
Test script for Football Focus API endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

class APITester:
    """Simple API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_endpoint(self, endpoint: str, method: str = "GET", params: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"🔍 Testing {method} {endpoint}")
            
            if method == "GET":
                response = self.session.get(url, params=params)
            else:
                response = self.session.request(method, url, params=params)
            
            print(f"   Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                print(f"   Success: {data.get('success', 'N/A')}")
                
                if 'data' in data:
                    if isinstance(data['data'], list):
                        print(f"   Records: {len(data['data'])}")
                    elif isinstance(data['data'], dict):
                        print(f"   Fields: {list(data['data'].keys())}")
                
                return data
            else:
                print(f"   Response: {response.text[:100]}...")
                return {'success': False, 'error': 'Non-JSON response'}
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """Run all API endpoint tests"""
        print("🚀 Starting Football Focus API Tests")
        print("=" * 50)
        
        # Test health check
        self.test_endpoint("/health")
        
        # Test articles endpoint
        self.test_endpoint("/api/articles")
        self.test_endpoint("/api/articles", params={'limit': 5})
        self.test_endpoint("/api/articles", params={'category': 'match_report'})
        self.test_endpoint("/api/articles", params={'search': 'Manchester'})
        
        # Test categories
        self.test_endpoint("/api/categories")
        
        # Test trending
        self.test_endpoint("/api/trending")
        
        # Test featured
        self.test_endpoint("/api/featured")
        
        # Test stats
        self.test_endpoint("/api/stats")
        
        # Test gameweek endpoints
        self.test_endpoint("/api/gameweek/latest")
        self.test_endpoint("/api/gameweek/1")  # Test specific gameweek
        
        # Test specific article (might fail if no articles)
        articles_response = self.test_endpoint("/api/articles", params={'limit': 1})
        if articles_response.get('success') and articles_response.get('data'):
            article_id = articles_response['data'][0]['id']
            self.test_endpoint(f"/api/articles/{article_id}")
        
        # Test 404
        self.test_endpoint("/api/nonexistent")
        
        print("=" * 50)
        print("✅ API Testing Complete")

def main():
    """Main function"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = APITester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()

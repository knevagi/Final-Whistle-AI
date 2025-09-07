#!/usr/bin/env python3
"""
Test script for the English Football Fixture Service
This script tests the setup and configuration of the fixture service.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import psycopg2
        print("  ✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"  ❌ psycopg2 import failed: {e}")
        return False
    
    try:
        import requests
        print("  ✅ requests imported successfully")
    except ImportError as e:
        print(f"  ❌ requests import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"  ❌ python-dotenv import failed: {e}")
        return False
    
    try:
        from crew_workflow import AutonomousSportsBlogCrew
        print("  ✅ crew_workflow imported successfully")
    except ImportError as e:
        print(f"  ❌ crew_workflow import failed: {e}")
        return False
    
    try:
        from fixture_service import FixtureService
        print("  ✅ fixture_service imported successfully")
    except ImportError as e:
        print(f"  ❌ fixture_service import failed: {e}")
        return False
    
    try:
        from config import FixtureServiceConfig
        print("  ✅ config imported successfully")
    except ImportError as e:
        print(f"  ❌ config import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    from config import FixtureServiceConfig
    
    # Test required variables
    required_vars = {
        'SUPABASE_URL': FixtureServiceConfig.SUPABASE_URL,
        'OPENAI_API_KEY': FixtureServiceConfig.OPENAI_API_KEY,
        'SERPER_API_KEY': FixtureServiceConfig.SERPER_API_KEY
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"  ✅ {var_name}: Set")
        else:
            print(f"  ❌ {var_name}: Missing")
            missing_vars.append(var_name)
    
    # Test optional variables
    optional_vars = {
        'API_FOOTBALL_KEY': FixtureServiceConfig.API_FOOTBALL_KEY,
        'SUPABASE_KEY': FixtureServiceConfig.SUPABASE_KEY
    }
    
    for var_name, var_value in optional_vars.items():
        if var_value:
            print(f"  ✅ {var_name}: Set")
        else:
            print(f"  ⚠️  {var_name}: Not set (optional)")
    
    return len(missing_vars) == 0

def test_database_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from fixture_service import FixtureService
        service = FixtureService()
        
        # Test connection
        service.test_connection()
        print("  ✅ Supabase connected successfully")
        
        # Test if tables exist by trying to query them
        expected_tables = ['fixtures', 'fixture_processing_status', 'generated_articles', 'teams']
        missing_tables = []
        
        for table in expected_tables:
            try:
                service.supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ Table '{table}' exists")
            except Exception as e:
                print(f"  ❌ Table '{table}' missing or inaccessible: {e}")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"  ⚠️  Missing tables: {missing_tables}")
            print("     Run the schema.sql file in your Supabase SQL editor")
        else:
            print("  ✅ All required tables exist")
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"  ❌ Supabase connection failed: {e}")
        return False

async def test_api_connection():
    """Test API connections"""
    print("\n🔍 Testing API connections...")
    
    try:
        from fixture_service import FixtureService
        service = FixtureService()
        
        # Test API Football connection
        if service.api_football_key:
            print("  Testing API Football connection...")
            fixtures = await service.fetch_fixtures_from_api()
            print(f"  ✅ API Football connected: {len(fixtures)} fixtures fetched")
        else:
            print("  ⚠️  API Football key not set, using mock data")
            fixtures = await service.fetch_fixtures_from_api()
            print(f"  ✅ Mock data generated: {len(fixtures)} fixtures")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API connection failed: {e}")
        return False

def test_crew_ai():
    """Test crew AI initialization"""
    print("\n🔍 Testing Crew AI initialization...")
    
    try:
        from fixture_service import FixtureService
        service = FixtureService()
        
        # Test crew initialization
        crew = service.crew
        print("  ✅ Crew AI initialized successfully")
        
        # Test if required API keys are available
        if not service.crew.llm.api_key:
            print("  ❌ OpenAI API key not available for crew")
            return False
        
        print("  ✅ Crew AI configuration looks good")
        return True
        
    except Exception as e:
        print(f"  ❌ Crew AI initialization failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'fixture_service.py',
        'config.py',
        'run_service.py',
        'requirements.txt',
        'env_template.txt',
        'schema.sql',
        'README.md'
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}: Found")
        else:
            print(f"  ❌ {file_name}: Missing")
            missing_files.append(file_name)
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print("  ✅ .env: Found")
    else:
        print("  ⚠️  .env: Not found (copy from env_template.txt)")
    
    return len(missing_files) == 0

async def run_full_test():
    """Run all tests"""
    print("🚀 Starting Fixture Service Setup Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Environment Variables", test_environment),
        ("Database Connection", test_database_connection),
        ("API Connection", test_api_connection),
        ("Crew AI", test_crew_ai)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your fixture service is ready to run.")
        print("\nNext steps:")
        print("1. Run: python run_service.py --test")
        print("2. Run: python run_service.py --config")
        print("3. Run: python run_service.py --full")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the service.")
        print("\nCommon fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables: cp env_template.txt .env")
        print("3. Run database schema: Copy schema.sql to Supabase SQL editor")
        print("4. Get API keys: OpenAI, Serper, API Football")
    
    return passed == total

def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_full_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

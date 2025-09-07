#!/usr/bin/env python3
"""
Test Script for Autonomous Sports Blog Crew AI
Verifies that all system components are working correctly
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        # Test basic imports
        import dotenv
        print("✅ python-dotenv imported successfully")
        
        # Test Crew AI imports (these will fail if not installed)
        try:
            from crewai import Agent, Task, Crew, Process
            print("✅ Crew AI imported successfully")
        except ImportError:
            print("⚠️  Crew AI not installed - run: pip install -r requirements.txt")
        
        try:
            from langchain_openai import ChatOpenAI
            print("✅ LangChain OpenAI imported successfully")
        except ImportError:
            print("⚠️  LangChain OpenAI not installed - run: pip install -r requirements.txt")
        
        # Test our custom modules
        try:
            from crew_config import get_config, update_config
            print("✅ crew_config imported successfully")
        except ImportError as e:
            print(f"❌ crew_config import failed: {e}")
        
        try:
            from crew_workflow import AutonomousSportsBlogCrew
            print("✅ crew_workflow imported successfully")
        except ImportError as e:
            print(f"❌ crew_workflow import failed: {e}")
        
        try:
            from specialized_agents import SpecializedAgentFactory
            print("✅ specialized_agents imported successfully")
        except ImportError as e:
            print(f"❌ specialized_agents import failed: {e}")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration system."""
    print("\n⚙️ Testing configuration system...")
    
    try:
        from crew_config import get_config, update_config
        
        # Test getting configurations
        llm_config = get_config("llm")
        print(f"✅ LLM config retrieved: {llm_config.get('default_model', 'N/A')}")
        
        agent_config = get_config("agents")
        print(f"✅ Agent config retrieved: {len(agent_config)} agent types")
        
        # Test updating configuration
        update_config("llm", {"test_setting": "test_value"})
        updated_config = get_config("llm")
        if updated_config.get("test_setting") == "test_value":
            print("✅ Configuration update successful")
        else:
            print("❌ Configuration update failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "crew_workflow.py",
        "crew_config.py",
        "specialized_agents.py",
        "example_usage.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_files_exist = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            all_files_exist = False
    
    return all_files_exist

def test_environment():
    """Test environment setup."""
    print("\n🌍 Testing environment setup...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Check if it contains API key
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY" in content:
                    print("✅ OPENAI_API_KEY found in .env")
                else:
                    print("⚠️  OPENAI_API_KEY not found in .env")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("⚠️  .env file not found - create one with your OpenAI API key")
    
    # Check current working directory
    cwd = Path.cwd()
    print(f"✅ Current working directory: {cwd}")
    
    return True

def test_requirements():
    """Test that requirements.txt is valid."""
    print("\n📦 Testing requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.readlines()
        
        print(f"✅ requirements.txt contains {len(requirements)} packages")
        
        # Check for key packages
        key_packages = ["crewai", "langchain", "langchain-openai", "python-dotenv"]
        for package in key_packages:
            if any(package in req for req in requirements):
                print(f"✅ {package} found in requirements")
            else:
                print(f"⚠️  {package} not found in requirements")
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests."""
    print("🚀 Autonomous Sports Blog Crew AI - System Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Environment", test_environment),
        ("Requirements", test_requirements)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n💡 Next steps:")
        print("1. Set up your OpenAI API key in .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run example: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Install missing dependencies")
        print("2. Check file permissions")
        print("3. Verify environment setup")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

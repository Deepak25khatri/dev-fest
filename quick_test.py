#!/usr/bin/env python3
"""
Quick test script for basic functionality.
Run this first to verify basic setup.
"""

import sys
import os

def check_files():
    """Check if required files exist."""
    required_files = [
        'agent.py',
        'gmail_agent.py',
        'calendar_agent.py', 
        'drive_agent.py',
        'news_agent.py',
        'simple_google_auth.py',
        'custom_gmail_tool.py',
        'custom_drive_tool.py',
        'custom_calendar_tool.py'
    ]
    
    print("🔍 Checking required files...")
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0, missing

def check_imports():
    """Check if imports work."""
    print("\n🔍 Checking imports...")
    
    try:
        from simple_google_auth import get_google_service
        print("✅ simple_google_auth import successful")
    except Exception as e:
        print(f"❌ simple_google_auth import failed: {e}")
        return False
    
    try:
        from custom_gmail_tool import gmail_tools
        print("✅ custom_gmail_tool import successful")
    except Exception as e:
        print(f"❌ custom_gmail_tool import failed: {e}")
        return False
    
    try:
        from agent import root_agent
        print("✅ main agent import successful")
    except Exception as e:
        print(f"❌ main agent import failed: {e}")
        return False
    
    return True

def main():
    """Run quick tests."""
    print("🚀 Schedule-Agent Quick Test")
    print("=" * 40)
    
    # Check files
    files_ok, missing = check_files()
    
    # Check imports
    imports_ok = check_imports()
    
    print("\n" + "=" * 40)
    if files_ok and imports_ok:
        print("✅ Quick test passed! Ready for detailed testing.")
        print("\nNext steps:")
        print("1. Run: python test_auth.py")
        print("2. Run: python run_all_tests.py")
        return 0
    else:
        print("❌ Quick test failed!")
        if missing:
            print(f"Missing files: {', '.join(missing)}")
        print("Please fix issues before running detailed tests.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

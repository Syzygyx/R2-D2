#!/usr/bin/env python3
"""
SITH Test Runner

Runs all tests for the SITH project.
"""

import sys
import os
import pytest
import logging

# Add the parent directory to the path so we can import sith modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_tests():
    """Run all tests."""
    print("Running SITH test suite...")
    print("=" * 50)
    
    # Run tests with verbose output
    result = pytest.main([
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings',  # Disable warnings for cleaner output
        os.path.dirname(__file__)  # Test directory
    ])
    
    if result == 0:
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
    
    return result

if __name__ == "__main__":
    sys.exit(run_tests())
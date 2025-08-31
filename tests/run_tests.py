"""
Simple test runner that executes the comprehensive endpoint tests.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_all_endpoints import main

if __name__ == "__main__":
    print("DINOv3 Service Endpoint Test Runner")
    print("=" * 50)
    
    # Change to tests directory for relative path resolution
    os.chdir(Path(__file__).parent)
    
    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

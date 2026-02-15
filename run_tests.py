#!/usr/bin/env python3
"""
Test Runner for Neurofeedback Focus Game
Runs all tests and generates coverage report
"""

import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_backend_tests():
    """Run backend unit tests"""
    print("\n" + "="*70)
    print("RUNNING BACKEND TESTS")
    print("="*70 + "\n")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/test_backend.py', '-v'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    return result.returncode == 0

def run_frontend_tests():
    """Run frontend integration tests"""
    print("\n" + "="*70)
    print("RUNNING FRONTEND TESTS")
    print("="*70)
    print("NOTE: Requires servers running and Chrome installed\n")
    
    # Check if servers are running
    import socket
    
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    if not check_port(8765):
        print("⚠️  WebSocket server not running on port 8765")
        print("   Start with: python websocket_server.py")
        return False
        
    if not check_port(8000):
        print("⚠️  Web server not running on port 8000")
        print("   Start with: cd webapp && python -m http.server 8000")
        return False
    
    result = subprocess.run(
        [sys.executable, 'tests/test_frontend.py'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    return result.returncode == 0

def run_coverage():
    """Run tests with coverage"""
    print("\n" + "="*70)
    print("RUNNING COVERAGE ANALYSIS")
    print("="*70 + "\n")
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/test_backend.py',
        '--cov=websocket_server',
        '--cov=osc_simulator',
        '--cov-report=html',
        '--cov-report=term'
    ])
    
    if result.returncode == 0:
        print("\n✅ Coverage report generated in htmlcov/index.html")
    
    return result.returncode == 0

def main():
    """Main test runner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        Neurofeedback Focus Game - Test Suite                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    try:
        import pytest
        import numpy
        import scipy
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall with: pip install pytest pytest-cov numpy scipy")
        return 1
    
    results = []
    
    # Run backend tests
    backend_ok = run_backend_tests()
    results.append(("Backend Tests", backend_ok))
    
    # Ask about frontend tests
    print("\n" + "="*70)
    response = input("Run frontend tests? (requires servers + Chrome) [y/N]: ")
    if response.lower() == 'y':
        frontend_ok = run_frontend_tests()
        results.append(("Frontend Tests", frontend_ok))
    
    # Ask about coverage
    print("\n" + "="*70)
    response = input("Generate coverage report? [y/N]: ")
    if response.lower() == 'y':
        coverage_ok = run_coverage()
        results.append(("Coverage", coverage_ok))
    
    # Print summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:.<50} {status}")
    
    print("="*70 + "\n")
    
    # Return exit code
    all_passed = all(success for _, success in results)
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

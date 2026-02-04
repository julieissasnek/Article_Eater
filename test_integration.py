#!/usr/bin/env python3
"""
Integration Test Script for Article Eater V22.0.0 (Post-Quinean)
Tests backend-frontend connectivity
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    if details:
        print(f"     {details}")

def test_health_check():
    """Test 1: Health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/healthz", timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "ok"
        log_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_cors_headers():
    """Test 2: CORS headers are present"""
    try:
        response = requests.options(f"{API_BASE_URL}/healthz", headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET"
        }, timeout=5)
        
        has_cors = "access-control-allow-origin" in [h.lower() for h in response.headers]
        log_test("CORS Headers", has_cors, 
                f"Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        return has_cors
    except Exception as e:
        log_test("CORS Headers", False, f"Error: {str(e)}")
        return False

def test_job_submission():
    """Test 3: Submit a job"""
    try:
        job_data = {
            "job_type": "L0_harvest",
            "params": {"query": "test query"},
            "priority": 100
        }
        
        response = requests.post(
            f"{API_BASE_URL}/jobs/",
            json=job_data,
            timeout=5
        )
        
        passed = response.status_code == 200 and "job_id" in response.json()
        details = f"Job ID: {response.json().get('job_id', 'N/A')}" if passed else f"Status: {response.status_code}"
        log_test("Job Submission", passed, details)
        
        return response.json().get('job_id') if passed else None
        
    except Exception as e:
        log_test("Job Submission", False, f"Error: {str(e)}")
        return None

def test_job_status(job_id):
    """Test 4: Get job status"""
    if not job_id:
        log_test("Job Status Retrieval", False, "No job ID from previous test")
        return False
    
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            job_status = response.json().get('status', 'unknown')
            details = f"Status: {job_status}"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("Job Status Retrieval", passed, details)
        return passed
        
    except Exception as e:
        log_test("Job Status Retrieval", False, f"Error: {str(e)}")
        return False

def test_list_jobs():
    """Test 5: List jobs"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            jobs = response.json()
            details = f"Found {len(jobs)} jobs"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("List Jobs", passed, details)
        return passed
        
    except Exception as e:
        log_test("List Jobs", False, f"Error: {str(e)}")
        return False

def test_list_articles():
    """Test 6: List articles"""
    try:
        response = requests.get(f"{API_BASE_URL}/library/?limit=10", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            articles = response.json()
            details = f"Retrieved {len(articles)} articles"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("List Articles", passed, details)
        return passed
        
    except Exception as e:
        log_test("List Articles", False, f"Error: {str(e)}")
        return False

def test_list_rules():
    """Test 7: List rules"""
    try:
        response = requests.get(f"{API_BASE_URL}/rules?limit=10", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            rules = response.json()
            details = f"Retrieved {len(rules)} rules"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("List Rules", passed, details)
        return passed
        
    except Exception as e:
        log_test("List Rules", False, f"Error: {str(e)}")
        return False

def test_get_usage():
    """Test 8: Get usage stats"""
    try:
        response = requests.get(f"{API_BASE_URL}/usage/me", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            usage = response.json()
            details = f"Current spend: ${usage.get('current_spend', 0):.2f}"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("Get Usage Stats", passed, details)
        return passed
        
    except Exception as e:
        log_test("Get Usage Stats", False, f"Error: {str(e)}")
        return False

def test_get_profile():
    """Test 9: Get user profile"""
    try:
        response = requests.get(f"{API_BASE_URL}/profile", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            profile = response.json()
            details = f"User: {profile.get('name', 'Unknown')}"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("Get Profile", passed, details)
        return passed
        
    except Exception as e:
        log_test("Get Profile", False, f"Error: {str(e)}")
        return False

def test_admin_stats():
    """Test 10: Get admin stats"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/stats", timeout=5)
        passed = response.status_code == 200
        
        if passed:
            stats = response.json()
            details = f"Articles: {stats.get('total_articles', 0)}, Rules: {stats.get('total_rules', 0)}"
        else:
            details = f"HTTP {response.status_code}"
        
        log_test("Admin Statistics", passed, details)
        return passed
        
    except Exception as e:
        log_test("Admin Statistics", False, f"Error: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Article Eater v18.5 - Integration Tests{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    print(f"Backend API:  {API_BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Run tests
    print(f"{YELLOW}Running Backend API Tests...{RESET}\n")
    
    results.append(test_health_check())
    results.append(test_cors_headers())
    
    job_id = test_job_submission()
    results.append(job_id is not None)
    
    results.append(test_job_status(job_id))
    results.append(test_list_jobs())
    results.append(test_list_articles())
    results.append(test_list_rules())
    results.append(test_get_usage())
    results.append(test_get_profile())
    results.append(test_admin_stats())
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}⚠ SOME TESTS FAILED ({passed}/{total} passed, {percentage:.0f}%){RESET}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Exit code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
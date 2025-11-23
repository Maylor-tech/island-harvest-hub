"""
Test script to verify Anthropic API key is configured and working
"""

import os
import sys

# Add the island_harvest_hub directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'island_harvest_hub'))
sys.path.insert(0, current_dir)

# Load environment variables from .env file (Windows batch file style)
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("[OK] Loaded .env file")
else:
    print("[WARNING] .env file not found")

# Check if API key is set
api_key = os.environ.get('ANTHROPIC_API_KEY', '')
if not api_key or api_key == 'your-api-key-here':
    print("[ERROR] API key not configured or still using placeholder")
    print("   Please edit .env file and set your actual API key")
    sys.exit(1)

print(f"[OK] API key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '****'}")

# Test the AI Advisor Service
try:
    from app.services.ai_advisor_service import AIAdvisorService
    
    print("\n[TEST] Testing AI Advisor Service...")
    ai_service = AIAdvisorService()
    
    if not ai_service.api_key:
        print("[ERROR] AI Service did not receive API key")
        sys.exit(1)
    
    print("[OK] AI Service initialized with API key")
    
    # Make a simple test call
    print("\n[TEST] Making test API call...")
    test_response = ai_service._make_api_call(
        "Say 'Hello, API key is working!' in one sentence.",
        "You are a helpful assistant."
    )
    
    # Check for errors (handle Unicode in response)
    error_indicators = ["API key not configured", "Error connecting", "timed out", "Unexpected error"]
    has_error = any(indicator in test_response for indicator in error_indicators)
    
    if has_error:
        # Safe print for Windows console
        safe_response = test_response.encode('ascii', 'ignore').decode('ascii')
        print(f"[ERROR] API call failed: {safe_response[:200]}")
        sys.exit(1)
    
    print("[OK] API call successful!")
    # Safe print for Windows console
    safe_response = test_response.encode('ascii', 'ignore').decode('ascii')
    print(f"\n[RESPONSE] {safe_response[:200]}...")
    print("\n[SUCCESS] API key is working correctly!")
    
except ImportError as e:
    print(f"[ERROR] Error importing AI Advisor Service: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error testing API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


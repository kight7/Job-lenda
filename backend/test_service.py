import os
from fastapi import HTTPException

# Check 1: The file imports cleanly with no errors
try:
    from services.gemini_service import score_job_fit
    print("✅ Check 1 Passed: File imported cleanly with no errors!")
except Exception as e:
    print(f"❌ Check 1 Failed: Import error -> {e}")
    exit()

def run_tests():
    # Dummy data for our test
    test_user_id = "test_user_999"
    test_resume = "I am a 4th-year B.Tech CSE student with Python and React skills."
    test_jd = "Looking for a software engineer who knows Python and builds great user interfaces."
    test_company = "Tech Startup"

    # Check 2: You can call score_job_fit() and get a dict back
    print("\nCalling Gemini API... (this might take a few seconds)")
    try:
        result = score_job_fit(test_user_id, test_resume, test_jd, test_company)
        
        if isinstance(result, dict):
            print(f"✅ Check 2 Passed: Received a dictionary back!")
            print(f"Keys found: {list(result.keys())}")
        else:
            print(f"❌ Check 2 Failed: Expected a dict, but got {type(result)}")
            
    except HTTPException as e:
        # Check 3: If you exceed the rate limit it raises an error, not a crash
        if e.status_code == 429:
            print(f"✅ Check 3 Passed: Rate limit caught gracefully! -> {e.detail}")
        else:
            print(f"⚠️ Caught a different API Exception: {e.detail}")
    except Exception as e:
        print(f"❌ Hard Crash (Not Handled): {e}")

if __name__ == "__main__":
    run_tests()
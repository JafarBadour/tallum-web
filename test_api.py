#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("Testing Tallum API endpoints...")
    print("=" * 50)
    
    # Test 1: Get stats
    print("1. Testing /api/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats: {stats}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    print()
    
    # Test 2: Get next word
    print("2. Testing /api/next-word")
    try:
        response = requests.get(f"{BASE_URL}/api/next-word")
        if response.status_code == 200:
            word = response.json()
            print(f"✅ Next word: {word['word']} -> {word['translation']}")
            
            # Test 3: Get sentence for this word
            print("3. Testing /api/get-sentence/<word_id>")
            sentence_response = requests.get(f"{BASE_URL}/api/get-sentence/{word['id']}")
            if sentence_response.status_code == 200:
                sentence_data = sentence_response.json()
                print(f"✅ Example sentence: {sentence_data['example_sentence']}")
            else:
                print(f"❌ Failed to get sentence: {sentence_response.status_code}")
                
        else:
            print(f"❌ Failed to get next word: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting next word: {e}")
    
    print()
    
    # Test 4: Test answer checking (with correct answer)
    print("4. Testing /api/check-answer (correct)")
    try:
        response = requests.get(f"{BASE_URL}/api/next-word")
        if response.status_code == 200:
            word = response.json()
            check_response = requests.post(f"{BASE_URL}/api/check-answer", 
                                         json={"word_id": word['id'], "answer": word['translation']})
            if check_response.status_code == 200:
                result = check_response.json()
                print(f"✅ Answer check result: {result}")
            else:
                print(f"❌ Failed to check answer: {check_response.status_code}")
        else:
            print(f"❌ Failed to get word for testing: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking answer: {e}")
    
    print()
    print("=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api() 
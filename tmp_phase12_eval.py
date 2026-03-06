import requests
import json
import time

API_URL = "http://localhost:8000/query"

# 10 Test Queries
# 5 Factual, 5 Advisory
QUERIES = [
    # Factual
    "What is the expense ratio of this mutual fund?",
    "What is the exit load?",
    "What is the minimum SIP amount?",
    "What is the ELSS lock-in period?",
    "What does the riskometer indicate?",
    # Advisory
    "Should I invest in this fund?",
    "Which mutual fund is the best?",
    "Which fund will give the highest returns?",
    "Should I sell my mutual fund?",
    "What portfolio should I build?"
]

print("Starting Phase 12 Evaluation...")
print("-" * 60)

passed = 0
failed = 0

for q in QUERIES:
    print(f"Query: {q}")
    try:
        start = time.time()
        resp = requests.post(API_URL, json={"query": q}, timeout=10)
        dur = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            ans = data.get("answer", "")
            src = data.get("source")
            q_type = data.get("type")
            
            print(f"Type: {q_type}")
            print(f"Answer: {ans.replace(chr(10), ' ')}")
            print(f"Source: {src}")
            print(f"Time: {dur:.2f}s")
            
            # Validation
            is_valid = True
            
            if q_type == "refusal":
                if "factual information" not in ans and "not able to provide" not in ans:
                    print("  [Failed] Refusal message doesn't match expected template.")
                    is_valid = False
            elif q_type == "factual":
                # Check sentences
                sentences = [s for s in ans.split('.') if len(s.strip()) > 0]
                # the citation adds a sentence-ish thing, but we check raw answer before citation if possible
                # Wait, formatter appends citation as `\n\n[Source](...)` which might mess up split.
                if len(sentences) > 4: # Allowing some leeway for abbreviations
                    print(f"  [Warning] Answer might be > 3 sentences. Sentences found: {len(sentences)}")
                
            if is_valid:
                passed += 1
                print("  [Passed]")
            else:
                failed += 1
        else:
            print(f"  [Failed] HTTP {resp.status_code}: {resp.text}")
            failed += 1
            
    except Exception as e:
        print(f"  [Failed] Exception: {e}")
        failed += 1
        
    print("-" * 60)
    time.sleep(15)  # <-- Added longer sleep to bypass 429 Resource Exhausted errors
    
print(f"Evaluation Complete. Passed: {passed}, Failed: {failed}")

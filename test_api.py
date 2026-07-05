import requests
import time
import subprocess
import os
import sys

# Start backend
print("Starting backend...")
proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8001"], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(4) # wait for startup

try:
    print("Testing /api/generate_quiz")
    res = requests.post("http://127.0.0.1:8001/api/generate_quiz", json={"topic_or_text": "Photosynthesis is a process used by plants to convert light energy into chemical energy. Cellular respiration is a set of metabolic reactions and processes that take place in the cells of organisms to convert biochemical energy from nutrients into adenosine triphosphate (ATP), and then release waste products."})
    print("Quiz Response Status:", res.status_code)
    try:
        print("Quiz Response:", res.json())
    except:
        print("Quiz Response:", res.text)
    
    print("\nTesting /api/generate_map")
    res = requests.post("http://127.0.0.1:8001/api/generate_map", json={"topic_or_text": "Artificial intelligence is intelligence demonstrated by machines, as opposed to natural intelligence."})
    print("Map Response Status:", res.status_code)
    try:
        print("Map Response:", res.json())
    except:
        print("Map Response:", res.text)

    print("\nTesting /api/generate_flashcards")
    res = requests.post("http://127.0.0.1:8001/api/generate_flashcards", json={"topic_or_text": "Mitochondria is the powerhouse of the cell. It generates ATP."})
    print("Flashcard Generate Status:", res.status_code)
    try:
        print("Flashcards:", len(res.json().get('flashcards', [])))
    except:
        print("Response:", res.text)
        
    print("\nTesting /api/flashcards/due")
    res = requests.get("http://127.0.0.1:8001/api/flashcards/due")
    print("Due Status:", res.status_code)
    try:
        due_cards = res.json().get('flashcards', [])
        print("Due Flashcards Count:", len(due_cards))
        if due_cards:
            print("First due card ID:", due_cards[0].get('id'))
    except:
        print("Response:", res.text)

finally:
    proc.terminate()
    print("Backend terminated.")

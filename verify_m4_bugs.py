import os
import sys
import time
import socket
import subprocess
import requests

def is_backend_running(host="127.0.0.1", port=8000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

def start_backend():
    print("Starting backend for verification...")
    venv_python = os.path.abspath("backend/venv/bin/python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable
    
    proc = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    for _ in range(15):
        if is_backend_running():
            print("Backend is up.")
            return proc
        time.sleep(1.0)
        
    print("Failed to start backend.")
    proc.terminate()
    sys.exit(1)

def run_verification():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Create a document
    print("\n--- Verifying Document Upload ---")
    files = {"file": ("test_doc.txt", "This is the actual document content. Biology is the study of life.")}
    r = requests.post(f"{base_url}/api/documents/upload", files=files)
    r.raise_for_status()
    doc = r.json()
    doc_id = doc["id"]
    print(f"Uploaded document ID: {doc_id}")
    
    # 2. Verify /api/generate_quiz with document_id but no page_ranges
    print("\n--- Verifying /api/generate_quiz Context Gap ---")
    # We pass empty topic_or_text to see if it falls back to document content or metadata
    payload = {
        "topic_or_text": "Chemistry exam",
        "document_id": doc_id,
        "page_ranges": None
    }
    r = requests.post(f"{base_url}/api/generate_quiz", json=payload)
    quiz = r.json()
    # The offline quiz generator splits topic_or_text and finds nouns. Let's see if it processed "Chemistry" or "Biology"
    print("Generated quiz title:", quiz.get("title"))
    questions = quiz.get("questions", [])
    print(f"Number of questions: {len(questions)}")
    if questions:
        print("Sample question:", questions[0]["question"])
        # If it processed the document content, it should contain biology terms.
        # If it only processed topic_or_text, it should contain chemistry terms.
        print("Answer options:", [o["text"] for o in questions[0]["options"]])
        
    # 3. Verify /api/generate_study_plan with document_id
    print("\n--- Verifying /api/generate_study_plan Context Gap ---")
    payload = {
        "topic_or_text": "",
        "document_id": doc_id
    }
    r = requests.post(f"{base_url}/api/generate_study_plan", json=payload)
    plan = r.json()
    print("Generated study plan title:", plan.get("title"))
    print("Generated study plan content snippet:", plan.get("markdown_content")[:200])

    # 4. Verify /api/generate_flashcards with document_id and empty topic_or_text
    print("\n--- Verifying /api/generate_flashcards Context Gap ---")
    payload = {
        "topic_or_text": "",
        "document_id": doc_id
    }
    r = requests.post(f"{base_url}/api/generate_flashcards", json=payload)
    fc = r.json()
    print("Generated flashcards count:", len(fc.get("flashcards", [])))

    # 5. Verify /api/generate_map does not save artifacts
    print("\n--- Verifying /api/generate_map Artifact Absence ---")
    # Create a project first
    r = requests.post(f"{base_url}/api/projects", json={"name": "Test Project"})
    proj_id = r.json()["id"]
    print(f"Created project ID: {proj_id}")
    
    payload = {
        "topic_or_text": "Photosynthesis is the process used by plants.",
        "project_id": proj_id
    }
    r = requests.post(f"{base_url}/api/generate_map", json=payload)
    print("Concept Map response keys:", list(r.json().keys()))
    
    # Retrieve project artifacts to see if any concept_map artifact was created
    r = requests.get(f"{base_url}/api/projects/{proj_id}/artifacts")
    artifacts = r.json()
    print(f"Artifacts in project: {[a['type'] for a in artifacts]}")

    # 6. Verify invite email validation vulnerability
    print("\n--- Verifying Project Invite Email Validation ---")
    payload = {
        "email": "not-an-email-at-all",
        "role": "viewer"
    }
    r = requests.post(f"{base_url}/api/projects/{proj_id}/invite", json=payload)
    print("Invite status:", r.json())
    
    # Retrieve members list to see if the invalid email is pending
    r = requests.get(f"{base_url}/api/projects/{proj_id}/members")
    members = r.json()
    print("Pending invites:", [i["email"] for i in members.get("pending", [])])

    # Clean up
    print("\n--- Cleaning up ---")
    requests.delete(f"{base_url}/api/documents/{doc_id}")
    requests.delete(f"{base_url}/api/projects/{proj_id}")
    print("Cleanup done.")

def main():
    started = False
    proc = None
    if not is_backend_running():
        proc = start_backend()
        started = True
    else:
        print("Reusing already running backend.")
        
    try:
        run_verification()
    finally:
        if started and proc:
            print("Stopping backend...")
            proc.terminate()
            proc.wait()
            print("Backend stopped.")

if __name__ == "__main__":
    main()

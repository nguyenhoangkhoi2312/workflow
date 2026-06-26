import re
import os

with open('backend/main.py', 'r') as f:
    content = f.read()

# Add imports
if 'import random' not in content:
    content = content.replace('import os', 'import os\nimport re\nimport random')

# 1. Fallback Flashcards
flashcard_fallback = """    if not current_key or current_key.startswith("AQ"):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', request.topic_or_text) if len(s.split()) > 5]
        if not sentences:
            sentences = ["The provided text is too short to generate flashcards."]
        
        flashcards = []
        for s in sentences[:10]:
            words = [w for w in s.split() if len(re.sub(r'[^a-zA-Z]', '', w)) >= 5]
            if words:
                target = random.choice(words)
                front = s.replace(target, "_______")
                target_clean = re.sub(r'[^a-zA-Z]', '', target)
                flashcards.append({"front": front, "back": target_clean})
        if not flashcards:
            flashcards = [{"front": "What is AI?", "back": "Artificial Intelligence is the simulation of human intelligence processes by machines."}]
        return {"flashcards": flashcards}"""

content = re.sub(r'    if not current_key or current_key\.startswith\("AQ"\):\s*return \{"flashcards": \[\{"front": "What is AI\?", "back": ".*?"\}\]\}', flashcard_fallback, content, flags=re.DOTALL)

# 2. Fallback Path
path_fallback = """    if not current_key or current_key.startswith("AQ"):
        return {
            "title": f"Learning Path: {request.topic}",
            "description": f"An algorithmically generated structured path for mastering {request.topic}.",
            "modules": [
                {
                    "title": f"Module 1: Introduction to {request.topic}",
                    "topics": [
                        {"title": f"What is {request.topic}?", "description": f"Understanding the basic definition and scope of {request.topic}.", "estimated_time": "30 mins"},
                        {"title": "History and Evolution", "description": "How this field has evolved over time.", "estimated_time": "45 mins"}
                    ]
                },
                {
                    "title": "Module 2: Core Concepts",
                    "topics": [
                        {"title": "Key Principles", "description": "The fundamental building blocks and rules.", "estimated_time": "60 mins"},
                        {"title": "Important Terminology", "description": "A glossary of terms you must know.", "estimated_time": "45 mins"}
                    ]
                },
                {
                    "title": "Module 3: Advanced Applications",
                    "topics": [
                        {"title": "Real-world Use Cases", "description": f"How {request.topic} is applied in industry.", "estimated_time": "90 mins"},
                        {"title": "Next Steps", "description": "Resources and projects to continue learning.", "estimated_time": "30 mins"}
                    ]
                }
            ]
        }"""

content = re.sub(r'    if not current_key or current_key\.startswith\("AQ"\):\s*return \{\s*"title": "Mock Path: Introduction to Machine Learning".*?\}\s*\}', path_fallback, content, flags=re.DOTALL)

# 3. Fallback Quiz
quiz_fallback = """    if not current_key or current_key.startswith("AQ"):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', request.topic_or_text) if len(s.split()) > 5]
        all_long_words = list(set([re.sub(r'[^a-zA-Z]', '', w) for w in request.topic_or_text.split() if len(re.sub(r'[^a-zA-Z]', '', w)) >= 5]))
        
        questions = []
        for i, s in enumerate(sentences[:5]):
            words = [w for w in s.split() if len(re.sub(r'[^a-zA-Z]', '', w)) >= 5]
            if words and len(all_long_words) >= 4:
                target = random.choice(words)
                target_clean = re.sub(r'[^a-zA-Z]', '', target)
                
                distractors = random.sample([w for w in all_long_words if w.lower() != target_clean.lower()], min(3, len(all_long_words)-1))
                options_text = [target_clean] + distractors
                random.shuffle(options_text)
                
                options = [{"id": chr(97+j), "text": opt} for j, opt in enumerate(options_text)]
                correct_id = [opt["id"] for opt in options if opt["text"] == target_clean][0]
                
                questions.append({
                    "question": s.replace(target, "_______"),
                    "options": options,
                    "correct_option_id": correct_id,
                    "explanation": f"The missing word is '{target_clean}' from the original text."
                })
        
        if not questions:
            questions = [{
                "question": "What is 2+2?",
                "options": [{"id": "a", "text": "3"}, {"id": "b", "text": "4"}, {"id": "c", "text": "5"}, {"id": "d", "text": "6"}],
                "correct_option_id": "b",
                "explanation": "2+2 equals 4."
            }]

        return {
            "title": "Algorithmic Reading Comprehension Quiz",
            "questions": questions
        }"""

content = re.sub(r'    if not current_key or current_key\.startswith\("AQ"\):\s*return \{\s*"title": "Mock Quiz".*?\]\s*\}', quiz_fallback, content, flags=re.DOTALL)


# 4. Fallback Notes
notes_fallback = """    if not current_key or current_key.startswith("AQ"):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', request.topic_or_text) if s.strip()]
        
        summary = " ".join(sentences[:2]) if sentences else "No text provided."
        
        key_points = []
        for s in sentences[2:10]:
            if any(keyword in s.lower() for keyword in [" is ", " are ", " important", " must", " key ", " defined"]):
                key_points.append(s)
        
        if not key_points:
            key_points = sentences[2:7] # Fallback to next 5 sentences
            
        sections = []
        if key_points:
            sections.append({"heading": "Key Information", "bullet_points": key_points})
            
        other_points = sentences[10:15]
        if other_points:
            sections.append({"heading": "Additional Details", "bullet_points": other_points})

        return {
            "title": "Algorithmically Extracted Notes",
            "summary": summary,
            "sections": sections
        }"""

content = re.sub(r'    if not current_key or current_key\.startswith\("AQ"\):\s*return \{\s*"title": "Mock Notes".*?\]\s*\}', notes_fallback, content, flags=re.DOTALL)


with open('backend/main.py', 'w') as f:
    f.write(content)

print("Injected NLP heuristics into backend/main.py")

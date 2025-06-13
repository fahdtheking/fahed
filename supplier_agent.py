
import transcribe_audio
import analyze_text
import os
import sqlite3
import openai

def get_dynamic_questions(form_data):
    """
    Uses OpenAI GPT to generate interview questions based on supplier registration form data.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"""
    You are an onboarding AI for a B2B marketplace. Given the following supplier registration form data, generate 5-7 specific, clear, and relevant interview questions to verify the supplier's legitimacy, honesty, and suitability. Only return the questions as a Python list of strings.

    Registration Form Data:
    {form_data}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful onboarding assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.2
    )
    # Extract questions from the response
    import ast
    try:
        questions = ast.literal_eval(response.choices[0].message['content'])
        if isinstance(questions, list):
            return questions
    except Exception:
        pass
    # Fallback: split by lines if not a valid Python list
    return [q.strip('- ').strip() for q in response.choices[0].message['content'].split('\n') if q.strip()]

def initiate_supplier_interview(supplier_name="New Supplier", form_data=None):
    print(f"\n--- Initiating interview for {supplier_name} ---")
    # Dynamically generate questions based on the registration form
    if form_data:
        questions = get_dynamic_questions(form_data)
    else:
        questions = [
            "What is your company name and how long have you been in business?",
            "Can you describe your main products or services?",
            "Have you ever been involved in any disputes or legal issues?",
            "How do you ensure the quality and authenticity of your products?",
            "What payment methods do you accept?",
            "Can you provide references from other clients?"
        ]

    all_answers = []
    all_analyses = []
    total_score = 0

    for idx, question in enumerate(questions, 1):
        print(f"\nQuestion {idx}: {question}")
        audio_filename = f"supplier_{supplier_name.replace(' ', '_')}_q{idx}.wav"
        recorded_file_path = transcribe_audio.record_audio(filename=audio_filename, duration=20)
        transcribed_text = transcribe_audio.transcribe_audio_file(recorded_file_path)
        print(f"Answer: {transcribed_text}")
        analysis = analyze_text.analyze_text(transcribed_text)
        all_answers.append({"question": question, "answer": transcribed_text})
        all_analyses.append(analysis)
        total_score += analysis["trust_score"]
        if os.path.exists(recorded_file_path):
            os.remove(recorded_file_path)

    # Aggregate trust score (average)
    avg_score = int(total_score / len(questions))
    # Decision logic
    if avg_score >= 80:
        decision = "approve"
    elif avg_score >= 50:
        decision = "flag for review"
    else:
        decision = "reject"

    # Store Results
    conn = sqlite3.connect("supplier_verification.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS supplier_verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT,
            trust_score INTEGER,
            decision TEXT
        )
    """)
    c.execute("INSERT INTO supplier_verification (supplier_name, trust_score, decision) VALUES (?, ?, ?)",
              (supplier_name, avg_score, decision))
    conn.commit()
    conn.close()

    return {
        "supplier_name": supplier_name,
        "questions_and_answers": all_answers,
        "analyses": all_analyses,
        "trust_score": avg_score,
        "decision": decision
    }

if __name__ == "__main__":
    initiate_supplier_interview("Acme Solutions Inc.")
    initiate_supplier_interview("Global Suppliers LLC")

import os
import json
import google.generativeai as genai
from datetime import datetime, timezone
from fastapi import HTTPException
from config import GEMINI_API_KEY, MAX_DAILY_AI_CALLS_PER_USER
from services.firebase_service import db

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def clean_json_response(text: str) -> str:
    """Removes markdown formatting and code fences from the AI JSON response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
        
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def check_rate_limit(user_id: str):
    """Checks if the user has exceeded their daily AI call limit."""
    if not db:
        print("Warning: Rate limiter skipped because db is not initialized.")
        return
        
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    user_ref = db.collection("users").document(user_id)
    
    try:
        doc = user_ref.get()
        if doc.exists:
            data = doc.to_dict()
            usage = data.get("ai_usage", {})
            count = usage.get(today, 0)
            
            if count >= MAX_DAILY_AI_CALLS_PER_USER:
                raise HTTPException(status_code=429, detail="Daily AI call limit exceeded.")
            
            # Increment usage
            usage[today] = count + 1
            user_ref.update({"ai_usage": usage})
        else:
            # Initialize usage
            user_ref.set({"ai_usage": {today: 1}}, merge=True)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error checking rate limit: {e}")
        # Proceed if Firestore fails, to not block entirely, or choose to block.
        # We allow it to proceed to be safe.

def read_prompt(filename: str) -> str:
    """Reads a prompt template from the prompts folder."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def score_job_fit(user_id: str, resume_text: str, job_description: str, company_name: str) -> dict:
    check_rate_limit(user_id)
    template = read_prompt("fit_scoring.txt")
    prompt = template.format(
        resume_text=resume_text, 
        job_description=job_description, 
        company_name=company_name
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error scoring job fit: {str(e)}")

def tailor_resume(user_id: str, original_resume: str, job_description: str, job_title: str, company_name: str) -> dict:
    check_rate_limit(user_id)
    template = read_prompt("resume_tailor.txt")
    prompt = template.format(
        original_resume=original_resume,
        job_description=job_description,
        job_title=job_title,
        company_name=company_name
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error tailoring resume: {str(e)}")

def generate_cover_letter(user_id: str, resume_summary: str, job_description: str, job_title: str, company_name: str, tone: str) -> dict:
    check_rate_limit(user_id)
    template = read_prompt("cover_letter.txt")
    prompt = template.format(
        resume_summary=resume_summary,
        job_description=job_description,
        job_title=job_title,
        company_name=company_name,
        tone=tone
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error generating cover letter: {str(e)}")

def draft_outreach_message(user_id: str, candidate_name: str, job_title: str, company_name: str, recruiter_name: str, channel: str, candidate_highlights: str) -> dict:
    check_rate_limit(user_id)
    template = read_prompt("outreach_message.txt")
    prompt = template.format(
        candidate_name=candidate_name,
        job_title=job_title,
        company_name=company_name,
        recruiter_name=recruiter_name,
        channel=channel,
        candidate_highlights=candidate_highlights
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error drafting outreach message: {str(e)}")

def generate_interview_questions(user_id: str, job_description: str, job_title: str, tailored_resume: str) -> list:
    check_rate_limit(user_id)
    template = read_prompt("interview_questions.txt")
    prompt = template.format(
        job_description=job_description,
        job_title=job_title,
        tailored_resume=tailored_resume
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error generating interview questions: {str(e)}")

def evaluate_mock_answer(user_id: str, interview_question: str, candidate_answer: str, job_title: str, company_name: str, skill_being_tested: str) -> dict:
    check_rate_limit(user_id)
    template = read_prompt("mock_interview.txt")
    prompt = template.format(
        interview_question=interview_question,
        candidate_answer=candidate_answer,
        job_title=job_title,
        company_name=company_name,
        skill_being_tested=skill_being_tested
    )
    try:
        response = model.generate_content(prompt)
        cleaned = clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error evaluating mock answer: {str(e)}")
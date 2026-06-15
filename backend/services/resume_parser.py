import io
import re
from datetime import datetime, timezone
import PyPDF2
from docx import Document
from fastapi import HTTPException
from services.firebase_service import db
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini for the helper summary
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from all pages of a PDF file."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text_chunks = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_chunks.append(text)
        return "\n".join(text_chunks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text from all paragraphs in a DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text_chunks = [para.text for para in doc.paragraphs if para.text]
        return "\n".join(text_chunks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read DOCX: {str(e)}")

def clean_text(raw_text: str) -> str:
    """Removes excessive blank lines and strips leading/trailing whitespace."""
    lines = raw_text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)

def detect_sections(text: str) -> list:
    """Performs a basic check for common resume section headings."""
    common_headings = ["Experience", "Education", "Skills", "Projects", "Summary", "Objective", "Certifications", "Languages", "Publications"]
    found = []
    text_lower = text.lower()
    
    for heading in common_headings:
        # Check if the heading exists as an isolated word/phrase
        if re.search(r'\b' + heading.lower() + r'\b', text_lower):
            found.append(heading)
    return found

def generate_ai_summary(resume_text: str) -> str:
    """Creates a short 150-word plain English summary of the candidate's profile."""
    prompt = f"""
    You are an expert career coach. Summarize the following resume in plain English in around 150 words.
    Focus on their core profession, years of experience, key skills, and top achievements.
    Do not use markdown, just return standard plain text.
    
    Resume:
    {resume_text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return "Summary could not be generated."

def parse_and_store_resume(user_id: str, file_bytes: bytes, filename: str) -> dict:
    """Main service function to parse a resume, analyze it, and store it in Firestore."""
    ext = filename.lower().split('.')[-1]
    
    # 1 & 2. Detect and Extract Text
    if ext == 'pdf':
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext in ['doc', 'docx']:
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX are allowed.")
        
    # 3. Clean Text
    cleaned_text = clean_text(raw_text)
    word_count = len(cleaned_text.split())
    
    if word_count < 20:
        raise HTTPException(status_code=400, detail="The document appears to be empty or an image-based PDF. Could not extract text.")
    
    # 4. Basic Structured Summary Analysis
    # Extremely basic regex for contact info
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    has_contact_info = bool(re.search(email_pattern, cleaned_text) or re.search(phone_pattern, cleaned_text))
    
    detected_sections = detect_sections(cleaned_text)
    
    # 5. Generate AI Summary
    ai_summary = generate_ai_summary(cleaned_text)
    
    # Combine everything
    data = {
        "user_id": user_id,
        "filename": filename,
        "raw_text": cleaned_text,
        "summary": ai_summary,
        "word_count": word_count,
        "has_contact_info": has_contact_info,
        "detected_sections": detected_sections,
        "uploaded_at": datetime.now(timezone.utc)
    }
    
    # 6. Store in Firestore
    if db:
        try:
            doc_ref = db.collection("resumes").document()
            data["resume_id"] = doc_ref.id
            doc_ref.set(data)
        except Exception as e:
            print(f"Error saving to Firestore: {e}")
            raise HTTPException(status_code=500, detail="Failed to save resume to database.")
    else:
        print("Warning: Firestore DB not initialized. Resume not saved.")
        data["resume_id"] = "local_test_id"
        
    return data

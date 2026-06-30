import json
import google.generativeai as genai
from app.cores.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a resume analysis assistant. Compare the candidate's resume text against a job description and respond with ONLY valid JSON (no markdown, no preamble, no code fences) in exactly this shape:

{
  "match_score": <integer 0-100>,
  "matching_skills": [<string>, ...],
  "missing_skills": [<string>, ...],
  "summary": "<2-3 sentence summary of fit>",
  "tailored_resume": {
    "professional_summary": "<rewritten 2-3 sentence summary tailored to the JD>",
    "skills": [<string>, ...],
    "experience_bullets": [<string>, ...]
  }
}
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
)

def analyze_resume_against_jd(resume_text: str, jd_text: str) -> dict:
    user_prompt = f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""

    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    raw_content = response.text.strip()

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        raise ValueError("AI returned invalid JSON response")
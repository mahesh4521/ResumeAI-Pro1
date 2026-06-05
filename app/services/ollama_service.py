import ollama
import json
import re
from typing import Dict, List, Any
import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            logger.info("GEMINI_API_KEY detected. Switching to Google Gemini API (gemini-1.5-flash).")
            genai.configure(api_key=self.gemini_api_key)
            self.use_gemini = True
        else:
            logger.info("No GEMINI_API_KEY detected. Defaulting to local Ollama client.")
            self.use_gemini = False
            self.client = ollama
        
    def _make_request(self, prompt: str, system_message: str = None) -> str:
        """Make a request to the configured AI model (Gemini or Ollama)"""
        if self.use_gemini:
            try:
                # Initialize Gemini model
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_message
                )
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.9,
                        max_output_tokens=2000
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"Error making Gemini request: {str(e)}")
                return ""
        else:
            try:
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                )
                return response['message']['content']
            except Exception as e:
                logger.error(f"Error making Ollama request: {str(e)}")
                return ""
    
    async def chat(self, message: str) -> str:
        """Simple chat method for testing"""
        return self._make_request(message)
    
    def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """Extract skills from resume text using Ollama"""
        system_message = """You are an expert resume analyzer. Extract technical and professional skills from the given resume text. 
        Return only a JSON array of skills, nothing else. Focus on concrete skills like programming languages, tools, frameworks, certifications, etc."""
        
        prompt = f"""Extract all skills from this resume text:

{resume_text}

Return only a JSON array of skills like: ["Python", "React", "Project Management", "AWS"]"""

        response = self._make_request(prompt, system_message)
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                skills = json.loads(json_match.group())
                return skills if isinstance(skills, list) else []
        except:
            pass
            
        # Fallback: parse skills manually
        skills = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '-', '*')):
                # Remove quotes and clean up
                skill = re.sub(r'^["\'-]+|["\'-]+$', '', line)
                if skill and len(skill) > 1:
                    skills.append(skill)
        
        return skills[:20]  # Limit to 20 skills
    
    def analyze_skills_gap(self, resume_skills: List[str], job_description: str) -> Dict[str, Any]:
        """Analyze skills gap between resume and job requirements"""
        system_message = """You are an expert HR analyst. Compare the candidate's skills with job requirements and identify gaps. 
        Return a JSON response with matched_skills, missing_skills, and skill_gaps arrays."""
        
        prompt = f"""Analyze the skills gap between these candidate skills and job requirements:

CANDIDATE SKILLS:
{', '.join(resume_skills)}

JOB DESCRIPTION:
{job_description}

Return JSON with this exact structure:
{{
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"], 
    "skill_gaps": [
        {{
            "skill": "skill_name",
            "importance": "High|Medium|Low",
            "current_level": "None|Beginner|Intermediate|Advanced",
            "required_level": "Beginner|Intermediate|Advanced"
        }}
    ]
}}"""

        response = self._make_request(prompt, system_message)
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except:
            pass
            
        # Fallback response
        return {
            "matched_skills": resume_skills[:min(5, len(resume_skills))],
            "missing_skills": ["Communication", "Leadership", "Problem Solving"],
            "skill_gaps": [
                {
                    "skill": "Advanced Python",
                    "importance": "High",
                    "current_level": "Intermediate",
                    "required_level": "Advanced"
                }
            ]
        }
    
    def score_resume(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Score resume against job description"""
        system_message = """You are an expert resume evaluator. Score the resume against the job description on a scale of 0-100. 
        Provide scores for different categories and an overall score. Return JSON format."""
        
        prompt = f"""Score this resume against the job description:

RESUME:
{resume_text[:2000]}...

JOB DESCRIPTION:
{job_description}

Return JSON with this structure:
{{
    "overall_score": 85,
    "category_scores": {{
        "technical_skills": 80,
        "experience": 90,
        "education": 75,
        "achievements": 88
    }}
}}"""

        response = self._make_request(prompt, system_message)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except:
            pass
            
        # Fallback scoring
        return {
            "overall_score": 78,
            "category_scores": {
                "technical_skills": 75,
                "experience": 82,
                "education": 70,
                "achievements": 80
            }
        }
    
    def generate_upskilling_suggestions(self, missing_skills: List[str], job_description: str) -> List[Dict[str, Any]]:
        """Generate upskilling suggestions based on missing skills"""
        system_message = """You are a career development expert. Generate practical upskilling suggestions with resources and timelines. 
        Return JSON array of suggestions."""
        
        prompt = f"""Generate upskilling suggestions for these missing skills:

MISSING SKILLS:
{', '.join(missing_skills)}

JOB CONTEXT:
{job_description[:1000]}

Return JSON array with this structure:
[
    {{
        "skill": "skill_name",
        "priority": "High|Medium|Low",
        "estimated_time": "1-2 months",
        "resources": ["resource1", "resource2", "resource3"]
    }}
]"""

        response = self._make_request(prompt, system_message)
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result if isinstance(result, list) else []
        except:
            pass
            
        # Fallback suggestions
        suggestions = []
        for skill in missing_skills[:5]:
            suggestions.append({
                "skill": skill,
                "priority": "High" if len(suggestions) < 2 else "Medium",
                "estimated_time": "2-3 months",
                "resources": [
                    f"Online course for {skill}",
                    f"{skill} documentation",
                    f"Practice projects with {skill}"
                ]
            })
        
        return suggestions
    
    def generate_interview_questions(self, resume_text: str, job_description: str) -> List[str]:
        """Generate interview questions based on resume and job description"""
        system_message = """You are an experienced interviewer. Generate relevant interview questions based on the candidate's resume and job requirements. 
        Mix technical, behavioral, and role-specific questions."""
        
        prompt = f"""Generate 8-10 interview questions for this candidate:

RESUME SUMMARY:
{resume_text[:1500]}

JOB DESCRIPTION:
{job_description[:1000]}

Generate questions that test:
1. Technical skills
2. Behavioral competencies  
3. Experience relevance
4. Problem-solving abilities

Return questions as a simple list, one per line."""

        response = self._make_request(prompt, system_message)
        
        # Extract questions from response
        questions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering, bullets, and clean up
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^[-\*]\s*', '', line)
            line = line.strip('"\'')
            
            if line and len(line) > 20 and '?' in line:
                questions.append(line)
        
        # Fallback questions if parsing failed
        if not questions:
            questions = [
                "Tell me about your most challenging project and how you overcame obstacles.",
                "How do you stay updated with the latest technologies in your field?",
                "Describe a time when you had to learn a new skill quickly.",
                "What motivates you in your work?",
                "How do you handle tight deadlines and pressure?",
                "Tell me about a time you disagreed with a team member.",
                "What are your career goals for the next 2-3 years?",
                "How do you approach debugging and problem-solving?"
            ]
        
        return questions[:10]  # Limit to 10 questions

# Global instance
ollama_service = OllamaService()
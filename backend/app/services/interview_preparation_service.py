"""
AI-Powered Interview Preparation Service

Provides intelligent interview preparation including question generation,
real-time feedback, industry-specific tips, and salary negotiation practice.
"""
from typing import List, Dict, Optional
import random
from app.models.job import ExternalJob
from app.models.cv import CV


# Interview questions by field and level
INTERVIEW_QUESTIONS = {
    "computer_it": {
        "entry_level": [
            "What programming languages are you most comfortable with and why?",
            "Describe a project you worked on and your role in it.",
            "How do you approach debugging when you encounter an error?",
            "What's your experience with version control systems like Git?",
            "How do you stay updated with new technologies and programming languages?",
            "Describe a time you had to learn a new technology quickly.",
            "What do you know about our company and why do you want to work here?",
            "How do you handle tight deadlines in your work?",
            "Describe your experience working in a team environment.",
            "What's your approach to testing and quality assurance?"
        ],
        "mid_level": [
            "Describe a complex technical problem you solved and your approach.",
            "How do you design scalable systems and handle performance issues?",
            "What's your experience with cloud platforms and DevOps practices?",
            "How do you handle technical disagreements with team members?",
            "Describe your experience with database design and optimization.",
            "How do you approach code reviews and giving feedback to others?",
            "What's your experience with microservices architecture?",
            "How do you balance technical debt with new feature development?",
            "Describe a time you led a technical project or initiative.",
            "How do you approach system security and data protection?"
        ],
        "senior_level": [
            "How do you make architectural decisions and trade-offs?",
            "Describe your experience with team leadership and mentoring.",
            "How do you handle system failures and incident response?",
            "What's your approach to technical strategy and roadmap planning?",
            "How do you evaluate and adopt new technologies for your organization?",
            "Describe your experience with cross-functional collaboration.",
            "How do you manage technical budget and resource allocation?",
            "What's your approach to hiring and building high-performing teams?",
            "How do you handle stakeholder management and communication?",
            "Describe a major technical challenge you overcame as a leader."
        ],
        "executive_level": [
            "How do you align technical strategy with business goals?",
            "Describe your experience with digital transformation initiatives.",
            "How do you build and maintain strong engineering culture?",
            "What's your approach to technology investment and ROI analysis?",
            "How do you handle crisis management and major technical incidents?",
            "Describe your experience with mergers, acquisitions, or partnerships.",
            "How do you balance innovation with stability in your organization?",
            "What's your approach to talent retention and development?",
            "How do you communicate technical concepts to non-technical stakeholders?",
            "Describe your vision for the future of technology in your industry."
        ]
    },
    "engineering": {
        "entry_level": [
            "What CAD software are you proficient in?",
            "Describe a design project you worked on during your studies.",
            "How do you approach safety in engineering design?",
            "What's your experience with project management tools?",
            "How do you handle design conflicts or revisions?",
            "Describe your understanding of industry standards and codes.",
            "What areas of engineering interest you most?",
            "How do you approach problem-solving in engineering?",
            "Describe your experience with hands-on projects or internships.",
            "What do you know about our company's engineering projects?"
        ],
        "mid_level": [
            "Describe a complex engineering project you managed.",
            "How do you handle budget constraints in engineering projects?",
            "What's your experience with project management methodologies?",
            "How do you ensure quality control in your work?",
            "Describe your experience with client interactions and requirements.",
            "How do you approach sustainability in engineering design?",
            "What's your experience with regulatory compliance?",
            "How do you handle technical challenges or failures?",
            "Describe your experience with mentoring junior engineers.",
            "How do you stay current with engineering standards and technologies?"
        ],
        "senior_level": [
            "How do you approach strategic planning for engineering projects?",
            "Describe your experience with cross-functional team leadership.",
            "How do you handle complex stakeholder requirements?",
            "What's your approach to risk management in engineering?",
            "Describe your experience with innovation and process improvement.",
            "How do you balance cost, quality, and timeline in projects?",
            "What's your experience with international engineering standards?",
            "How do you develop and maintain client relationships?",
            "Describe your approach to contract negotiation and proposals.",
            "How do you handle crisis situations in engineering projects?"
        ],
        "executive_level": [
            "How do you align engineering strategy with business objectives?",
            "Describe your experience with large-scale engineering programs.",
            "How do you build and maintain engineering excellence?",
            "What's your approach to technology investment and modernization?",
            "How do you handle regulatory and compliance challenges?",
            "Describe your experience with M&A due diligence from engineering perspective.",
            "How do you develop engineering talent and succession planning?",
            "What's your approach to sustainability and environmental responsibility?",
            "How do you communicate engineering value to business leaders?",
            "Describe your vision for the future of engineering in your industry."
        ]
    },
    "health": {
        "entry_level": [
            "What clinical procedures are you most experienced with?",
            "How do you handle difficult patient interactions?",
            "Describe your experience with electronic health record systems.",
            "What's your approach to patient safety and infection control?",
            "How do you handle high-stress situations in healthcare?",
            "Describe your experience working in multidisciplinary teams.",
            "What medical certifications do you hold?",
            "How do you stay updated with medical advancements?",
            "Describe your experience with patient education.",
            "What draws you to healthcare as a career?"
        ],
        "mid_level": [
            "Describe a complex patient case you managed.",
            "How do you handle conflicts with patients or families?",
            "What's your experience with quality improvement initiatives?",
            "How do you approach mentorship of junior healthcare professionals?",
            "Describe your experience with healthcare technology implementation.",
            "How do you handle ethical dilemmas in healthcare?",
            "What's your experience with research and evidence-based practice?",
            "How do you manage competing priorities in healthcare settings?",
            "Describe your experience with interdisciplinary collaboration.",
            "How do you approach patient-centered care?"
        ],
        "senior_level": [
            "How do you approach healthcare leadership and management?",
            "Describe your experience with quality metrics and patient outcomes.",
            "How do you handle healthcare policy and regulatory changes?",
            "What's your approach to staff development and retention?",
            "Describe your experience with healthcare technology adoption.",
            "How do you manage budget constraints in healthcare delivery?",
            "What's your experience with healthcare accreditation processes?",
            "How do you handle public health emergencies or crises?",
            "Describe your approach to patient safety and risk management.",
            "How do you develop and implement healthcare programs?"
        ],
        "executive_level": [
            "How do you align healthcare strategy with patient outcomes?",
            "Describe your experience with healthcare system transformation.",
            "How do you build and maintain healthcare excellence?",
            "What's your approach to healthcare policy and advocacy?",
            "How do you handle healthcare economics and financial sustainability?",
            "Describe your experience with healthcare partnerships and collaborations.",
            "How do you develop healthcare leadership talent?",
            "What's your approach to healthcare innovation and research?",
            "How do you communicate healthcare value to stakeholders?",
            "Describe your vision for the future of healthcare delivery."
        ]
    },
    "business_finance": {
        "entry_level": [
            "What financial analysis tools are you proficient with?",
            "Describe a financial analysis project you worked on.",
            "How do you approach data analysis and reporting?",
            "What's your experience with financial software systems?",
            "How do you handle tight deadlines in financial reporting?",
            "Describe your understanding of basic accounting principles.",
            "What areas of business or finance interest you most?",
            "How do you approach problem-solving in business contexts?",
            "Describe your experience with Excel and data visualization.",
            "What do you know about our company's business model?"
        ],
        "mid_level": [
            "Describe a complex financial analysis you performed.",
            "How do you handle budget management and forecasting?",
            "What's your experience with financial modeling and valuation?",
            "How do you approach risk assessment in financial decisions?",
            "Describe your experience with stakeholder communication.",
            "How do you handle financial discrepancies or audits?",
            "What's your experience with cross-functional collaboration?",
            "How do you approach business process improvement?",
            "Describe your experience with financial reporting compliance.",
            "How do you stay current with financial regulations and trends?"
        ],
        "senior_level": [
            "How do you approach strategic financial planning?",
            "Describe your experience with M&A or capital raising.",
            "How do you handle complex financial negotiations?",
            "What's your approach to risk management and mitigation?",
            "Describe your experience with financial systems implementation.",
            "How do you balance financial discipline with business growth?",
            "What's your experience with investor relations?",
            "How do you develop financial talent and teams?",
            "Describe your approach to financial governance and compliance.",
            "How do you handle financial crises or market downturns?"
        ],
        "executive_level": [
            "How do you align financial strategy with business objectives?",
            "Describe your experience with capital allocation and investment.",
            "How do you build and maintain financial excellence?",
            "What's your approach to financial technology and innovation?",
            "How do you handle regulatory and compliance challenges?",
            "Describe your experience with financial partnerships and alliances.",
            "How do you develop financial leadership talent?",
            "What's your approach to financial sustainability and growth?",
            "How do you communicate financial strategy to stakeholders?",
            "Describe your vision for the future of finance in your industry."
        ]
    }
}


# Behavioral interview questions
BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you had to work with a difficult colleague.",
    "Describe a situation where you had to meet a tight deadline.",
    "Tell me about a time you made a mistake and how you handled it.",
    "Describe a project where you had to lead a team.",
    "Tell me about a time you had to adapt to significant change.",
    "Describe a situation where you had to persuade someone.",
    "Tell me about a time you had to handle a dissatisfied client.",
    "Describe a project where you had to innovate or solve a complex problem.",
    "Tell me about a time you had to prioritize competing demands.",
    "Describe a situation where you had to learn something new quickly."
]


# Salary negotiation scenarios
SALARY_NEGOTIATION_SCENARIOS = [
    {
        "scenario": "The company offers below your expected salary range.",
        "company_offer": "We can offer $75,000.",
        "user_expectation": "$85,000 - $95,000",
        "strategy": "Express enthusiasm, highlight value, provide market data, suggest a range.",
        "suggested_response": "I'm very excited about this opportunity and confident I can bring significant value to the team. Based on my research of market rates for this role and my experience, I was expecting something in the $85,000-$95,000 range. Given the value I can bring, would it be possible to consider something closer to that range?"
    },
    {
        "scenario": "The company offers a good base salary but limited benefits.",
        "company_offer": "$90,000 with standard benefits.",
        "user_expectation": "$90,000 with enhanced benefits.",
        "strategy": "Focus on total compensation package, negotiate benefits instead of salary.",
        "suggested_response": "The base salary is very competitive and I appreciate the offer. I was hoping we could discuss the benefits package. Would it be possible to enhance the healthcare coverage, add a 401k match, or consider additional vacation days?"
    },
    {
        "scenario": "The company claims budget constraints.",
        "company_offer": "We have a strict budget cap at $80,000.",
        "user_expectation": "$90,000.",
        "strategy": "Negotiate non-monetary benefits, performance-based increases, signing bonus.",
        "suggested_response": "I understand budget constraints. Could we discuss other forms of compensation that might work within the budget? Perhaps a signing bonus, performance-based bonuses, additional vacation time, or professional development budget?"
    },
    {
        "scenario": "The company asks for your salary expectations first.",
        "company_offer": "What are your salary expectations?",
        "user_expectation": "$85,000 - $95,000.",
        "strategy": "Provide a range based on market research, not your minimum.",
        "suggested_response": "Based on my research of similar roles in the market and considering my experience and skills, I'm looking for something in the $85,000-$95,000 range. However, I'm flexible depending on the total compensation package and growth opportunities."
    }
]


class InterviewPreparationService:
    """Service for AI-powered interview preparation and practice."""
    
    def __init__(self):
        self.interview_questions = INTERVIEW_QUESTIONS
        self.behavioral_questions = BEHAVIORAL_QUESTIONS
        self.salary_scenarios = SALARY_NEGOTIATION_SCENARIOS
    
    def generate_interview_questions(self, job: ExternalJob, cv: Optional[CV] = None) -> Dict:
        """Generate personalized interview questions based on job and CV."""
        # Determine field and level
        field = job.field if job.field and job.field != "other" else "computer_it"
        
        # Determine experience level from CV or job requirements
        experience_level = self._determine_experience_level(cv, job)
        
        # Get field-specific questions
        field_questions = self.interview_questions.get(field, self.interview_questions["computer_it"])
        level_questions = field_questions.get(experience_level, field_questions["entry_level"])
        
        # Select random questions (5-7)
        selected_questions = random.sample(level_questions, min(7, len(level_questions)))
        
        # Add behavioral questions (2-3)
        behavioral_selected = random.sample(self.behavioral_questions, min(3, len(self.behavioral_questions)))
        
        # Add job-specific questions
        job_specific = self._generate_job_specific_questions(job)
        
        return {
            "field": field,
            "experience_level": experience_level,
            "technical_questions": selected_questions,
            "behavioral_questions": behavioral_selected,
            "job_specific_questions": job_specific,
            "total_questions": len(selected_questions) + len(behavioral_selected) + len(job_specific),
            "preparation_tips": self._get_preparation_tips(field, experience_level)
        }
    
    def _determine_experience_level(self, cv: Optional[CV], job: ExternalJob) -> str:
        """Determine experience level from CV or job requirements."""
        if cv and cv.experience_level:
            level_mapping = {
                "entry_level": "entry_level",
                "junior": "entry_level",
                "mid_level": "mid_level", 
                "senior": "senior_level",
                "executive": "executive_level",
                "expert": "executive_level"
            }
            return level_mapping.get(cv.experience_level.lower(), "entry_level")
        
        # Fallback to job requirements analysis
        if job.requirements:
            requirements_lower = job.requirements.lower()
            if any(word in requirements_lower for word in ["senior", "lead", "principal", "architect"]):
                return "senior_level"
            elif any(word in requirements_lower for word in ["manager", "director", "head", "chief"]):
                return "executive_level"
            elif any(word in requirements_lower for word in ["mid", "3+", "experienced"]):
                return "mid_level"
        
        return "entry_level"
    
    def _generate_job_specific_questions(self, job: ExternalJob) -> List[str]:
        """Generate questions specific to the job description."""
        questions = []
        
        if job.title:
            questions.append(f"Why are you interested in this {job.title} position?")
        
        if job.company:
            questions.append(f"What do you know about {job.company} and why do you want to work here?")
        
        if job.requirements:
            questions.append("How does your experience align with the key requirements of this position?")
        
        if job.description:
            questions.append("What challenges in this role do you find most exciting?")
        
        return questions
    
    def _get_preparation_tips(self, field: str, experience_level: str) -> List[str]:
        """Get field and level-specific preparation tips."""
        tips = [
            "Research the company thoroughly before the interview",
            "Prepare specific examples using the STAR method (Situation, Task, Action, Result)",
            "Practice your answers out loud to improve confidence",
            "Prepare thoughtful questions to ask the interviewer",
            "Dress professionally and arrive early",
            "Follow up with a thank-you note within 24 hours"
        ]
        
        # Add field-specific tips
        field_tips = {
            "computer_it": [
                "Be prepared for technical assessments or coding challenges",
                "Review data structures, algorithms, and system design basics",
                "Have examples of projects with GitHub links ready",
                "Be ready to discuss your approach to problem-solving"
            ],
            "engineering": [
                "Review relevant engineering software and tools",
                "Be prepared to discuss design calculations and methodologies",
                "Have examples of projects with technical drawings",
                "Understand industry standards and safety protocols"
            ],
            "health": [
                "Review clinical procedures and best practices",
                "Be prepared to discuss patient care scenarios",
                "Have examples of handling difficult patient situations",
                "Stay updated on current healthcare protocols"
            ],
            "business_finance": [
                "Review financial analysis and modeling techniques",
                "Be prepared to discuss specific achievements with metrics",
                "Have examples of process improvements you've implemented",
                "Understand current market trends and economic factors"
            ]
        }
        
        tips.extend(field_tips.get(field, field_tips["computer_it"]))
        
        # Add level-specific tips
        if experience_level in ["senior_level", "executive_level"]:
            tips.extend([
                "Be prepared to discuss leadership philosophy and experience",
                "Have examples of strategic decisions you've made",
                "Be ready to discuss team building and mentoring",
                "Prepare to discuss your vision and approach to challenges"
            ])
        
        return tips[:10]  # Return top 10 tips
    
    def analyze_answer_quality(self, question: str, answer: str) -> Dict:
        """Analyze the quality of an interview answer using enhanced NLP."""
        if not answer or len(answer) < 30:
            return {
                "score": 0,
                "feedback": "Your answer is too short. Provide more detail and examples.",
                "strengths": [],
                "improvements": ["Add more detail", "Provide specific examples", "Use the STAR method"]
            }

        score = 40  # Base score for providing an answer
        strengths = []
        improvements = []
        
        answer_lower = answer.lower()
        answer_words = answer_lower.split()
        
        # Check answer length and quality
        if len(answer) > 100:
            score += 10
            strengths.append("Good length with sufficient detail")
        elif len(answer) < 50:
            improvements.append("Your answer is brief - consider adding more detail")
        
        # Check for STAR method indicators (Situation, Task, Action, Result)
        star_indicators = {
            "situation": ["situation", "context", "background", "when i was", "in my previous role"],
            "task": ["task", "challenge", "problem", "goal", "objective", "needed to"],
            "action": ["action", "i did", "i took", "i implemented", "i created", "i managed", "i led"],
            "result": ["result", "outcome", "achieved", "successful", "completed", "accomplished", "as a result"]
        }
        
        star_score = 0
        for star_type, indicators in star_indicators.items():
            if any(indicator in answer_lower for indicator in indicators):
                star_score += 5
                if star_type == "result":
                    strengths.append("Includes measurable results")
        
        if star_score >= 15:
            score += 20
            strengths.append("Well-structured response using STAR method")
        elif star_score >= 10:
            score += 10
            strengths.append("Some STAR structure present")
        else:
            improvements.append("Use the STAR method: Situation, Task, Action, Result")
        
        # Check for specific examples/numbers/metrics
        has_numbers = any(char.isdigit() for char in answer)
        has_quantifiable = any(word in answer_lower for word in ["percent", "%", "increase", "decrease", "dollar", "$", "revenue", "savings", "time", "hours", "days", "months", "years"])
        
        if has_numbers and has_quantifiable:
            score += 15
            strengths.append("Includes specific metrics and quantifiable results")
        elif has_numbers:
            score += 8
            strengths.append("Includes some numerical data")
        else:
            improvements.append("Add specific metrics (e.g., 'increased sales by 25%')")
        
        # Check for action verbs (stronger list)
        action_verbs = [
            "led", "managed", "developed", "created", "implemented", "achieved", "improved", "increased",
            "reduced", "designed", "built", "launched", "delivered", "executed", "optimized", "solved",
            "coordinated", "directed", "supervised", "trained", "mentored", "analyzed", "researched"
        ]
        action_count = sum(1 for verb in action_verbs if verb in answer_lower)
        
        if action_count >= 3:
            score += 10
            strengths.append("Uses multiple strong action verbs")
        elif action_count >= 1:
            score += 5
            strengths.append("Uses action verbs")
        
        # Check for weak language to avoid
        weak_phrases = ["i think", "maybe", "possibly", "i guess", "probably", "kind of", "sort of"]
        weak_count = sum(1 for phrase in weak_phrases if phrase in answer_lower)
        
        if weak_count > 0:
            score -= 5
            improvements.append("Avoid uncertain language (use confident statements)")
        
        # Check for industry-specific keywords based on question
        tech_keywords = ["python", "javascript", "react", "django", "flask", "sql", "aws", "cloud", "machine learning", "data", "api"]
        business_keywords = ["revenue", "profit", "sales", "marketing", "customer", "growth", "strategy", "team", "management"]
        general_keywords = ["experience", "skill", "project", "team", "collaborate", "communicate", "result", "success"]
        
        relevant_keywords = []
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["programming", "code", "software", "technical", "development"]):
            relevant_keywords = [kw for kw in tech_keywords if kw in answer_lower]
        elif any(word in question_lower for word in ["business", "management", "strategy", "financial"]):
            relevant_keywords = [kw for kw in business_keywords if kw in answer_lower]
        else:
            relevant_keywords = [kw for kw in general_keywords if kw in answer_lower]
        
        if len(relevant_keywords) >= 2:
            score += 10
            strengths.append("Includes relevant technical/business keywords")
        
        # Check for completeness (addresses the question)
        question_words = set(question_lower.split())
        answer_word_set = set(answer_words)
        overlap = len(question_words.intersection(answer_word_set))
        
        if overlap >= 3:
            score += 5
            strengths.append("Directly addresses the question")
        
        # Check for personal pronouns (shows ownership)
        personal_pronouns = ["i", "my", "we", "our"]
        personal_count = sum(1 for pronoun in personal_pronouns if pronoun in answer_lower)
        
        if personal_count >= 2:
            score += 5
            strengths.append("Takes ownership with personal examples")
        
        # Cap score at 100
        score = max(0, min(score, 100))
        
        # Generate feedback based on score
        if score >= 85:
            feedback = "Excellent answer! Well-structured with specific examples and strong results."
        elif score >= 70:
            feedback = "Good answer with solid structure. Add more specific metrics for improvement."
        elif score >= 55:
            feedback = "Decent answer. Focus on adding more detail and using the STAR method."
        elif score >= 40:
            feedback = "Basic answer provided. Needs more structure, examples, and metrics."
        else:
            feedback = "Your answer needs significant improvement. Add detail, structure, and specific examples."
        
        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements[:5],  # Top 5 improvements
            "word_count": len(answer_words),
            "star_method_score": star_score
        }
    
    def get_salary_negotiation_scenario(self) -> Dict:
        """Get a random salary negotiation scenario for practice."""
        return random.choice(self.salary_scenarios)
    
    def get_all_salary_scenarios(self) -> List[Dict]:
        """Get all salary negotiation scenarios for comprehensive practice."""
        return self.salary_scenarios
    
    def generate_mock_interview(self, job: ExternalJob, cv: Optional[CV] = None, num_questions: int = 5) -> Dict:
        """Generate a complete mock interview session."""
        questions_data = self.generate_interview_questions(job, cv)
        
        # Combine all questions
        all_questions = (
            questions_data["technical_questions"][:3] +
            questions_data["behavioral_questions"][:1] +
            questions_data["job_specific_questions"][:1]
        )
        
        return {
            "job_title": job.title,
            "company": job.company,
            "field": questions_data["field"],
            "experience_level": questions_data["experience_level"],
            "questions": all_questions[:num_questions],
            "total_duration_estimate": f"{num_questions * 5} minutes",
            "preparation_tips": questions_data["preparation_tips"]
        }

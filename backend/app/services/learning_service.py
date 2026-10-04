"""
Personalized Learning & Skill Tracking Service

Creates personalized learning plans based on career goals, recommends specific courses and resources,
tracks learning progress with gamification, and integrates with learning platforms.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models.cv import CV
from app.models.user import User


# Learning resources by skill and field
LEARNING_RESOURCES = {
    "computer_it": {
        "python": {
            "courses": [
                {"name": "Python for Everybody", "platform": "Coursera", "duration": "4 weeks", "difficulty": "beginner"},
                {"name": "Complete Python Bootcamp", "platform": "Udemy", "duration": "12 hours", "difficulty": "beginner"},
                {"name": "Python Data Science", "platform": "DataCamp", "duration": "8 weeks", "difficulty": "intermediate"}
            ],
            "books": ["Python Crash Course", "Automate the Boring Stuff with Python", "Fluent Python"],
            "resources": ["Python Documentation", "Real Python", "Python.org Tutorial"]
        },
        "javascript": {
            "courses": [
                {"name": "JavaScript Algorithms and Data Structures", "platform": "FreeCodeCamp", "duration": "6 weeks", "difficulty": "intermediate"},
                {"name": "The Complete JavaScript Course", "platform": "Udemy", "duration": "27 hours", "difficulty": "beginner"},
                {"name": "JavaScript: Understanding the Weird Parts", "platform": "Udemy", "duration": "3 hours", "difficulty": "advanced"}
            ],
            "books": ["Eloquent JavaScript", "JavaScript: The Good Parts", "You Don't Know JS"],
            "resources": ["MDN JavaScript Guide", "JavaScript.info", "ES6 Features"]
        },
        "react": {
            "courses": [
                {"name": "React - The Complete Guide", "platform": "Udemy", "duration": "40 hours", "difficulty": "intermediate"},
                {"name": "Modern React with Redux", "platform": "Udemy", "duration": "45 hours", "difficulty": "intermediate"},
                {"name": "React.js: Zero to Hero", "platform": "Coursera", "duration": "8 weeks", "difficulty": "beginner"}
            ],
            "books": ["Learning React", "React Up & Running", "The Road to React"],
            "resources": ["React Documentation", "React.dev", "React Patterns"]
        },
        "machine learning": {
            "courses": [
                {"name": "Machine Learning Specialization", "platform": "Coursera", "duration": "3 months", "difficulty": "intermediate"},
                {"name": "Deep Learning Specialization", "platform": "Coursera", "duration": "4 months", "difficulty": "advanced"},
                {"name": "Introduction to Machine Learning", "platform": "Kaggle", "duration": "4 weeks", "difficulty": "beginner"}
            ],
            "books": ["Hands-On Machine Learning", "Python Machine Learning", "Introduction to Statistical Learning"],
            "resources": ["Scikit-learn Documentation", "TensorFlow Tutorials", "Kaggle Learn"]
        },
        "cloud": {
            "courses": [
                {"name": "AWS Cloud Practitioner", "platform": "AWS Training", "duration": "1 week", "difficulty": "beginner"},
                {"name": "Google Cloud Fundamentals", "platform": "Google Cloud Skills Boost", "duration": "2 weeks", "difficulty": "beginner"},
                {"name": "Azure Fundamentals", "platform": "Microsoft Learn", "duration": "2 weeks", "difficulty": "beginner"}
            ],
            "books": ["Cloud Computing for Dummies", "AWS Solutions Architect", "The Cloud Native Playbook"],
            "resources": ["AWS Documentation", "Google Cloud Documentation", "Azure Documentation"]
        }
    },
    "engineering": {
        "cad": {
            "courses": [
                {"name": "AutoCAD Essentials", "platform": "Autodesk", "duration": "4 weeks", "difficulty": "beginner"},
                {"name": "SolidWorks Fundamentals", "platform": "SolidWorks", "duration": "6 weeks", "difficulty": "beginner"},
                {"name": "Revit Architecture", "platform": "Autodesk", "duration": "8 weeks", "difficulty": "intermediate"}
            ],
            "books": ["AutoCAD 2024", "SolidWorks Bible", "Mastering Revit"],
            "resources": ["Autodesk Knowledge Network", "CAD Forum", "Engineering.com"]
        },
        "project management": {
            "courses": [
                {"name": "PMP Certification Training", "platform": "PMI", "duration": "8 weeks", "difficulty": "advanced"},
                {"name": "Project Management Professional", "platform": "Coursera", "duration": "6 weeks", "difficulty": "intermediate"},
                {"name": "Agile Project Management", "platform": "edX", "duration": "4 weeks", "difficulty": "beginner"}
            ],
            "books": ["PMBOK Guide", "Agile Project Management", "Scrum: The Art of Doing Twice the Work"],
            "resources": ["PMI.org", "Scrum Alliance", "ProjectManagement.com"]
        }
    },
    "health": {
        "health informatics": {
            "courses": [
                {"name": "Health Informatics Fundamentals", "platform": "Coursera", "duration": "6 weeks", "difficulty": "beginner"},
                {"name": "Digital Health Transformation", "platform": "edX", "duration": "8 weeks", "difficulty": "intermediate"},
                {"name": "Healthcare Data Analytics", "platform": "DataCamp", "duration": "4 weeks", "difficulty": "intermediate"}
            ],
            "books": ["Health Informatics", "Digital Health", "Healthcare Analytics"],
            "resources": ["AMIA", "HIMSS", "HealthIT.gov"]
        },
        "clinical skills": {
            "courses": [
                {"name": "Clinical Skills Foundation", "platform": "WHO", "duration": "4 weeks", "difficulty": "beginner"},
                {"name": "Advanced Clinical Practice", "platform": "Coursera", "duration": "8 weeks", "difficulty": "advanced"},
                {"name": "Patient Safety Fundamentals", "platform": "IHI", "duration": "2 weeks", "difficulty": "beginner"}
            ],
            "books": ["Clinical Skills", "Patient Safety", "Evidence-Based Practice"],
            "resources": ["WHO Guidelines", "CDC Guidelines", "Clinical Guidelines"]
        }
    },
    "business_finance": {
        "financial modeling": {
            "courses": [
                {"name": "Financial Modeling Fundamentals", "platform": "Coursera", "duration": "4 weeks", "difficulty": "beginner"},
                {"name": "Advanced Financial Modeling", "platform": "Udemy", "duration": "8 hours", "difficulty": "intermediate"},
                {"name": "Valuation Modeling", "platform": "Wharton Online", "duration": "6 weeks", "difficulty": "advanced"}
            ],
            "books": ["Financial Modeling", "Valuation", "Investment Valuation"],
            "resources": ["Investopedia", "CFA Institute", "Financial Times"]
        },
        "business analytics": {
            "courses": [
                {"name": "Business Analytics Specialization", "platform": "Coursera", "duration": "6 months", "difficulty": "intermediate"},
                {"name": "Data Analytics for Business", "platform": "Udemy", "duration": "6 hours", "difficulty": "beginner"},
                {"name": "Advanced Business Analytics", "platform": "edX", "duration": "8 weeks", "difficulty": "advanced"}
            ],
            "books": ["Business Analytics", "Data Science for Business", "Predictive Analytics"],
            "resources": ["Tableau Public", "Power BI Community", "Kaggle Datasets"]
        }
    }
}


# Achievement and badge system
ACHIEVEMENTS = {
    "first_course": {"name": "First Steps", "description": "Complete your first course", "icon": "🎯"},
    "skill_master": {"name": "Skill Master", "description": "Complete 3 courses in one skill", "icon": "🏆"},
    "quick_learner": {"name": "Quick Learner", "description": "Complete a course in half the expected time", "icon": "⚡"},
    "dedicated": {"name": "Dedicated Learner", "description": "Complete 10 courses total", "icon": "🔥"},
    "field_expert": {"name": "Field Expert", "description": "Complete courses covering all field skills", "icon": "🎓"},
    "consistency": {"name": "Consistent", "description": "Study for 7 consecutive days", "icon": "📅"},
    "perfect_score": {"name": "Perfect Score", "description": "Get 100% on course assessment", "icon": "💯"},
    "social_learner": {"name": "Social Learner", "description": "Complete 5 group projects", "icon": "👥"}
}


class LearningService:
    """Service for personalized learning and skill tracking."""
    
    def __init__(self):
        self.learning_resources = LEARNING_RESOURCES
        self.achievements = ACHIEVEMENTS
    
    def create_personalized_learning_plan(self, user: User, cv: Optional[CV] = None, career_goal: Optional[str] = None) -> Dict:
        """Create personalized learning plan based on career goals and current skills."""
        if not cv:
            return {"error": "No CV data available"}
        
        # Determine field
        field = cv.field if cv.field and cv.field != "other" else "computer_it"
        
        # Parse current skills
        current_skills = set()
        if cv.skills:
            try:
                import json
                skills_data = json.loads(cv.skills)
                if isinstance(skills_data, list):
                    current_skills = {str(skill).lower() for skill in skills_data}
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Get field-specific learning resources
        field_resources = self.learning_resources.get(field, self.learning_resources["computer_it"])
        
        # Identify skills to learn (missing skills)
        skills_to_learn = []
        for skill, resources in field_resources.items():
            if skill not in current_skills:
                skills_to_learn.append({
                    "skill": skill,
                    "resources": resources,
                    "priority": self._calculate_skill_priority(skill, career_goal),
                    "estimated_duration": self._estimate_learning_duration(skill)
                })
        
        # Sort by priority
        skills_to_learn.sort(key=lambda x: x["priority"], reverse=True)
        
        # Create learning timeline
        learning_timeline = self._create_learning_timeline(skills_to_learn[:5])  # Top 5 skills
        
        return {
            "field": field,
            "current_skills": list(current_skills),
            "skills_to_learn": skills_to_learn,
            "learning_timeline": learning_timeline,
            "total_estimated_duration": self._calculate_total_duration(learning_timeline),
            "recommended_start": self._get_recommended_start(skills_to_learn),
            "career_goal": career_goal or "Career advancement in current field"
        }
    
    def _calculate_skill_priority(self, skill: str, career_goal: Optional[str]) -> int:
        """Calculate priority of learning a skill based on career goals."""
        # High priority skills for most careers
        high_priority_skills = ["python", "javascript", "machine learning", "cloud", "data analysis", "project management"]
        
        priority = 50  # Base priority
        
        if skill in high_priority_skills:
            priority += 30
        
        if career_goal:
            goal_lower = career_goal.lower()
            if any(word in goal_lower for word in ["data", "analytics", "science"]):
                if skill in ["python", "machine learning", "data analysis"]:
                    priority += 20
            elif any(word in goal_lower for word in ["cloud", "devops", "infrastructure"]):
                if skill in ["cloud", "devops", "docker", "kubernetes"]:
                    priority += 20
            elif any(word in goal_lower for word in ["web", "frontend", "ui"]):
                if skill in ["javascript", "react", "css", "html"]:
                    priority += 20
        
        return min(priority, 100)
    
    def _estimate_learning_duration(self, skill: str) -> str:
        """Estimate learning duration for a skill."""
        # Rough estimates
        if skill in ["python", "javascript"]:
            return "4-6 weeks"
        elif skill in ["react", "machine learning", "cloud"]:
            return "6-8 weeks"
        elif skill in ["project management", "business analytics"]:
            return "4-6 weeks"
        else:
            return "4-8 weeks"
    
    def _create_learning_timeline(self, skills_to_learn: List[Dict]) -> List[Dict]:
        """Create a structured learning timeline."""
        timeline = []
        week_offset = 0
        
        for skill_data in skills_to_learn:
            duration_weeks = 6  # Default duration
            try:
                duration_str = skill_data["estimated_duration"]
                if "weeks" in duration_str:
                    week_nums = [int(s) for s in duration_str.split() if s.isdigit()]
                    if week_nums:
                        duration_weeks = max(week_nums)
            except:
                pass
            
            timeline.append({
                "skill": skill_data["skill"],
                "start_week": week_offset + 1,
                "end_week": week_offset + duration_weeks,
                "duration_weeks": duration_weeks,
                "priority": skill_data["priority"],
                "recommended_courses": skill_data["resources"]["courses"][:2],  # Top 2 courses
                "recommended_books": skill_data["resources"]["books"][:1]  # Top 1 book
            })
            
            week_offset += duration_weeks
        
        return timeline
    
    def _calculate_total_duration(self, timeline: List[Dict]) -> str:
        """Calculate total duration of learning plan."""
        if not timeline:
            return "0 weeks"
        
        total_weeks = max(item["end_week"] for item in timeline)
        
        if total_weeks < 4:
            return f"{total_weeks} weeks"
        elif total_weeks < 24:
            return f"{total_weeks // 4} months"
        else:
            return f"{total_weeks // 52} years"
    
    def _get_recommended_start(self, skills_to_learn: List[Dict]) -> Dict:
        """Get recommended starting point."""
        if not skills_to_learn:
            return {"skill": None, "reason": "No skills to learn"}
        
        top_skill = skills_to_learn[0]
        return {
            "skill": top_skill["skill"],
            "reason": f"Highest priority skill ({top_skill['priority']}% priority)",
            "first_course": top_skill["resources"]["courses"][0] if top_skill["resources"]["courses"] else None
        }
    
    def recommend_courses(self, skill: str, field: str = "computer_it") -> Dict:
        """Get course recommendations for a specific skill."""
        field_resources = self.learning_resources.get(field, self.learning_resources["computer_it"])
        skill_resources = field_resources.get(skill, {})
        
        if not skill_resources:
            return {
                "error": f"No learning resources found for skill: {skill}",
                "suggestion": "Try a different skill or check back later"
            }
        
        return {
            "skill": skill,
            "field": field,
            "courses": skill_resources.get("courses", []),
            "books": skill_resources.get("books", []),
            "resources": skill_resources.get("resources", []),
            "total_courses": len(skill_resources.get("courses", [])),
            "total_books": len(skill_resources.get("books", []))
        }
    
    def track_learning_progress(self, user_progress: Dict) -> Dict:
        """Track and analyze learning progress with gamification."""
        completed_courses = user_progress.get("completed_courses", [])
        total_courses = user_progress.get("total_courses_planned", 0)
        current_streak = user_progress.get("current_streak", 0)
        assessment_scores = user_progress.get("assessment_scores", [])
        
        # Calculate progress metrics
        completion_rate = int((len(completed_courses) / total_courses) * 100) if total_courses > 0 else 0
        average_score = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
        
        # Check for achievements
        unlocked_achievements = self._check_achievements(user_progress)
        
        # Generate progress insights
        insights = self._generate_progress_insights(completion_rate, average_score, current_streak)
        
        return {
            "completion_rate": completion_rate,
            "courses_completed": len(completed_courses),
            "courses_remaining": total_courses - len(completed_courses),
            "average_score": round(average_score, 1),
            "current_streak": current_streak,
            "unlocked_achievements": unlocked_achievements,
            "total_achievements": len(self.achievements),
            "insights": insights,
            "recommendation": self._get_progress_recommendation(completion_rate, current_streak)
        }
    
    def _check_achievements(self, user_progress: Dict) -> List[Dict]:
        """Check for unlocked achievements."""
        unlocked = []
        
        completed_courses = user_progress.get("completed_courses", [])
        assessment_scores = user_progress.get("assessment_scores", [])
        current_streak = user_progress.get("current_streak", 0)
        
        # First course
        if len(completed_courses) >= 1:
            unlocked.append(self.achievements["first_course"])
        
        # Dedicated learner
        if len(completed_courses) >= 10:
            unlocked.append(self.achievements["dedicated"])
        
        # Consistency
        if current_streak >= 7:
            unlocked.append(self.achievements["consistency"])
        
        # Perfect score
        if any(score == 100 for score in assessment_scores):
            unlocked.append(self.achievements["perfect_score"])
        
        # Quick learner (simplified check)
        if user_progress.get("completed_ahead_of_schedule", False):
            unlocked.append(self.achievements["quick_learner"])
        
        return unlocked
    
    def _generate_progress_insights(self, completion_rate: int, average_score: float, streak: int) -> List[str]:
        """Generate insights about learning progress."""
        insights = []
        
        if completion_rate >= 80:
            insights.append("Excellent progress! You're ahead of schedule.")
        elif completion_rate >= 50:
            insights.append("Good progress. Keep up the momentum!")
        elif completion_rate >= 25:
            insights.append("Making steady progress. Stay consistent!")
        else:
            insights.append("Just getting started. Focus on consistency.")
        
        if average_score >= 90:
            insights.append("Outstanding assessment performance!")
        elif average_score >= 70:
            insights.append("Good understanding of the material.")
        elif average_score >= 50:
            insights.append("Solid foundation, but room for improvement.")
        
        if streak >= 7:
            insights.append("Amazing consistency! You're building great habits.")
        elif streak >= 3:
            insights.append("Good consistency - keep the streak going!")
        
        return insights
    
    def _get_progress_recommendation(self, completion_rate: int, streak: int) -> str:
        """Get personalized recommendation based on progress."""
        if completion_rate >= 80 and streak >= 7:
            return "You're excelling! Consider taking on more challenging courses or starting a new skill."
        elif completion_rate >= 50:
            return "Great progress! Maintain your consistency and consider joining study groups."
        elif streak >= 7:
            return "Excellent consistency! Consider increasing your daily study time."
        elif completion_rate < 25:
            return "Focus on building a daily study habit. Start with just 15-30 minutes per day."
        else:
            return "Keep pushing forward! Consistency is key to success."
    
    def get_skill_validation_quizzes(self, skill: str) -> Dict:
        """Get micro-assessments for skill validation."""
        # Simplified quiz system - in production, this would integrate with learning platforms
        quiz_questions = {
            "python": [
                {"question": "What is the correct way to create a list in Python?", "options": ["list = []", "list = ()", "list = {}", "list = <"], "correct": 0},
                {"question": "Which keyword is used to define a function in Python?", "options": ["function", "def", "func", "define"], "correct": 1},
                {"question": "What does len() do in Python?", "options": ["Calculate length", "Create list", "Define function", "Import module"], "correct": 0}
            ],
            "javascript": [
                {"question": "How do you declare a variable in modern JavaScript?", "options": ["var x = 5", "let x = 5", "const x = 5", "Both B and C"], "correct": 3},
                {"question": "What is the correct way to write a for loop in JavaScript?", "options": ["for i = 0 to 10", "for (let i = 0; i < 10; i++)", "foreach i in range(10)", "loop i from 0 to 10"], "correct": 1},
                {"question": "Which method is used to add an element to the end of an array?", "options": ["push()", "pop()", "shift()", "unshift()"], "correct": 0}
            ]
        }
        
        questions = quiz_questions.get(skill, [])
        
        if not questions:
            return {
                "error": f"No quiz available for skill: {skill}",
                "message": "Quiz coming soon for this skill"
            }
        
        return {
            "skill": skill,
            "total_questions": len(questions),
            "questions": questions,
            "passing_score": 70,  # 70% to pass
            "estimated_time": f"{len(questions) * 2} minutes"
        }

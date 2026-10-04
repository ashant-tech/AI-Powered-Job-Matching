"""
Professional Network Analysis Service

Analyzes LinkedIn/social connections for job opportunities, identifies "weak ties" that lead to better
job opportunities, suggests networking events and communities, and provides industry-specific networking recommendations.
"""
from typing import List, Dict, Optional
from app.models.user import User
from app.models.cv import CV


# Networking events and communities by field
NETWORKING_RESOURCES = {
    "computer_it": {
        "events": [
            {"name": "Tech Meetups", "type": "local", "frequency": "monthly", "platform": "Meetup.com"},
            {"name": "Hackathons", "type": "competition", "frequency": "quarterly", "platform": "Devpost"},
            {"name": "Tech Conferences", "type": "conference", "frequency": "annual", "platform": "Various"},
            {"name": "AWS Community Days", "type": "community", "frequency": "annual", "platform": "AWS"},
            {"name": "Google Cloud Events", "type": "community", "frequency": "quarterly", "platform": "Google Cloud"}
        ],
        "communities": [
            {"name": "GitHub", "type": "code", "description": "Open source contribution and networking"},
            {"name": "Stack Overflow", "type": "forum", "description": "Technical Q&A and reputation building"},
            {"name": "Reddit r/programming", "type": "forum", "description": "Programming discussions and advice"},
            {"name": "Discord Tech Communities", "type": "chat", "description": "Real-time tech discussions"},
            {"name": "LinkedIn Tech Groups", "type": "professional", "description": "Professional networking and job opportunities"}
        ],
        "networking_tips": [
            "Contribute to open source projects on GitHub",
            "Attend local tech meetups and conferences",
            "Build a strong LinkedIn profile with recommendations",
            "Write technical blog posts to establish expertise",
            "Participate in hackathons to expand your network",
            "Join relevant Discord and Slack communities",
            "Engage thoughtfully on Stack Overflow and Reddit",
            "Connect with colleagues from past projects and roles"
        ]
    },
    "engineering": {
        "events": [
            {"name": "Engineering Conferences", "type": "conference", "frequency": "annual", "platform": "Various"},
            {"name": "Professional Society Meetings", "type": "professional", "frequency": "monthly", "platform": "ASCE, IEEE"},
            {"name": "Industry Workshops", "type": "workshop", "frequency": "quarterly", "platform": "Various"},
            {"name": "Trade Shows", "type": "exhibition", "frequency": "annual", "platform": "Various"},
            {"name": "Alumni Events", "type": "alumni", "frequency": "semi-annual", "platform": "Universities"}
        ],
        "communities": [
            {"name": "LinkedIn Engineering Groups", "type": "professional", "description": "Professional networking and job opportunities"},
            {"name": "Professional Society Forums", "type": "forum", "description": "Industry-specific discussions and resources"},
            {"name": "Engineering Alumni Networks", "type": "alumni", "description": "University and college alumni connections"},
            {"name": "Industry Associations", "type": "professional", "description": "Professional development and networking"},
            {"name": "Online Engineering Communities", "type": "forum", "description": "Technical discussions and knowledge sharing"}
        ],
        "networking_tips": [
            "Join professional engineering societies (ASCE, IEEE, ASME)",
            "Attend industry conferences and trade shows",
            "Maintain relationships with former colleagues and professors",
            "Participate in professional development workshops",
            "Engage with university alumni networks",
            "Contribute to industry forums and discussions",
            "Build relationships with suppliers and contractors",
            "Attend company-sponsored engineering events"
        ]
    },
    "health": {
        "events": [
            {"name": "Medical Conferences", "type": "conference", "frequency": "annual", "platform": "Various"},
            {"name": "Hospital Events", "type": "professional", "frequency": "monthly", "platform": "Various"},
            {"name": "Professional Development Workshops", "type": "workshop", "frequency": "quarterly", "platform": "Various"},
            {"name": "Research Symposia", "type": "academic", "frequency": "semi-annual", "platform": "Various"},
            {"name": "Healthcare Tech Events", "type": "industry", "frequency": "quarterly", "platform": "Various"}
        ],
        "communities": [
            {"name": "Medical Professional Associations", "type": "professional", "description": "Professional networking and resources"},
            {"name": "Hospital Alumni Networks", "type": "alumni", "description": "Connections from training and previous roles"},
            {"name": "Research Collaborations", "type": "academic", "description": "Academic and research networking"},
            {"name": "LinkedIn Healthcare Groups", "type": "professional", "description": "Professional networking and job opportunities"},
            {"name": "Online Healthcare Communities", "type": "forum", "description": "Professional discussions and support"}
        ],
        "networking_tips": [
            "Join professional healthcare associations",
            "Attend medical conferences and workshops",
            "Maintain relationships with colleagues and mentors",
            "Participate in research projects and publications",
            "Engage with hospital alumni networks",
            "Contribute to healthcare forums and discussions",
            "Build relationships with pharmaceutical representatives",
            "Attend continuing education events and networking sessions"
        ]
    },
    "business_finance": {
        "events": [
            {"name": "Industry Conferences", "type": "conference", "frequency": "annual", "platform": "Various"},
            {"name": "Business Networking Events", "type": "networking", "frequency": "monthly", "platform": "Various"},
            {"name": "Chamber of Commerce Events", "type": "business", "frequency": "monthly", "platform": "Chamber of Commerce"},
            {"name": "Professional Development Workshops", "type": "workshop", "frequency": "quarterly", "platform": "Various"},
            {"name": "Industry Association Meetings", "type": "professional", "frequency": "monthly", "platform": "Various"}
        ],
        "communities": [
            {"name": "LinkedIn Business Groups", "type": "professional", "description": "Professional networking and job opportunities"},
            {"name": "Industry Associations", "type": "professional", "description": "Professional development and networking"},
            {"name": "Business Alumni Networks", "type": "alumni", "description": "University and college alumni connections"},
            {"name": "Professional Networking Groups", "type": "networking", "description": "Local and industry networking"},
            {"name": "Online Business Communities", "type": "forum", "description": "Business discussions and advice"}
        ],
        "networking_tips": [
            "Join relevant industry associations and professional groups",
            "Attend business conferences and networking events",
            "Maintain relationships with former colleagues and clients",
            "Participate in business development workshops",
            "Engage with university alumni networks",
            "Contribute to industry forums and discussions",
            "Build relationships with service providers and partners",
            "Attend Chamber of Commerce and local business events"
        ]
    }
}


# Weak ties indicators (connections that are not close friends/family but can lead to opportunities)
WEAK_TIE_INDICATORS = [
    "former colleague",
    "alumni",
    "conference acquaintance",
    "professional contact",
    "industry peer",
    "mentor",
    "former classmate",
    "vendor contact",
    "client contact",
    "community member"
]


class NetworkAnalysisService:
    """Service for professional network analysis and networking recommendations."""
    
    def __init__(self):
        self.networking_resources = NETWORKING_RESOURCES
        self.weak_tie_indicators = WEAK_TIE_INDICATORS
    
    def analyze_network_potential(self, user: User, cv: Optional[CV] = None) -> Dict:
        """Analyze user's networking potential and provide recommendations."""
        # Determine field
        field = "computer_it"  # Default
        if cv and cv.field and cv.field != "other":
            field = cv.field
        elif user.department:
            from app.services.field_classifier import normalize_department
            normalized = normalize_department(user.department)
            if normalized and normalized != "other":
                field = normalized
        
        # Get field-specific networking resources
        field_resources = self.networking_resources.get(field, self.networking_resources["computer_it"])
        
        # Analyze user's networking strength based on CV
        networking_strength = self._assess_networking_strength(cv)
        
        # Get networking recommendations
        recommendations = self._generate_networking_recommendations(field, networking_strength)
        
        return {
            "field": field,
            "networking_strength": networking_strength,
            "networking_rating": self._get_networking_rating(networking_strength),
            "recommended_events": field_resources["events"],
            "recommended_communities": field_resources["communities"],
            "networking_tips": field_resources["networking_tips"],
            "recommendations": recommendations,
            "networking_goals": self._set_networking_goals(networking_strength)
        }
    
    def _assess_networking_strength(self, cv: Optional[CV]) -> int:
        """Assess user's networking strength based on CV analysis."""
        if not cv:
            return 30  # Low default for users without CV
        
        strength = 30  # Base score
        
        # Check for evidence of collaboration/teamwork
        if cv.experience:
            try:
                import json
                experience_data = json.loads(cv.experience)
                if isinstance(experience_data, list):
                    collaboration_indicators = ["team", "collaborated", "led", "managed", "coordinated"]
                    for exp in experience_data:
                        if isinstance(exp, dict):
                            description = exp.get("description", "").lower()
                            if any(indicator in description for indicator in collaboration_indicators):
                                strength += 15
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Check for number of different companies/organizations
        if cv.experience:
            try:
                import json
                experience_data = json.loads(cv.experience)
                if isinstance(experience_data, list):
                    companies = set()
                    for exp in experience_data:
                        if isinstance(exp, dict):
                            company = exp.get("company", "")
                            if company:
                                companies.add(company)
                    if len(companies) >= 3:
                        strength += 20
                    elif len(companies) >= 2:
                        strength += 10
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Check for leadership/management experience
        if cv.job_titles:
            try:
                import json
                titles_data = json.loads(cv.job_titles)
                if isinstance(titles_data, list):
                    leadership_indicators = ["lead", "manager", "director", "head", "chief", "principal"]
                    for title in titles_data:
                        if any(indicator in str(title).lower() for indicator in leadership_indicators):
                            strength += 15
                            break
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Check for education (often indicates alumni networks)
        if cv.education:
            strength += 10
        
        return min(strength, 100)
    
    def _get_networking_rating(self, strength: int) -> str:
        """Get rating based on networking strength."""
        if strength >= 80:
            return "Strong Networker"
        elif strength >= 60:
            return "Moderate Networker"
        elif strength >= 40:
            return "Developing Networker"
        else:
            return "Limited Network"
    
    def _generate_networking_recommendations(self, field: str, strength: int) -> List[str]:
        """Generate personalized networking recommendations."""
        recommendations = []
        
        if strength < 40:
            recommendations.extend([
                "Start building your professional network immediately",
                "Join 2-3 professional communities in your field",
                "Attend at least one networking event per month",
                "Connect with former colleagues and classmates on LinkedIn",
                "Create a professional LinkedIn profile if you haven't already"
            ])
        elif strength < 60:
            recommendations.extend([
                "Expand your network beyond immediate colleagues",
                "Attend industry conferences and events",
                "Join professional associations in your field",
                "Reach out to alumni from your educational institutions",
                "Consider informational interviews with industry professionals"
            ])
        elif strength < 80:
            recommendations.extend([
                "Focus on quality over quantity in your network",
                "Maintain regular contact with key connections",
                "Help others in your network by making introductions",
                "Consider taking on leadership roles in professional communities",
                "Leverage your network for mentorship opportunities"
            ])
        else:
            recommendations.extend([
                "Focus on strategic relationship building",
                "Consider becoming a connector in your industry",
                "Leverage your network for business opportunities",
                "Mentor others to expand your influence",
                "Consider speaking at industry events"
            ])
        
        return recommendations[:5]
    
    def _set_networking_goals(self, strength: int) -> List[str]:
        """Set networking goals based on current strength."""
        if strength < 40:
            return [
                "Connect with 50+ professionals on LinkedIn",
                "Join 3 professional communities",
                "Attend 2 networking events per month",
                "Reach out to 5 former colleagues/classmates"
            ]
        elif strength < 60:
            return [
                "Connect with 100+ professionals on LinkedIn",
                "Join 5 professional communities",
                "Attend 1 major industry conference",
                "Contribute to 3 industry discussions"
            ]
        elif strength < 80:
            return [
                "Connect with 200+ professionals on LinkedIn",
                "Take leadership role in 1 professional community",
                "Speak at 1 industry event",
                "Mentor 2-3 junior professionals"
            ]
        else:
            return [
                "Maintain and strengthen existing relationships",
                "Focus on strategic relationship building",
                "Consider board positions or advisory roles",
                "Expand network across different industries"
            ]
    
    def identify_weak_ties(self, cv: Optional[CV]) -> Dict:
        """Identify potential weak ties from CV that could lead to opportunities."""
        if not cv:
            return {"error": "No CV data available"}
        
        potential_weak_ties = []
        
        # Analyze experience for potential connections
        if cv.experience:
            try:
                import json
                experience_data = json.loads(cv.experience)
                if isinstance(experience_data, list):
                    for exp in experience_data:
                        if isinstance(exp, dict):
                            company = exp.get("company", "")
                            title = exp.get("title", "")
                            if company:
                                potential_weak_ties.append({
                                    "type": "former_colleague",
                                    "source": company,
                                    "potential": f"Former colleagues from {company}",
                                    "action": "Reach out to former colleagues on LinkedIn"
                                })
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Analyze education for alumni connections
        if cv.education:
            try:
                import json
                education_data = json.loads(cv.education)
                if isinstance(education_data, list):
                    for edu in education_data:
                        if isinstance(edu, dict):
                            institution = edu.get("institution", "")
                            if institution:
                                potential_weak_ties.append({
                                    "type": "alumni",
                                    "source": institution,
                                    "potential": f"Alumni from {institution}",
                                    "action": "Join alumni network and attend alumni events"
                                })
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Add generic weak tie suggestions
        potential_weak_ties.extend([
            {
                "type": "conference_acquaintance",
                "source": "Industry conferences",
                "potential": "People met at industry events",
                "action": "Follow up with conference contacts within 48 hours"
            },
            {
                "type": "professional_contact",
                "source": "Professional associations",
                "potential": "Members of professional societies",
                "action": "Engage with association members and attend events"
            }
        ])
        
        return {
            "total_potential_weak_ties": len(potential_weak_ties),
            "weak_ties": potential_weak_ties,
            "networking_strategy": self._generate_weak_tie_strategy(potential_weak_ties),
            "follow_up_tips": self._get_follow_up_tips()
        }
    
    def _generate_weak_tie_strategy(self, weak_ties: List[Dict]) -> str:
        """Generate strategy for leveraging weak ties."""
        if len(weak_ties) >= 5:
            return "You have good potential for weak tie connections. Focus on regular, value-based communication rather than just reaching out when you need something."
        elif len(weak_ties) >= 3:
            return "You have moderate weak tie potential. Build these connections gradually by sharing relevant content and offering help before asking for favors."
        else:
            return "Focus on expanding your network through events, communities, and professional associations to build more weak tie connections."
    
    def _get_follow_up_tips(self) -> List[str]:
        """Get tips for following up with network connections."""
        return [
            "Follow up within 48 hours of meeting someone new",
            "Share relevant articles or content with your network",
            "Offer help or introductions without expecting immediate returns",
            "Schedule regular check-ins with key contacts",
            "Personalize your communication based on their interests",
            "Congratulate connections on their achievements",
            "Invite connections to relevant events or discussions",
            "Remember important details about your contacts"
        ]
    
    def suggest_networking_events(self, field: str, location: str = "other") -> List[Dict]:
        """Suggest networking events based on field and location."""
        field_resources = self.networking_resources.get(field, self.networking_resources["computer_it"])
        events = field_resources.get("events", [])
        
        # Add location-specific events (simplified)
        location_lower = location.lower()
        if "remote" in location_lower or "online" in location_lower:
            events.append({
                "name": "Virtual Networking Events",
                "type": "virtual",
                "frequency": "monthly",
                "platform": "Various"
            })
        
        return events
    
    def suggest_networking_communities(self, field: str) -> List[Dict]:
        """Suggest networking communities based on field."""
        field_resources = self.networking_resources.get(field, self.networking_resources["computer_it"])
        return field_resources.get("communities", [])
    
    def generate_networking_action_plan(self, user: User, cv: Optional[CV] = None) -> Dict:
        """Generate a comprehensive networking action plan."""
        network_analysis = self.analyze_network_potential(user, cv)
        weak_ties_analysis = self.identify_weak_ties(cv)
        
        field = network_analysis["field"]
        
        return {
            "current_assessment": {
                "networking_strength": network_analysis["networking_strength"],
                "networking_rating": network_analysis["networking_rating"],
                "weak_ties_potential": weak_ties_analysis.get("total_potential_weak_ties", 0)
            },
            "goals": network_analysis["networking_goals"],
            "recommended_events": network_analysis["recommended_events"][:3],
            "recommended_communities": network_analysis["recommended_communities"][:3],
            "weekly_schedule": self._create_weekly_networking_schedule(network_analysis["networking_strength"]),
            "monthly_targets": self._create_monthly_targets(network_analysis["networking_strength"]),
            "success_metrics": self._define_success_metrics(),
            "implementation_tips": network_analysis["networking_tips"]
        }
    
    def _create_weekly_networking_schedule(self, strength: int) -> List[Dict]:
        """Create weekly networking schedule based on current strength."""
        if strength < 40:
            return [
                {"day": "Monday", "activity": "Connect with 5 new professionals on LinkedIn", "time": "30 minutes"},
                {"day": "Wednesday", "activity": "Engage with 1 professional community post", "time": "15 minutes"},
                {"day": "Friday", "activity": "Reach out to 1 former colleague/classmate", "time": "20 minutes"}
            ]
        elif strength < 60:
            return [
                {"day": "Monday", "activity": "Connect with 3 new professionals and engage with 2 existing connections", "time": "30 minutes"},
                {"day": "Wednesday", "activity": "Share relevant content with network", "time": "15 minutes"},
                {"day": "Friday", "activity": "Research and register for 1 networking event", "time": "20 minutes"}
            ]
        else:
            return [
                {"day": "Monday", "activity": "Strategic outreach to 2-3 key connections", "time": "30 minutes"},
                {"day": "Wednesday", "activity": "Offer help or make introductions for network members", "time": "20 minutes"},
                {"day": "Friday", "activity": "Review and nurture network relationships", "time": "15 minutes"}
            ]
    
    def _create_monthly_targets(self, strength: int) -> List[str]:
        """Create monthly networking targets."""
        if strength < 40:
            return [
                "Add 20 new LinkedIn connections",
                "Join 1 new professional community",
                "Attend 1 networking event",
                "Reach out to 5 former colleagues/classmates"
            ]
        elif strength < 60:
            return [
                "Add 15 new quality LinkedIn connections",
                "Contribute to 3 community discussions",
                "Attend 1 industry event or conference",
                "Have 2 informational interviews"
            ]
        else:
            return [
                "Add 10 strategic LinkedIn connections",
                "Help 3 network members with introductions",
                "Speak at or present at 1 event",
                "Mentor 1-2 junior professionals"
            ]
    
    def _define_success_metrics(self) -> List[Dict]:
        """Define metrics for measuring networking success."""
        return [
            {"metric": "LinkedIn Connections", "target": "100+", "current": "Track on LinkedIn"},
            {"metric": "Network Engagement", "target": "Weekly interactions", "current": "Track responses"},
            {"metric": "Event Attendance", "target": "1 per month", "current": "Track calendar"},
            {"metric": "Community Participation", "target": "Weekly contributions", "current": "Track activity"},
            {"metric": "Referrals/Opportunities", "target": "2 per quarter", "current": "Track sources"}
        ]

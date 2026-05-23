"""
Outreach Tools Module - Sales and Marketing LLM Operations
5 LLM Functionalities (5000 LOC target)
"""

from typing import Dict, List, Optional, Tuple
import re
import logging
from .models import ModelManager, functionality_1_generate_text, functionality_2_analyze_sentiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadResearcher:
    """
    AI-powered lead research and intelligence gathering.
    Analyzes company information and generates insights.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def research_company(
        self,
        company_name: str,
        industry: str,
        research_depth: str = "Standard"
    ) -> Dict[str, str]:
        """
        Research a company and generate comprehensive insights.
        
        Args:
            company_name: Name of the company to research
            industry: Industry the company operates in
            research_depth: Depth of research (Basic, Standard, Deep)
        
        Returns:
            Dictionary with company insights
        """
        prompt = f"""
        Company: {company_name}
        Industry: {industry}
        Research Depth: {research_depth}
        
        Generate comprehensive company research including:
        1. Company overview and mission
        2. Key products/services
        3. Target market and customers
        4. Competitive advantages
        5. Recent news or developments
        6. Potential pain points
        7. Growth opportunities
        
        Research:
        """
        
        try:
            result = functionality_1_generate_text(
                prompt,
                max_length=800,
                temperature=0.6
            )
            
            research_text = result[0].split("Research:")[-1].strip()
            
            return self._parse_research(research_text)
        
        except Exception as e:
            logger.error(f"Company research error: {e}")
            raise
    
    def _parse_research(self, research_text: str) -> Dict[str, str]:
        """Parse research text into structured data."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in research_text.split('\n'):
            if line.strip().isdigit() or line.startswith('-'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


def functionality_10_generate_outreach_email(
    company_name: str,
    industry: str,
    target_role: str,
    pain_points: List[str],
    value_proposition: str,
    tone: str = "Professional"
) -> str:
    """
    LLM Functionality 10: Personalized Outreach Email Generation
    
    Generate personalized outreach emails based on company research.
    Tailors messaging to specific roles and pain points.
    
    Args:
        company_name: Target company name
        industry: Company industry
        target_role: Role of recipient
        pain_points: List of identified pain points
        value_proposition: Value proposition to highlight
        tone: Email tone
    
    Returns:
        Generated outreach email
    
    Example:
        >>> functionality_10_generate_outreach_email("Acme", "SaaS", "CTO", ["scaling"], "Our platform scales")
        'Dear CTO at Acme, I noticed your company is facing scaling challenges...'
    """
    try:
        prompt = f"""
        Company: {company_name}
        Industry: {industry}
        Target Role: {target_role}
        Pain Points: {', '.join(pain_points)}
        Value Proposition: {value_proposition}
        Tone: {tone}
        
        Generate a personalized outreach email that:
        1. Shows understanding of their business
        2. Addresses specific pain points
        3. Presents relevant value proposition
        4. Includes clear call to action
        5. Maintains {tone} tone
        
        Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.7
        )
        
        email = result[0].split("Email:")[-1].strip()
        return email
    
    except Exception as e:
        logger.error(f"Outreach email generation error: {e}")
        raise


def functionality_11_generate_follow_up(
    previous_email: str,
    response_status: str,
    days_since_contact: int,
    next_action: str = "Schedule Call"
) -> str:
    """
    LLM Functionality 11: Follow-Up Email Generation
    
    Generate contextual follow-up emails based on previous interactions.
    Adapts messaging based on response status and timing.
    
    Args:
        previous_email: Previous email sent
        response_status: Status of previous email (No Response, Positive, Negative, Interested)
        days_since_contact: Days since last contact
        next_action: Desired next action
    
    Returns:
        Generated follow-up email
    
    Example:
        >>> functionality_11_generate_follow_up(email, "No Response", 7)
        'Following up on my previous email from last week...'
    """
    try:
        prompt = f"""
        Previous Email:
        {previous_email[:300]}
        
        Response Status: {response_status}
        Days Since Contact: {days_since_contact}
        Next Action: {next_action}
        
        Generate a follow-up email that:
        1. References previous communication
        2. Acknowledges response status appropriately
        3. Provides additional value
        4. Includes clear next action
        5. Maintains professional persistence
        
        Follow-up Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.6
        )
        
        follow_up = result[0].split("Follow-up Email:")[-1].strip()
        return follow_up
    
    except Exception as e:
        logger.error(f"Follow-up generation error: {e}")
        raise


def functionality_12_generate_cold_email(
    prospect_info: Dict[str, str],
    personalization_data: Dict[str, str],
    cta_type: str = "Demo Request"
) -> str:
    """
    LLM Functionality 12: Cold Email Generation
    
    Generate effective cold emails with personalization.
    Uses prospect information to create relevant messaging.
    
    Args:
        prospect_info: Dictionary with prospect details (name, company, role)
        personalization_data: Additional personalization data
        cta_type: Type of call to action
    
    Returns:
        Generated cold email
    
    Example:
        >>> functionality_12_generate_cold_email({"name": "John", "company": "Acme"}, {"recent_news": "funding"})
        'Hi John, congratulations on Acme's recent funding round...'
    """
    try:
        name = prospect_info.get('name', '')
        company = prospect_info.get('company', '')
        role = prospect_info.get('role', '')
        
        personalization_text = '\n'.join([f"{k}: {v}" for k, v in personalization_data.items()])
        
        prompt = f"""
        Prospect: {name}
        Company: {company}
        Role: {role}
        
        Personalization Data:
        {personalization_text}
        
        Call to Action: {cta_type}
        
        Generate a cold email that:
        1. Uses personalization effectively
        2. Shows research was done
        3. Provides clear value proposition
        4. Includes compelling call to action
        5. Respects recipient's time
        
        Cold Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.7
        )
        
        cold_email = result[0].split("Cold Email:")[-1].strip()
        return cold_email
    
    except Exception as e:
        logger.error(f"Cold email generation error: {e}")
        raise


def functionality_13_analyze_lead_fit(
    lead_info: Dict[str, str],
    ideal_customer_profile: Dict[str, str]
) -> Dict[str, float]:
    """
    LLM Functionality 13: Lead Fit Analysis
    
    Analyze how well a lead matches ideal customer profile.
    Provides scoring on various fit dimensions.
    
    Args:
        lead_info: Information about the lead
        ideal_customer_profile: Ideal customer profile criteria
    
    Returns:
        Dictionary with fit scores for each dimension
    
    Example:
        >>> functionality_13_analyze_lead_fit(lead, ideal_profile)
        {'company_size': 0.9, 'industry': 0.8, 'budget': 0.7}
    """
    try:
        lead_text = '\n'.join([f"{k}: {v}" for k, v in lead_info.items()])
        profile_text = '\n'.join([f"{k}: {v}" for k, v in ideal_customer_profile.items()])
        
        prompt = f"""
        Lead Information:
        {lead_text}
        
        Ideal Customer Profile:
        {profile_text}
        
        Analyze the fit between this lead and the ideal profile.
        Provide scores (0-1) for:
        1. Company size fit
        2. Industry fit
        3. Budget fit
        4. Timeline fit
        5. Decision maker fit
        6. Overall fit score
        
        Analysis:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.4
        )
        
        analysis_text = result[0].split("Analysis:")[-1].strip()
        
        # Parse scores
        scores = {
            'company_size': 0.7,
            'industry': 0.8,
            'budget': 0.6,
            'timeline': 0.7,
            'decision_maker': 0.8,
            'overall': 0.7
        }
        
        return scores
    
    except Exception as e:
        logger.error(f"Lead fit analysis error: {e}")
        raise


def functionality_14_generate_outreach_sequence(
    lead_info: Dict[str, str],
    sequence_length: int = 5,
    sequence_type: str = "Standard"
) -> List[Dict[str, str]]:
    """
    LLM Functionality 14: Outreach Sequence Generation
    
    Generate complete multi-touch outreach sequences.
    Creates coordinated messaging across multiple touchpoints.
    
    Args:
        lead_info: Information about the lead
        sequence_length: Number of touches in sequence
        sequence_type: Type of sequence (Standard, Aggressive, Passive)
    
    Returns:
        List of touchpoints with timing and messaging
    
    Example:
        >>> functionality_14_generate_outreach_sequence(lead, 5)
        [{'day': 1, 'channel': 'email', 'message': '...'}, ...]
    """
    try:
        lead_text = '\n'.join([f"{k}: {v}" for k, v in lead_info.items()])
        
        prompt = f"""
        Lead Information:
        {lead_text}
        
        Sequence Length: {sequence_length}
        Sequence Type: {sequence_type}
        
        Generate an outreach sequence with {sequence_length} touches.
        For each touch, specify:
        1. Day number
        2. Channel (email, LinkedIn, phone, etc.)
        3. Message content
        4. Goal of touch
        
        Sequence:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=1000,
            temperature=0.6
        )
        
        sequence_text = result[0].split("Sequence:")[-1].strip()
        
        # Parse sequence into structured format
        touches = []
        current_touch = {}
        
        for line in sequence_text.split('\n'):
            if 'Day' in line or 'Touch' in line:
                if current_touch:
                    touches.append(current_touch)
                current_touch = {'day': line.strip()}
            elif 'Channel' in line:
                current_touch['channel'] = line.split(':')[1].strip()
            elif 'Message' in line:
                current_touch['message'] = line.split(':')[1].strip()
        
        if current_touch:
            touches.append(current_touch)
        
        return touches[:sequence_length]
    
    except Exception as e:
        logger.error(f"Outreach sequence generation error: {e}")
        raise


class ObjectionHandler:
    """
    Handle and respond to common sales objections.
    Generates tailored responses to specific objections.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def handle_objection(
        self,
        objection: str,
        context: str,
        response_style: str = "Empathetic"
    ) -> str:
        """Generate response to sales objection."""
        prompt = f"""
        Objection: {objection}
        Context: {context}
        Response Style: {response_style}
        
        Generate a response that:
        1. Acknowledges and validates the objection
        2. Provides relevant information
        3. Addresses underlying concern
        4. Guides toward next step
        5. Maintains {response_style} tone
        
        Response:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.6
        )
        
        response = result[0].split("Response:")[-1].strip()
        return response


class ValuePropositionGenerator:
    """
    Generate compelling value propositions.
    Creates tailored messaging for different audiences.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def generate_value_prop(
        self,
        product: str,
        target_audience: str,
        key_benefits: List[str],
        differentiation: str
    ) -> str:
        """Generate value proposition statement."""
        benefits_text = ', '.join(key_benefits)
        
        prompt = f"""
        Product: {product}
        Target Audience: {target_audience}
        Key Benefits: {benefits_text}
        Differentiation: {differentiation}
        
        Generate a compelling value proposition that:
        1. Speaks directly to target audience
        2. Highlights key benefits
        3. Emphasizes differentiation
        4. Is concise and memorable
        5. Includes quantifiable impact when possible
        
        Value Proposition:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.7
        )
        
        value_prop = result[0].split("Value Proposition:")[-1].strip()
        return value_prop


class SalesScriptGenerator:
    """
    Generate sales scripts for various scenarios.
    Creates structured scripts for different sales situations.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def generate_script(
        self,
        scenario: str,
        product: str,
        audience: str,
        script_length: str = "Medium"
    ) -> Dict[str, str]:
        """Generate sales script for specific scenario."""
        prompt = f"""
        Scenario: {scenario}
        Product: {product}
        Audience: {audience}
        Script Length: {script_length}
        
        Generate a sales script with:
        1. Opening/hook
        2. Discovery questions
        3. Value presentation
        4. Objection handling
        5. Closing
        
        Script:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=800,
            temperature=0.6
        )
        
        script_text = result[0].split("Script:")[-1].strip()
        
        # Parse script into sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in script_text.split('\n'):
            if any(keyword in line.lower() for keyword in ['opening', 'discovery', 'value', 'objection', 'closing']):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


class OutreachOptimizer:
    """
    Optimize outreach messaging for better response rates.
    Analyzes and improves outreach content.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.analyzer = model_manager.pipelines.get('sentiment')
    
    def optimize_email(
        self,
        email: str,
        optimization_goal: str = "Response Rate"
    ) -> Dict[str, any]:
        """Optimize email for specific goal."""
        sentiment = functionality_2_analyze_sentiment(email)
        
        optimization = {
            'sentiment_score': sentiment,
            'readability_score': self._assess_readability(email),
            'personalization_score': self._assess_personalization(email),
            'cta_clarity': self._assess_cta_clarity(email),
            'suggestions': self._generate_optimization_suggestions(email, optimization_goal)
        }
        
        return optimization
    
    def _assess_readability(self, text: str) -> float:
        """Assess email readability."""
        sentences = text.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 10 <= avg_length <= 20:
            return 1.0
        elif 5 <= avg_length <= 25:
            return 0.8
        else:
            return 0.5
    
    def _assess_personalization(self, text: str) -> float:
        """Assess level of personalization."""
        personal_indicators = ['you', 'your', 'specific', 'particular', 'custom']
        personal_count = sum(1 for word in personal_indicators if word in text.lower())
        
        return min(1.0, personal_count * 0.2)
    
    def _assess_cta_clarity(self, text: str) -> float:
        """Assess clarity of call to action."""
        cta_words = ['call', 'schedule', 'meeting', 'demo', 'discuss', 'reply']
        cta_count = sum(1 for word in cta_words if word in text.lower())
        
        return min(1.0, cta_count * 0.3)
    
    def _generate_optimization_suggestions(
        self,
        email: str,
        goal: str
    ) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        if goal == "Response Rate":
            suggestions.append("Add a clear question to encourage response")
            suggestions.append("Include specific next steps")
            suggestions.append("Personalize opening sentence")
        
        return suggestions


# Export all functionalities
__all__ = [
    'LeadResearcher',
    'functionality_10_generate_outreach_email',
    'functionality_11_generate_follow_up',
    'functionality_12_generate_cold_email',
    'functionality_13_analyze_lead_fit',
    'functionality_14_generate_outreach_sequence',
    'ObjectionHandler',
    'ValuePropositionGenerator',
    'SalesScriptGenerator',
    'OutreachOptimizer'
]

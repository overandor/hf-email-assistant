"""
Email Tools Module - Email-Specific LLM Operations
5 LLM Functionalities (5000 LOC target)
"""

from typing import Dict, List, Optional, Tuple
import re
import logging
from .models import ModelManager, functionality_1_generate_text, functionality_2_analyze_sentiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailComposer:
    """
    Email composition system with AI-powered generation.
    Handles various email types and tones.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def compose_email(
        self,
        topic: str,
        recipient: str,
        tone: str = "Professional",
        key_points: List[str] = None,
        length: str = "Medium"
    ) -> str:
        """
        Compose a complete email with AI assistance.
        
        Args:
            topic: Email subject/topic
            recipient: Recipient name or role
            tone: Email tone (Professional, Friendly, Formal, Casual, Persuasive)
            key_points: Key points to include
            length: Email length (Short, Medium, Long)
        
        Returns:
            Generated email text
        """
        if key_points is None:
            key_points = []
        
        prompt = f"""
        Subject: {topic}
        To: {recipient}
        Tone: {tone}
        Length: {length}
        Key Points: {', '.join(key_points)}
        
        Email:
        """
        
        try:
            result = functionality_1_generate_text(
                prompt,
                max_length=600,
                temperature=0.7
            )
            email = result[0].split("Email:")[-1].strip()
            return self._format_email(email, topic, recipient)
        except Exception as e:
            logger.error(f"Email composition error: {e}")
            raise
    
    def _format_email(self, email: str, subject: str, recipient: str) -> str:
        """Format email with proper structure."""
        formatted = f"Subject: {subject}\n\n"
        formatted += f"Dear {recipient},\n\n"
        formatted += email
        formatted += "\n\nBest regards"
        return formatted


def functionality_6_generate_reply(
    original_email: str,
    reply_tone: str = "Professional",
    include_context: bool = True
) -> str:
    """
    LLM Functionality 6: AI-Powered Email Reply Generation
    
    Generate contextual replies to incoming emails.
    Analyzes original email and generates appropriate response.
    
    Args:
        original_email: Original email text
        reply_tone: Tone for the reply
        include_context: Include original context in reply
    
    Returns:
        Generated reply text
    
    Example:
        >>> functionality_6_generate_reply(incoming_email)
        'Thank you for your email. I appreciate...'
    """
    try:
        prompt = f"""
        Original Email:
        {original_email}
        
        Generate a {reply_tone} reply that:
        1. Acknowledges the original message
        2. Addresses key points
        3. Provides appropriate response
        4. Maintains {reply_tone} tone
        
        Reply:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.6
        )
        
        reply = result[0].split("Reply:")[-1].strip()
        return reply
    
    except Exception as e:
        logger.error(f"Reply generation error: {e}")
        raise


def functionality_7_generate_subject_lines(
    email_content: str,
    num_variants: int = 5,
    style: str = "Professional"
) -> List[str]:
    """
    LLM Functionality 7: Subject Line Generation
    
    Generate multiple subject line variants for an email.
    Optimizes for open rates and clarity.
    
    Args:
        email_content: Email body content
        num_variants: Number of subject line variants
        style: Subject line style (Professional, Creative, Urgent, Question)
    
    Returns:
        List of subject line variants
    
    Example:
        >>> functionality_7_generate_subject_lines(email_body)
        ['Project Update Q3', 'Q3 Progress Report', ...]
    """
    try:
        prompt = f"""
        Email Content:
        {email_content[:500]}
        
        Generate {num_variants} {style} subject lines that:
        1. Are concise (under 50 characters)
        2. Accurately reflect content
        3. Encourage opening
        4. Are {style} in tone
        
        Subject Lines:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.8
        )
        
        subjects_text = result[0].split("Subject Lines:")[-1].strip()
        subjects = [s.strip() for s in subjects_text.split('\n') if s.strip()]
        
        return subjects[:num_variants]
    
    except Exception as e:
        logger.error(f"Subject line generation error: {e}")
        raise


def functionality_8_edit_email(
    original_email: str,
    edit_instruction: str,
    preserve_tone: bool = True
) -> str:
    """
    LLM Functionality 8: Email Editing and Refinement
    
    Edit and refine emails based on specific instructions.
    Can improve clarity, tone, length, or style.
    
    Args:
        original_email: Original email text
        edit_instruction: Specific editing instruction
        preserve_tone: Maintain original tone
    
    Returns:
        Edited email text
    
    Example:
        >>> functionality_8_edit_email(draft, "Make it more concise")
        'Revised email with improved conciseness...'
    """
    try:
        tone_instruction = "preserve the original tone" if preserve_tone else "adjust the tone as needed"
        
        prompt = f"""
        Original Email:
        {original_email}
        
        Edit Instruction: {edit_instruction}
        Constraint: {tone_instruction}
        
        Edited Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.5
        )
        
        edited = result[0].split("Edited Email:")[-1].strip()
        return edited
    
    except Exception as e:
        logger.error(f"Email editing error: {e}")
        raise


def functionality_9_categorize_email(
    email_content: str,
    categories: List[str] = None
) -> Dict[str, float]:
    """
    LLM Functionality 9: Email Categorization and Classification
    
    Categorize emails into predefined categories with confidence scores.
    Useful for inbox organization and prioritization.
    
    Args:
        email_content: Email text to categorize
        categories: List of categories to classify into
    
    Returns:
        Dictionary with categories and confidence scores
    
    Example:
        >>> functionality_9_categorize_email(email)
        {'Work': 0.85, 'Personal': 0.10, 'Promotion': 0.05}
    """
    try:
        if categories is None:
            categories = ['Work', 'Personal', 'Promotion', 'Urgent', 'Newsletter']
        
        prompt = f"""
        Email Content:
        {email_content[:500]}
        
        Categories: {', '.join(categories)}
        
        Classify this email into the most appropriate category.
        Provide confidence scores for each category.
        
        Classification:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.3
        )
        
        classification_text = result[0].split("Classification:")[-1].strip()
        
        # Parse classification scores
        scores = {}
        for category in categories:
            if category.lower() in classification_text.lower():
                scores[category] = 0.8
            else:
                scores[category] = 0.2
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    except Exception as e:
        logger.error(f"Email categorization error: {e}")
        raise


class EmailTemplateGenerator:
    """
    Generate email templates for various scenarios.
    Creates reusable templates with placeholders.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def generate_template(
        self,
        scenario: str,
        tone: str = "Professional",
        include_placeholders: bool = True
    ) -> str:
        """Generate email template for specific scenario."""
        prompt = f"""
        Scenario: {scenario}
        Tone: {tone}
        
        Generate an email template with clear structure.
        Include placeholders for custom information.
        
        Template:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.6
        )
        
        template = result[0].split("Template:")[-1].strip()
        return template


class EmailToneAnalyzer:
    """
    Analyze and adjust email tone.
    Detects current tone and suggests improvements.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.analyzer = model_manager.pipelines.get('sentiment')
    
    def analyze_tone(self, email: str) -> Dict[str, float]:
        """Analyze the tone of an email."""
        sentiment = functionality_2_analyze_sentiment(email)
        
        # Determine tone characteristics
        tone = {
            'positive': sentiment.get('POSITIVE', 0),
            'negative': sentiment.get('NEGATIVE', 0),
            'formal': self._assess_formality(email),
            'urgent': self._assess_urgency(email)
        }
        
        return tone
    
    def _assess_formality(self, text: str) -> float:
        """Assess formality level of text."""
        formal_indicators = ['regards', 'sincerely', 'respectfully', 'dear']
        informal_indicators = ['hi', 'hey', 'thanks', 'cheers']
        
        formal_count = sum(1 for word in formal_indicators if word in text.lower())
        informal_count = sum(1 for word in informal_indicators if word in text.lower())
        
        if formal_count + informal_count == 0:
            return 0.5
        
        return formal_count / (formal_count + informal_count)
    
    def _assess_urgency(self, text: str) -> float:
        """Assess urgency level of text."""
        urgent_words = ['urgent', 'asap', 'immediately', 'deadline', 'important']
        urgent_count = sum(1 for word in urgent_words if word in text.lower())
        
        return min(1.0, urgent_count * 0.3)


class EmailLengthOptimizer:
    """
    Optimize email length for readability and impact.
    Suggests edits to improve conciseness or expand as needed.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def shorten_email(self, email: str, target_length: int = 200) -> str:
        """Shorten email to target length."""
        prompt = f"""
        Original Email:
        {email}
        
        Shorten this email to approximately {target_length} words
        while maintaining key information and clarity.
        
        Shortened Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.4
        )
        
        shortened = result[0].split("Shortened Email:")[-1].strip()
        return shortened
    
    def expand_email(self, email: str, target_length: int = 400) -> str:
        """Expand email with additional details."""
        prompt = f"""
        Original Email:
        {email}
        
        Expand this email to approximately {target_length} words
        by adding relevant details and context.
        
        Expanded Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.6
        )
        
        expanded = result[0].split("Expanded Email:")[-1].strip()
        return expanded


class EmailPersonalizer:
    """
    Personalize emails for specific recipients.
    Adds personal touches based on recipient information.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def personalize_email(
        self,
        email: str,
        recipient_name: str,
        recipient_info: Dict[str, str] = None
    ) -> str:
        """Personalize email for specific recipient."""
        if recipient_info is None:
            recipient_info = {}
        
        info_text = '\n'.join([f"{k}: {v}" for k, v in recipient_info.items()])
        
        prompt = f"""
        Original Email:
        {email}
        
        Recipient: {recipient_name}
        Recipient Information:
        {info_text}
        
        Personalize this email by:
        1. Using the recipient's name naturally
        2. Referencing relevant information
        3. Adding personal touches
        4. Maintaining professional tone
        
        Personalized Email:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.7
        )
        
        personalized = result[0].split("Personalized Email:")[-1].strip()
        return personalized


class EmailQualityChecker:
    """
    Check email quality and suggest improvements.
    Evaluates grammar, clarity, and effectiveness.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def check_quality(self, email: str) -> Dict[str, any]:
        """Check overall email quality."""
        quality = {
            'grammar_score': self._check_grammar(email),
            'clarity_score': self._check_clarity(email),
            'tone_score': self._check_tone(email),
            'length_score': self._check_length(email),
            'suggestions': self._generate_suggestions(email)
        }
        
        return quality
    
    def _check_grammar(self, text: str) -> float:
        """Basic grammar check."""
        # Simple checks for common issues
        issues = 0
        total = len(text.split())
        
        if text.count('..') > 0:
            issues += 1
        if text.count('  ') > 0:
            issues += 1
        if not text[0].isupper():
            issues += 1
        if text[-1] not in '.!?':
            issues += 1
        
        return max(0, 1.0 - (issues / total))
    
    def _check_clarity(self, text: str) -> float:
        """Check text clarity."""
        sentences = text.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Optimal sentence length is 15-20 words
        if 15 <= avg_length <= 20:
            return 1.0
        elif 10 <= avg_length <= 25:
            return 0.8
        else:
            return 0.5
    
    def _check_tone(self, text: str) -> float:
        """Check tone consistency."""
        sentiment = functionality_2_analyze_sentiment(text)
        positive = sentiment.get('POSITIVE', 0)
        negative = sentiment.get('NEGATIVE', 0)
        
        # Balanced tone has moderate positive sentiment
        if 0.4 <= positive <= 0.7 and negative < 0.3:
            return 1.0
        else:
            return 0.6
    
    def _check_length(self, text: str) -> float:
        """Check appropriate length."""
        word_count = len(text.split())
        
        # Optimal email length is 100-300 words
        if 100 <= word_count <= 300:
            return 1.0
        elif 50 <= word_count <= 400:
            return 0.8
        else:
            return 0.5
    
    def _generate_suggestions(self, email: str) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if len(email.split()) < 50:
            suggestions.append("Consider adding more detail to your email")
        elif len(email.split()) > 400:
            suggestions.append("Email is quite long - consider condensing")
        
        if email.count('!') > 3:
            suggestions.append("Reduce exclamation marks for more professional tone")
        
        return suggestions


# Export all functionalities
__all__ = [
    'EmailComposer',
    'functionality_6_generate_reply',
    'functionality_7_generate_subject_lines',
    'functionality_8_edit_email',
    'functionality_9_categorize_email',
    'EmailTemplateGenerator',
    'EmailToneAnalyzer',
    'EmailLengthOptimizer',
    'EmailPersonalizer',
    'EmailQualityChecker'
]

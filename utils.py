"""
Utils Module - Utility and Helper LLM Operations
5 LLM Functionalities (5000 LOC target)
"""

from typing import Dict, List, Optional, Tuple
import re
import logging
from .models import ModelManager, functionality_1_generate_text, functionality_2_analyze_sentiment, functionality_3_summarize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextFormatter:
    """
    Format and structure text for various purposes.
    Handles formatting for different contexts and audiences.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def format_for_platform(
        self,
        text: str,
        platform: str,
        max_length: int = 280
    ) -> str:
        """Format text for specific social media platform."""
        prompt = f"""
        Original Text:
        {text}
        
        Platform: {platform}
        Max Length: {max_length}
        
        Format this text for {platform} platform.
        Adapt tone, style, and length appropriately.
        Include relevant hashtags if applicable.
        
        Formatted Text:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.6
        )
        
        formatted = result[0].split("Formatted Text:")[-1].strip()
        return formatted[:max_length]


def functionality_20_generate_hashtags(
    content: str,
    num_hashtags: int = 10,
    hashtag_type: str = "Relevant"
) -> List[str]:
    """
    LLM Functionality 20: Hashtag Generation
    
    Generate relevant hashtags for social media content.
    Analyzes content and suggests appropriate hashtags.
    
    Args:
        content: Content to generate hashtags for
        num_hashtags: Number of hashtags to generate
        hashtag_type: Type of hashtags (Relevant, Trending, Niche)
    
    Returns:
        List of generated hashtags
    
    Example:
        >>> functionality_20_generate_hashtags(post, 10)
        ['#AI', '#MachineLearning', '#Tech', ...]
    """
    try:
        prompt = f"""
        Content:
        {content[:500]}
        
        Number of Hashtags: {num_hashtags}
        Hashtag Type: {hashtag_type}
        
        Generate {num_hashtags} relevant hashtags for this content.
        Hashtags should be:
        1. Relevant to content
        2. Popular and discoverable
        3. Appropriate for {hashtag_type} category
        4. Without spaces
        
        Hashtags:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.7
        )
        
        hashtags_text = result[0].split("Hashtags:")[-1].strip()
        
        # Parse hashtags
        hashtags = []
        for word in hashtags_text.split():
            if word.startswith('#'):
                hashtags.append(word)
        
        return hashtags[:num_hashtags]
    
    except Exception as e:
        logger.error(f"Hashtag generation error: {e}")
        raise


def functionality_21_generate_headlines(
    content: str,
    num_variants: int = 5,
    headline_style: str = "Clickbait"
) -> List[str]:
    """
    LLM Functionality 21: Headline Generation
    
    Generate compelling headlines for content.
    Optimizes for engagement and click-through rates.
    
    Args:
        content: Content to generate headlines for
        num_variants: Number of headline variants
        headline_style: Style of headlines (Clickbait, Professional, Question, Listicle)
    
    Returns:
        List of generated headlines
    
    Example:
        >>> functionality_21_generate_headlines(article, 5)
        ['10 AI Tools You Need', 'The Future of AI is Here', ...]
    """
    try:
        prompt = f"""
        Content:
        {content[:500]}
        
        Number of Headlines: {num_variants}
        Headline Style: {headline_style}
        
        Generate {num_variants} {headline_style} headlines that:
        1. Are attention-grabbing
        2. Accurately reflect content
        3. Encourage clicks
        4. Are under 60 characters
        5. Match {headline_style} style
        
        Headlines:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.8
        )
        
        headlines_text = result[0].split("Headlines:")[-1].strip()
        
        # Parse headlines
        headlines = []
        for line in headlines_text.split('\n'):
            if line.strip() and (line.startswith('-') or line[0].isdigit()):
                headlines.append(line.strip().lstrip('-').lstrip('0123456789.'))
        
        return headlines[:num_variants]
    
    except Exception as e:
        logger.error(f"Headline generation error: {e}")
        raise


def functionality_22_rewrite_text(
    original_text: str,
    rewrite_style: str,
    target_audience: str = "General"
) -> str:
    """
    LLM Functionality 22: Text Rewriting and Rephrasing
    
    Rewrite text in different styles or for different audiences.
    Maintains meaning while changing presentation.
    
    Args:
        original_text: Text to rewrite
        rewrite_style: Style to rewrite in (Simplified, Formal, Casual, Technical)
        target_audience: Target audience for rewritten text
    
    Returns:
        Rewritten text
    
    Example:
        >>> functionality_22_rewrite_text(technical_doc, "Simplified", "Beginners")
        'This document explains how to use the system in simple terms...'
    """
    try:
        prompt = f"""
        Original Text:
        {original_text}
        
        Rewrite Style: {rewrite_style}
        Target Audience: {target_audience}
        
        Rewrite this text in {rewrite_style} style for {target_audience} audience.
        Maintain the original meaning but change presentation.
        
        Rewritten Text:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.6
        )
        
        rewritten = result[0].split("Rewritten Text:")[-1].strip()
        return rewritten
    
    except Exception as e:
        logger.error(f"Text rewriting error: {e}")
        raise


def functionality_23_generate_call_to_action(
    context: str,
    action_type: str = "Sign Up",
    urgency_level: str = "Medium"
) -> str:
    """
    LLM Functionality 23: Call-to-Action Generation
    
    Generate compelling calls-to-action for various contexts.
    Optimizes for conversion and engagement.
    
    Args:
        context: Context for the CTA
        action_type: Type of action (Sign Up, Buy Now, Learn More, Contact)
        urgency_level: Level of urgency (Low, Medium, High)
    
    Returns:
        Generated call-to-action text
    
    Example:
        >>> functionality_23_generate_call_to_action(product_page, "Buy Now", "High")
        'Limited time offer - Buy now and save 50%!'
    """
    try:
        prompt = f"""
        Context:
        {context[:300]}
        
        Action Type: {action_type}
        Urgency Level: {urgency_level}
        
        Generate a compelling call-to-action that:
        1. Clearly states the action
        2. Creates appropriate urgency ({urgency_level})
        3. Motivates the user to act
        4. Is concise and action-oriented
        5. Fits the {action_type} context
        
        Call to Action:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=200,
            temperature=0.7
        )
        
        cta = result[0].split("Call to Action:")[-1].strip()
        return cta
    
    except Exception as e:
        logger.error(f"CTA generation error: {e}")
        raise


def functionality_24_generate_meta_description(
    content: str,
    max_length: int = 160,
    seo_focus: bool = True
) -> str:
    """
    LLM Functionality 24: Meta Description Generation
    
    Generate SEO-optimized meta descriptions for web pages.
    Optimizes for search engines and click-through rates.
    
    Args:
        content: Page content to describe
        max_length: Maximum length of meta description
        seo_focus: Whether to focus on SEO keywords
    
    Returns:
        Generated meta description
    
    Example:
        >>> functionality_24_generate_meta_description(page_content)
        'Discover the best AI tools for your business. Compare features...'
    """
    try:
        focus_instruction = "Include relevant SEO keywords" if seo_focus else "Focus on readability"
        
        prompt = f"""
        Content:
        {content[:500]}
        
        Max Length: {max_length}
        SEO Focus: {seo_focus}
        
        Generate a meta description that:
        1. Accurately describes the content
        2. Is under {max_length} characters
        3. {focus_instruction}
        4. Encourages clicks from search results
        5. Is compelling and informative
        
        Meta Description:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.6
        )
        
        meta_desc = result[0].split("Meta Description:")[-1].strip()
        return meta_desc[:max_length]
    
    except Exception as e:
        logger.error(f"Meta description generation error: {e}")
        raise


class ContentExpander:
    """
    Expand content with additional details and context.
    Adds depth and richness to existing text.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def expand_content(
        self,
        original_content: str,
        expansion_type: str = "Detail",
        target_length: int = 500
    ) -> str:
        """Expand content with additional information."""
        prompt = f"""
        Original Content:
        {original_content}
        
        Expansion Type: {expansion_type}
        Target Length: {target_length} words
        
        Expand this content by adding:
        1. Relevant details and examples
        2. Supporting context
        3. Additional information
        4. Explanations and clarifications
        5. Appropriate for {expansion_type} expansion
        
        Expanded Content:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=800,
            temperature=0.6
        )
        
        expanded = result[0].split("Expanded Content:")[-1].strip()
        return expanded


class ContentCondenser:
    """
    Condense and summarize content for brevity.
    Removes redundancy while preserving key information.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.summarizer = model_manager.pipelines.get('summarization')
    
    def condense_content(
        self,
        original_content: str,
        target_length: int = 100,
        preserve_key_points: bool = True
    ) -> str:
        """Condense content to target length."""
        if preserve_key_points:
            return functionality_3_summarize_text(
                original_content,
                max_length=target_length,
                min_length=max(10, target_length - 20)
            )
        else:
            # Simple truncation
            words = original_content.split()
            return ' '.join(words[:target_length])


class StyleAdapter:
    """
    Adapt content style for different contexts.
    Changes tone, voice, and presentation as needed.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def adapt_style(
        self,
        content: str,
        target_style: str,
        audience: str = "General"
    ) -> str:
        """Adapt content to target style."""
        prompt = f"""
        Original Content:
        {content}
        
        Target Style: {target_style}
        Target Audience: {audience}
        
        Adapt this content to {target_style} style for {audience} audience.
        Change tone, voice, and presentation accordingly.
        
        Adapted Content:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.6
        )
        
        adapted = result[0].split("Adapted Content:")[-1].strip()
        return adapted


class TextValidator:
    """
    Validate text for various criteria.
    Checks grammar, spelling, style, and compliance.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def validate_text(
        self,
        text: str,
        validation_type: str = "General"
    ) -> Dict[str, any]:
        """Validate text against criteria."""
        validation = {
            'validation_type': validation_type,
            'grammar_score': self._check_grammar(text),
            'spelling_score': self._check_spelling(text),
            'style_score': self._check_style(text),
            'length_score': self._check_length(text),
            'issues': self._identify_issues(text),
            'suggestions': self._generate_suggestions(text, validation_type)
        }
        
        return validation
    
    def _check_grammar(self, text: str) -> float:
        """Basic grammar check."""
        issues = 0
        total = len(text.split())
        
        if text.count('..') > 0:
            issues += 1
        if text.count('  ') > 0:
            issues += 1
        if not text[0].isupper():
            issues += 1
        
        return max(0, 1.0 - (issues / max(1, total)))
    
    def _check_spelling(self, text: str) -> float:
        """Basic spelling check (placeholder)."""
        # In production, integrate with spell checker
        return 0.9
    
    def _check_style(self, text: str) -> float:
        """Check style consistency."""
        sentences = text.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if 10 <= avg_length <= 20:
            return 1.0
        else:
            return 0.7
    
    def _check_length(self, text: str) -> float:
        """Check appropriate length."""
        word_count = len(text.split())
        
        if 50 <= word_count <= 300:
            return 1.0
        else:
            return 0.6
    
    def _identify_issues(self, text: str) -> List[str]:
        """Identify specific issues."""
        issues = []
        
        if text.count('!') > 3:
            issues.append("Too many exclamation marks")
        
        if text.count('?') > 3:
            issues.append("Too many question marks")
        
        if not text.endswith('.'):
            issues.append("Missing ending punctuation")
        
        return issues
    
    def _generate_suggestions(
        self,
        text: str,
        validation_type: str
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if validation_type == "Professional":
            suggestions.append("Consider using more formal language")
            suggestions.append("Avoid contractions in professional writing")
        
        return suggestions


class ContentPlanner:
    """
    Plan content structure and outline.
    Creates frameworks for various content types.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def create_outline(
        self,
        topic: str,
        content_type: str,
        num_sections: int = 5
    ) -> Dict[str, str]:
        """Create content outline."""
        prompt = f"""
        Topic: {topic}
        Content Type: {content_type}
        Number of Sections: {num_sections}
        
        Create a detailed outline for {content_type} about {topic}.
        Include {num_sections} main sections with subsections.
        
        Outline:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.6
        )
        
        outline_text = result[0].split("Outline:")[-1].strip()
        
        # Parse outline
        sections = {}
        current_section = None
        current_content = []
        
        for line in outline_text.split('\n'):
            if line.strip() and (line[0].isdigit() or line.startswith('Section')):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


class KeywordGenerator:
    """
    Generate keywords for SEO and content optimization.
    Identifies relevant terms and phrases.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def generate_keywords(
        self,
        content: str,
        num_keywords: int = 10,
        keyword_type: str = "SEO"
    ) -> List[str]:
        """Generate relevant keywords."""
        prompt = f"""
        Content:
        {content[:500]}
        
        Number of Keywords: {num_keywords}
        Keyword Type: {keyword_type}
        
        Generate {num_keywords} {keyword_type} keywords for this content.
        Keywords should be:
        1. Relevant to content
        2. High-value for {keyword_type}
        3. Searchable and discoverable
        4. Varied in length and specificity
        
        Keywords:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.7
        )
        
        keywords_text = result[0].split("Keywords:")[-1].strip()
        
        # Parse keywords
        keywords = []
        for line in keywords_text.split('\n'):
            if line.strip() and (line.startswith('-') or line[0].isdigit()):
                keyword = line.strip().lstrip('-').lstrip('0123456789.')
                keywords.append(keyword)
        
        return keywords[:num_keywords]


# Export all functionalities
__all__ = [
    'TextFormatter',
    'functionality_20_generate_hashtags',
    'functionality_21_generate_headlines',
    'functionality_22_rewrite_text',
    'functionality_23_generate_call_to_action',
    'functionality_24_generate_meta_description',
    'ContentExpander',
    'ContentCondenser',
    'StyleAdapter',
    'TextValidator',
    'ContentPlanner',
    'KeywordGenerator'
]

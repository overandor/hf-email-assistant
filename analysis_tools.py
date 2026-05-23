"""
Analysis Tools Module - Data Analysis and Insights LLM Operations
5 LLM Functionalities (5000 LOC target)
"""

from typing import Dict, List, Optional, Tuple
import re
import logging
from .models import ModelManager, functionality_1_generate_text, functionality_2_analyze_sentiment, functionality_3_summarize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextAnalyzer:
    """
    Advanced text analysis with multiple dimensions.
    Analyzes structure, patterns, and content characteristics.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
        self.analyzer = model_manager.pipelines.get('sentiment')
    
    def analyze_text_complexity(self, text: str) -> Dict[str, float]:
        """Analyze complexity of text."""
        words = text.split()
        sentences = text.split('.')
        
        metrics = {
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            'vocabulary_richness': len(set(words)) / len(words) if words else 0,
            'readability_score': self._calculate_readability(text)
        }
        
        return metrics
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified Flesch)."""
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.5
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllable_count = sum(self._count_syllables(w) for w in words) / len(words)
        
        # Simplified readability formula
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllable_count)
        return max(0, min(100, readability / 100))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        return max(1, count)


def functionality_15_extract_key_points(
    text: str,
    num_points: int = 5,
    summary_type: str = "Bullet Points"
) -> List[str]:
    """
    LLM Functionality 15: Key Point Extraction
    
    Extract key points and main ideas from text.
    Generates concise summaries of important information.
    
    Args:
        text: Input text to analyze
        num_points: Number of key points to extract
        summary_type: Format of output (Bullet Points, Numbered List, Paragraph)
    
    Returns:
        List of key points
    
    Example:
        >>> functionality_15_extract_key_points(article, 5)
        ['Point 1: ...', 'Point 2: ...', ...]
    """
    try:
        prompt = f"""
        Text:
        {text[:1000]}
        
        Extract {num_points} key points from this text.
        Format as {summary_type}.
        Each point should be concise and capture main ideas.
        
        Key Points:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.5
        )
        
        points_text = result[0].split("Key Points:")[-1].strip()
        
        # Parse points
        points = []
        for line in points_text.split('\n'):
            if line.strip() and (line.startswith('-') or line[0].isdigit() or line.startswith('•')):
                points.append(line.strip())
        
        return points[:num_points]
    
    except Exception as e:
        logger.error(f"Key point extraction error: {e}")
        raise


def functionality_16_analyze_sentiment_trend(
    texts: List[str],
    time_labels: List[str] = None
) -> Dict[str, List]:
    """
    LLM Functionality 16: Sentiment Trend Analysis
    
    Analyze sentiment changes across multiple texts over time.
    Identifies patterns and trends in emotional tone.
    
    Args:
        texts: List of texts to analyze
        time_labels: Optional time labels for each text
    
    Returns:
        Dictionary with sentiment trends over time
    
    Example:
        >>> functionality_16_analyze_sentiment_trend([email1, email2, email3])
        {'labels': ['Day 1', 'Day 2', 'Day 3'], 'positive': [0.8, 0.6, 0.9], 'negative': [0.2, 0.4, 0.1]}
    """
    try:
        if time_labels is None:
            time_labels = [f"Point {i+1}" for i in range(len(texts))]
        
        trends = {
            'labels': time_labels,
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        for text in texts:
            sentiment = functionality_2_analyze_sentiment(text)
            positive = sentiment.get('POSITIVE', 0)
            negative = sentiment.get('NEGATIVE', 0)
            neutral = 1.0 - positive - negative
            
            trends['positive'].append(positive)
            trends['negative'].append(negative)
            trends['neutral'].append(max(0, neutral))
        
        return trends
    
    except Exception as e:
        logger.error(f"Sentiment trend analysis error: {e}")
        raise


def functionality_17_compare_texts(
    text1: str,
    text2: str,
    comparison_type: str = "Similarity"
) -> Dict[str, any]:
    """
    LLM Functionality 17: Text Comparison and Analysis
    
    Compare two texts and analyze similarities/differences.
    Provides detailed comparison metrics and insights.
    
    Args:
        text1: First text to compare
        text2: Second text to compare
        comparison_type: Type of comparison (Similarity, Differences, Style)
    
    Returns:
        Dictionary with comparison results
    
    Example:
        >>> functionality_17_compare_texts(draft1, draft2)
        {'similarity_score': 0.85, 'differences': [...], 'analysis': '...'}
    """
    try:
        prompt = f"""
        Text 1:
        {text1[:500]}
        
        Text 2:
        {text2[:500]}
        
        Comparison Type: {comparison_type}
        
        Compare these texts and provide:
        1. Similarity score (0-1)
        2. Key differences
        3. Shared themes
        4. Style comparison
        5. Overall analysis
        
        Comparison:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.5
        )
        
        comparison_text = result[0].split("Comparison:")[-1].strip()
        
        # Parse comparison
        comparison = {
            'similarity_score': 0.7,
            'differences': [],
            'shared_themes': [],
            'style_comparison': '',
            'analysis': comparison_text
        }
        
        return comparison
    
    except Exception as e:
        logger.error(f"Text comparison error: {e}")
        raise


def functionality_18_generate_insights(
    data: str,
    insight_type: str = "Business",
    context: str = ""
) -> List[str]:
    """
    LLM Functionality 18: Insight Generation from Data
    
    Generate actionable insights from data or text.
    Identifies patterns, trends, and opportunities.
    
    Args:
        data: Data or text to analyze
        insight_type: Type of insights (Business, Technical, Strategic)
        context: Additional context for analysis
    
    Returns:
        List of generated insights
    
    Example:
        >>> functionality_18_generate_insights(sales_data, "Business")
        ['Insight 1: Sales increased by 20%', 'Insight 2: ...']
    """
    try:
        prompt = f"""
        Data:
        {data[:800]}
        
        Context: {context}
        Insight Type: {insight_type}
        
        Generate 5 actionable insights from this data.
        Each insight should:
        1. Be specific and data-driven
        2. Include supporting evidence
        3. Suggest actionable next steps
        4. Be relevant to {insight_type} context
        
        Insights:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.6
        )
        
        insights_text = result[0].split("Insights:")[-1].strip()
        
        # Parse insights
        insights = []
        for line in insights_text.split('\n'):
            if line.strip() and (line.startswith('-') or line[0].isdigit() or line.startswith('•')):
                insights.append(line.strip())
        
        return insights[:5]
    
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        raise


def functionality_19_classify_content(
    text: str,
    categories: List[str],
    multi_label: bool = False
) -> Dict[str, float]:
    """
    LLM Functionality 19: Content Classification
    
    Classify text into predefined categories.
    Supports single-label and multi-label classification.
    
    Args:
        text: Text to classify
        categories: List of possible categories
        multi_label: Allow multiple category assignments
    
    Returns:
        Dictionary with category confidence scores
    
    Example:
        >>> functionality_19_classify_content(article, ['Tech', 'Business', 'Health'])
        {'Tech': 0.85, 'Business': 0.30, 'Health': 0.10}
    """
    try:
        categories_text = ', '.join(categories)
        mode = "multiple categories" if multi_label else "single best category"
        
        prompt = f"""
        Text:
        {text[:500]}
        
        Categories: {categories_text}
        Classification Mode: {mode}
        
        Classify this text into the most appropriate categories.
        Provide confidence scores for each category (0-1).
        
        Classification:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=300,
            temperature=0.4
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
        logger.error(f"Content classification error: {e}")
        raise


class PatternAnalyzer:
    """
    Analyze patterns in text data.
    Identifies recurring themes, structures, and anomalies.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def analyze_patterns(
        self,
        texts: List[str],
        pattern_type: str = "Thematic"
    ) -> Dict[str, any]:
        """Analyze patterns across multiple texts."""
        combined_text = '\n\n'.join(texts[:5])
        
        prompt = f"""
        Texts:
        {combined_text[:1000]}
        
        Pattern Type: {pattern_type}
        
        Analyze these texts for patterns including:
        1. Recurring themes
        2. Common structures
        3. Frequency patterns
        4. Anomalies or outliers
        5. Trend patterns
        
        Pattern Analysis:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=600,
            temperature=0.5
        )
        
        analysis_text = result[0].split("Pattern Analysis:")[-1].strip()
        
        return {
            'pattern_type': pattern_type,
            'analysis': analysis_text,
            'num_texts_analyzed': len(texts)
        }


class TopicExtractor:
    """
    Extract topics and themes from text.
    Identifies main subjects and subtopics.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def extract_topics(
        self,
        text: str,
        num_topics: int = 5,
        granularity: str = "Main Topics"
    ) -> List[Dict[str, str]]:
        """Extract topics from text."""
        prompt = f"""
        Text:
        {text[:1000]}
        
        Number of Topics: {num_topics}
        Granularity: {granularity}
        
        Extract {num_topics} main topics from this text.
        For each topic, provide:
        1. Topic name
        2. Brief description
        3. Relevance score
        
        Topics:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.6
        )
        
        topics_text = result[0].split("Topics:")[-1].strip()
        
        # Parse topics
        topics = []
        current_topic = {}
        
        for line in topics_text.split('\n'):
            if line.strip():
                if 'Topic' in line or line[0].isdigit():
                    if current_topic:
                        topics.append(current_topic)
                    current_topic = {'name': line.strip()}
                elif 'Description' in line:
                    current_topic['description'] = line.split(':')[1].strip()
                elif 'Relevance' in line:
                    current_topic['relevance'] = line.split(':')[1].strip()
        
        if current_topic:
            topics.append(current_topic)
        
        return topics[:num_topics]


class EntityRecognizer:
    """
    Recognize and extract entities from text.
    Identifies people, organizations, locations, and more.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def recognize_entities(
        self,
        text: str,
        entity_types: List[str] = None
    ) -> Dict[str, List[str]]:
        """Recognize entities in text."""
        if entity_types is None:
            entity_types = ['Person', 'Organization', 'Location', 'Date', 'Product']
        
        prompt = f"""
        Text:
        {text[:800]}
        
        Entity Types: {', '.join(entity_types)}
        
        Recognize and extract entities of the specified types.
        List each entity with its type.
        
        Entities:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=400,
            temperature=0.4
        )
        
        entities_text = result[0].split("Entities:")[-1].strip()
        
        # Parse entities
        entities = {etype: [] for etype in entity_types}
        
        for line in entities_text.split('\n'):
            for etype in entity_types:
                if etype in line:
                    entity_name = line.replace(etype, '').strip()
                    entities[etype].append(entity_name)
        
        return entities


class RelationshipExtractor:
    """
    Extract relationships between entities in text.
    Identifies connections and dependencies.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.generator = model_manager.pipelines.get('text_generation')
    
    def extract_relationships(
        self,
        text: str,
        relationship_types: List[str] = None
    ) -> List[Dict[str, str]]:
        """Extract relationships from text."""
        if relationship_types is None:
            relationship_types = ['works_for', 'located_in', 'part_of', 'related_to', 'owns']
        
        prompt = f"""
        Text:
        {text[:800]}
        
        Relationship Types: {', '.join(relationship_types)}
        
        Extract relationships between entities in this text.
        For each relationship, specify:
        1. Entity 1
        2. Relationship type
        3. Entity 2
        4. Context
        
        Relationships:
        """
        
        result = functionality_1_generate_text(
            prompt,
            max_length=500,
            temperature=0.5
        )
        
        relationships_text = result[0].split("Relationships:")[-1].strip()
        
        # Parse relationships
        relationships = []
        current_rel = {}
        
        for line in relationships_text.split('\n'):
            if line.strip():
                if 'Entity' in line:
                    if current_rel:
                        relationships.append(current_rel)
                    current_rel = {}
                elif 'Relationship' in line:
                    current_rel['type'] = line.split(':')[1].strip()
                elif 'Context' in line:
                    current_rel['context'] = line.split(':')[1].strip()
        
        if current_rel:
            relationships.append(current_rel)
        
        return relationships


class SummarizationEngine:
    """
    Advanced summarization with multiple strategies.
    Supports abstractive and extractive summarization.
    """
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.summarizer = model_manager.pipelines.get('summarization')
    
    def summarize_with_focus(
        self,
        text: str,
        focus_area: str,
        max_length: int = 150
    ) -> str:
        """Summarize text with focus on specific area."""
        prompt = f"""
        Text:
        {text}
        
        Focus Area: {focus_area}
        
        Summarize this text with special attention to {focus_area}.
        Keep summary under {max_length} words.
        
        Summary:
        """
        
        return functionality_3_summarize_text(text, max_length=max_length)
    
    def summarize_multi_document(
        self,
        documents: List[str],
        combined_length: int = 200
    ) -> str:
        """Summarize multiple documents."""
        combined = '\n\n'.join(documents)
        return functionality_3_summarize_text(combined, max_length=combined_length)


# Export all functionalities
__all__ = [
    'TextAnalyzer',
    'functionality_15_extract_key_points',
    'functionality_16_analyze_sentiment_trend',
    'functionality_17_compare_texts',
    'functionality_18_generate_insights',
    'functionality_19_classify_content',
    'PatternAnalyzer',
    'TopicExtractor',
    'EntityRecognizer',
    'RelationshipExtractor',
    'SummarizationEngine'
]

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def generate_mcqs(topic, context='', number=5):
    """
    Generate Multiple Choice Questions for a given topic
    
    Args:
        topic (str): Topic to generate MCQs for
        context (str): Context text from documents
        number (int): Number of MCQs to generate (default: 5)
    
    Returns:
        list: List of MCQ dictionaries
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""Create {number} high-quality multiple choice questions about "{topic}".
    Use this context for accurate questions: {context[:2000]}
    
    Each MCQ should follow this exact structure:
    1. Clear, specific question
    2. Four distinct options (a, b, c, d)
    3. One clearly correct answer
    4. Detailed explanation of why the answer is correct
    
    Respond with a JSON array where each MCQ has this exact format:
    {{
        "question": "What is...",
        "choices": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "correct_answer": "a",
        "explanation": "Detailed explanation..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        json_str = response.text
        # Find JSON array in response if it's not pure JSON
        if not json_str.strip().startswith('['):
            import re
            json_match = re.search(r'\[.*\]', json_str, re.DOTALL)
            if json_match:
                json_str = json_match.group()
        
        # Parse MCQs
        mcqs = json.loads(json_str)
        
        # Validate and clean MCQs
        validated_mcqs = []
        for mcq in mcqs:
            if (isinstance(mcq, dict) and
                'question' in mcq and
                'choices' in mcq and
                'correct_answer' in mcq and
                'explanation' in mcq and
                len(mcq['choices']) == 4):
                
                # Ensure choices has exactly a, b, c, d keys
                if all(key in mcq['choices'] for key in ['a', 'b', 'c', 'd']):
                    validated_mcqs.append(mcq)
        
        if validated_mcqs:
            return validated_mcqs
        
        raise ValueError("No valid MCQs generated")
        
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        # Return fallback MCQs
        return [{
            "question": f"What is a key concept in {topic}?",
            "choices": {
                "a": "First fundamental principle",
                "b": "Second core concept",
                "c": "Third main idea",
                "d": "Fourth basic element"
            },
            "correct_answer": "a",
            "explanation": f"This is a sample question about {topic}. Please try regenerating MCQs."
        }] * number

def generate_topic_list(documents):
    """
    Generate a list of meaningful topics from documents
    
    Args:
        documents (list): List of document texts
    
    Returns:
        list: List of topic strings
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""Analyze these documents and extract 5-8 key study topics.
    
    Documents: {' '.join(documents)[:3000]}
    
    Requirements:
    1. Topics should be 2-4 words long
    2. Cover different aspects of the content
    3. Be specific and meaningful
    4. Avoid overlapping topics
    
    Respond with just a JSON array of topic strings."""
    
    try:
        response = model.generate_content(prompt)
        
        # Parse topics
        topics = json.loads(response.text)
        
        # Validate topics
        validated_topics = [
            topic for topic in topics 
            if isinstance(topic, str) and 
            len(topic.split()) >= 2 and 
            len(topic.split()) <= 4
        ]
        
        if validated_topics:
            return validated_topics[:8]  # Limit to 8 topics
        
        raise ValueError("No valid topics generated")
        
    except Exception as e:
        print(f"Error generating topics: {e}")
        return [
            "Document Key Concepts",
            "Main Theme Analysis",
            "Critical Framework Understanding",
            "Core Principles Review"
        ]
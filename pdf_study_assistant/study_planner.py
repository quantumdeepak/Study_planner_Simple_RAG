import os
import re
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def generate_comprehensive_topics(documents):
    """
    Use Gemini to generate comprehensive list of study topics
    
    :param documents: List of document texts
    :return: List of detailed study topics
    """
    # Combine all documents
    combined_text = " ".join(documents)
    
    # Use Gemini for topic generation
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""From the following documents, generate a comprehensive list of study topics:

Criteria for topic selection:
- Must be specific and actionable
- Derive from the core content of the documents
- Cover different aspects and depth levels
- Ensure topics are distinct and non-overlapping

Documents:
{combined_text[:10000]}

Output Format:
- List topics with brief description
"""
    
    try:
        response = model.generate_content(prompt)
        
        # Parse topics from response
        topics = []
        for line in response.text.split('\n'):
            if line.strip() and ':' in line:
                topic, details = line.split(':', 1)
                topics.append({
                    'name': topic.strip(),
                    'description': details.strip(),
                    'completed_percentage': 0
                })
        
        return topics
    
    except Exception as e:
        print(f"Error generating topics: {e}")
        return [{'name': 'General Study', 'description': 'Comprehensive study plan', 'completed_percentage': 0}]

def generate_advanced_study_plan(documents, study_hours_per_day=2, total_weeks=4):
    """
    Generate an advanced, AI-powered personalized study plan
    
    :param documents: List of document texts
    :param study_hours_per_day: Hours to study daily
    :param total_weeks: Total weeks for the study plan
    :return: Detailed study plan with advanced topic allocation
    """
    # Generate comprehensive topics
    topics = generate_comprehensive_topics(documents)
    
    # Initialize study plan
    start_date = datetime.now().date()
    study_plan = []
    
    # Distribute topics across weeks
    for week in range(1, total_weeks + 1):
        week_plan = {
            'week': week,
            'start_date': (start_date + timedelta(days=(week-1)*7)).strftime("%B %d, %Y"),
            'total_study_hours': study_hours_per_day * 7,
            'topics': []
        }
        
        # Calculate number of topics for this week
        topics_this_week = topics[(week-1)::total_weeks]
        
        # If no topics left, use a generic study topic
        if not topics_this_week:
            topics_this_week = [{
                'name': f'General Study Week {week}',
                'description': 'Comprehensive review and skill consolidation'
            }]
        
        for topic in topics_this_week:
            topic_plan = {
                'name': topic['name'],
                'description': topic.get('description', 'No description available'),
                'hours': study_hours_per_day,
                'completed_percentage': 0,
                'activities': [
                    f"In-depth study of {topic['name']}",
                    "Take comprehensive notes",
                    "Create summary mind maps",
                    "Practice self-assessment",
                    "Identify knowledge gaps"
                ]
            }
            week_plan['topics'].append(topic_plan)
        
        # Add weekly review session
        week_plan['topics'].append({
            'name': 'Weekly Review and Reflection',
            'hours': 1,
            'activities': [
                "Consolidate week's learning",
                "Review progress",
                "Adjust study strategy",
                "Plan for next week"
            ],
            'completed_percentage': 0
        })
        
        study_plan.append(week_plan)
    
    return study_plan

def generate_study_plan(documents, study_hours_per_day=2, total_weeks=4):
    """
    Fallback study plan generator
    """
    # Existing implementation as a backup
    topics = extract_topics(documents)
    
    if not topics:
        topics = ["General Study Topic"]
    
    start_date = datetime.now().date()
    study_plan = []
    
    topics_per_week = max(1, len(topics) // total_weeks)
    
    for week in range(1, total_weeks + 1):
        week_topics = topics[(week-1)*topics_per_week:week*topics_per_week]
        
        week_plan = {
            'week': week,
            'start_date': (start_date + timedelta(days=(week-1)*7)).strftime("%B %d, %Y"),
            'total_study_hours': len(week_topics) * study_hours_per_day,
            'topics': []
        }
        
        for topic in week_topics:
            topic_plan = {
                'name': topic,
                'hours': study_hours_per_day,
                'activities': [
                    f"In-depth reading on {topic}",
                    f"Create summary notes",
                    f"Practice recall",
                    f"Identify knowledge gaps"
                ]
            }
            week_plan['topics'].append(topic_plan)
        
        study_plan.append(week_plan)
    
    return study_plan

def extract_topics(documents):
    """
    Extract key topics from documents
    """
    topics = []
    for doc in documents:
        potential_topics = re.findall(r'^[A-Z][a-zA-Z\s]+[:.]', doc, re.MULTILINE)
        key_paragraphs = re.findall(r'^(?=.*[A-Z])(?=.*\w{10,}).+$', doc, re.MULTILINE)
        
        topics.extend(potential_topics)
        
        for para in key_paragraphs[:5]:
            first_words = ' '.join(para.split()[:3])
            if len(first_words.split()) > 1:
                topics.append(first_words)
    
    return list(set(t.strip(':.') for t in topics))
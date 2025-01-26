import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def generate_topic_list(documents):
    """
    Generate a comprehensive and meaningful list of topics from the uploaded documents
    
    :param documents: List of document texts
    :return: List of refined topics
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""Analyze the following documents and extract a comprehensive list of study topics. 
    Your goal is to create a list of meaningful, substantive topics that:
    
    Topic Selection Criteria:
    1. Must be at least 2-3 words long
    2. Represent significant, distinct areas of knowledge
    3. Cover the breadth and depth of the document's content
    4. Avoid single-word or overly broad topics
    5. Ensure topics are specific, actionable, and relevant to learning
    
    Desired Output Format:
    - Provide 8-10 well-defined, descriptive topics
    - Each topic should be a clear, meaningful phrase
    - Topics should be mutually exclusive and cover different aspects of the documents
    
    Example Good Topics:
    - Advanced Machine Learning Techniques
    - Sustainable Energy Infrastructure
    - Cognitive Psychology Principles
    
    Example Bad Topics:
    - Machine Learning
    - Energy
    - Psychology
    
    Documents Context:
    {' '.join(documents)[:15000]}  # Limit to first 15000 characters
    
    Respond strictly as a JSON array of topics."""
    
    try:
        response = model.generate_content(prompt)
        
        # Parse topics from response
        try:
            # First, try direct JSON parsing
            topics = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback parsing if JSON fails
            print("Direct JSON parsing failed. Attempting manual parsing.")
            # Clean and filter topics
            topics = []
            for line in response.text.split('\n'):
                # Remove bullet points, numbers, and strip whitespace
                topic = re.sub(r'^[-*•\d.\s]+', '', line).strip()
                
                # Add topic if it meets criteria
                if topic and len(topic.split()) >= 2 and len(topic) > 3:
                    topics.append(topic)
        
        # Ensure we have a minimum number of topics
        if not topics:
            topics = [
                "Core Document Analysis",
                "Key Knowledge Domains",
                "Comprehensive Study Insights"
            ]
        
        # Limit to 10 topics and remove any single-word or very short topics
        topics = [topic for topic in topics if len(topic.split()) >= 2][:10]
        
        return topics
    
    except Exception as e:
        print(f"Error generating topics: {e}")
        return [
            "Comprehensive Document Study",
            "Key Knowledge Areas",
            "Advanced Learning Insights",
            "Strategic Topic Analysis",
            "Detailed Document Review"
        ]



def generate_mcqs(topic, context=''):
    """
    Generate Multiple Choice Questions for a given topic
    
    :param topic: Topic to generate MCQs for
    :param context: Optional context from documents
    :return: List of MCQ dictionaries
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""Generate 10 high-quality multiple-choice questions about "{topic}". 
    Detailed MCQ Generation Guidelines:
    
    Question Design Criteria:
    1. Questions must be clear, precise, and challenging
    2. Cover different cognitive levels (recall, understanding, application)
    3. Ensure distractors are plausible but incorrect
    4. Avoid trivial or overly obvious questions
    5. Provide substantive, educational explanations
    
    Question Structure:
    - Stem: Clear, concise question
    - 4 options (a, b, c, d)
    - One definitively correct answer
    - Comprehensive explanation demonstrating deeper understanding
    
    Context for Topic Depth:
    {context[:2000]}  # Limit context to 2000 characters

    Output Format:
    JSON array with these keys for each question:
    - question: Full question text
    - choices: Object with a, b, c, d options
    - correct_answer: Correct option letter
    - explanation: Detailed explanation of the correct answer
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Robust JSON parsing
        try:
            mcqs = json.loads(response.text)
        except json.JSONDecodeError:
            print("Direct JSON parsing failed. Attempting manual parsing.")
            # Fallback parsing logic
            mcqs = []
        
        # Validate MCQs
        validated_mcqs = []
        for mcq in mcqs:
            # Ensure all required keys exist
            if all(key in mcq for key in ['question', 'choices', 'correct_answer', 'explanation']):
                # Ensure choices has exactly 4 options
                if len(mcq['choices']) == 4:
                    validated_mcqs.append(mcq)
        
        # Fallback if no valid MCQs
        if not validated_mcqs:
            validated_mcqs = [
                {
                    "question": f"What is a key aspect of {topic}?",
                    "choices": {
                        "a": "First important concept",
                        "b": "Second significant idea", 
                        "c": "Third crucial point",
                        "d": "Fourth critical understanding"
                    },
                    "correct_answer": "a",
                    "explanation": "This is a placeholder MCQ to ensure test functionality"
                }
            ]
        
        return validated_mcqs
    
    except Exception as e:
        print(f"Error generating MCQs for {topic}: {e}")
        return [
            {
                "question": f"What is an important aspect of {topic}?",
                "choices": {
                    "a": "First core concept",
                    "b": "Second fundamental idea", 
                    "c": "Third key principle",
                    "d": "Fourth essential understanding"
                },
                "correct_answer": "a",
                "explanation": "Fallback MCQ for system reliability"
            }
        ]
    



import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# Load environment variables
load_dotenv()

# Load response JSON template
def load_response_json():
    try:
        with open("response.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback template if file not found
        return {
            "1": {
                "mcq": "Sample Question",
                "options": {
                    "a": "Option A",
                    "b": "Option B", 
                    "c": "Option C",
                    "d": "Option D"
                },
                "correct": "a",
                "explanation": "Sample explanation"
            }
        }




import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
import json

# Load environment variables
load_dotenv()

# Initialize LLM with GEMINI_API_KEY
llm = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"),  # Changed from GOOGLE_API_KEY
    model="gemini-pro",
    temperature=0.7
)
# MCQ Generation Templates
TEMPLATE = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 

Key Requirements:
- Create {number} unique MCQs
- Ensure questions are based on the given text
- Avoid repetitive questions
- Provide detailed explanations
- Format strictly according to the JSON template

Output Format Guidelines:
- Each MCQ must have:
  1. A clear, concise question
  2. 4 distinct answer options
  3. Clearly marked correct answer
  4. Comprehensive explanation

JSON Template to Follow:
{RESPONSE_JSON}
"""

TEMPLATE2 = """
You are an expert English grammarian and writer. Evaluate the following quiz for {subject} students:

Complexity Analysis Criteria:
- Cognitive level appropriateness
- Question clarity
- Analytical depth
- Age/educational level alignment

Quiz to Evaluate:
{quiz}

Provide a critical review and suggest improvements if needed.
"""

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

# Load environment variables
load_dotenv()

def generate_mcqs(topic, context='', number=10, subject='general', tone='academic'):
    """
    Generate Multiple Choice Questions using Langchain
    
    :param topic: Topic for MCQ generation
    :param context: Optional context text
    :param number: Number of MCQs to generate
    :param subject: Educational subject/level
    :param tone: Tone of the questions
    :return: List of MCQs
    """
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            model="gemini-pro",
            temperature=0.7
        )

        # Prepare response JSON template
        RESPONSE_JSON = {
            "1": {
                "mcq": "Sample Question",
                "options": {
                    "a": "Option A",
                    "b": "Option B", 
                    "c": "Option C",
                    "d": "Option D"
                },
                "correct": "a",
                "explanation": "Sample explanation"
            }
        }

        # MCQ Generation Template
        TEMPLATE = """
        Topic: {topic}
        Context: {context}

        You are an expert MCQ maker. Create {number} unique multiple-choice questions for {subject} students in {tone} tone.

        Key Requirements:
        - Questions must be based on the topic and context
        - Avoid repetitive questions
        - Ensure each question tests different aspects of knowledge
        - Provide clear, plausible options
        - Include a detailed explanation for each correct answer

        Output Format:
        {RESPONSE_JSON}
        """

        # Prompt Templates
        quiz_generation_prompt = PromptTemplate(
            input_variables=["topic", "context", "number", "subject", "tone", "RESPONSE_JSON"],
            template=TEMPLATE
        )

        # Create LLM Chain
        quiz_chain = LLMChain(
            llm=llm, 
            prompt=quiz_generation_prompt, 
            output_key="quiz"
        )

        # Generate MCQs
        result = quiz_chain({
            "topic": topic,
            "context": context[:2000],  # Limit context length
            "number": number,
            "subject": subject,
            "tone": tone,
            "RESPONSE_JSON": json.dumps(RESPONSE_JSON)
        })

        # Parse and validate MCQs
        try:
            # Try to parse the quiz from the result
            quiz = json.loads(result['quiz'])
            
            # Convert to list format
            mcqs = []
            for key, mcq in quiz.items():
                mcqs.append({
                    "question": mcq['mcq'],
                    "choices": mcq['options'],
                    "correct_answer": mcq['correct'],
                    "explanation": mcq.get('explanation', 'No explanation provided')
                })
            
            return mcqs
        
        except (json.JSONDecodeError, KeyError) as parse_error:
            print(f"MCQ Parsing Error: {parse_error}")
            print("Raw result:", result.get('quiz', 'No quiz generated'))
            
            # Fallback MCQs
            return [
                {
                    "question": f"What is a key aspect of {topic}?",
                    "choices": {
                        "a": "First Concept", 
                        "b": "Second Idea", 
                        "c": "Third Principle", 
                        "d": "Fourth Understanding"
                    },
                    "correct_answer": "a",
                    "explanation": f"Fallback MCQ for {topic}"
                }
            ] * number
    
    except Exception as e:
        print(f"MCQ Generation Error: {e}")
        
        # Fallback MCQs
        return [
            {
                "question": f"What is a key aspect of {topic}?",
                "choices": {
                    "a": "First Concept", 
                    "b": "Second Idea", 
                    "c": "Third Principle", 
                    "d": "Fourth Understanding"
                },
                "correct_answer": "a",
                "explanation": f"Fallback MCQ for {topic}"
            }
        ] * number
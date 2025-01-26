import os
import re
import nltk
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Download NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def extract_pdf_text(filepath):
    """
    Extract text from a PDF file
    
    :param filepath: Path to the PDF file
    :return: Extracted text with filename and metadata
    """
    try:
        reader = PdfReader(filepath)
        text = "\n".join([page.extract_text() for page in reader.pages])
        cleaned_text = clean_text(text)
        
        # Add filename and additional metadata
        metadata = f"Source File: {os.path.basename(filepath)}\n"
        metadata += f"Total Pages: {len(reader.pages)}\n"
        metadata += f"File Size: {os.path.getsize(filepath)} bytes\n\n"
        
        return metadata + cleaned_text
    except Exception as e:
        print(f"Error extracting text from {filepath}: {e}")
        return f"Error processing file: {os.path.basename(filepath)}"

def clean_text(text):
    """
    Clean extracted text
    
    :param text: Raw extracted text
    :return: Cleaned text
    """
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove headers, footers, page numbers
    text = re.sub(r'\b\d+\b', '', text)
    
    return text

# def generate_enhanced_summary(documents):
#     """
#     Generate a comprehensive summary with additional insights
    
#     :param documents: List of document texts
#     :return: Detailed summary with enhanced analysis
#     """
#     # Combine all documents
#     combined_text = " ".join(documents)
    
#     # Use Gemini for advanced summarization
#     model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
#     # Enhanced prompt for comprehensive analysis
#     prompt = f"""Provide an in-depth analysis of the following documents:
#     1. Create a comprehensive summary
#     2. Identify key themes and topics
#     3. Highlight unique insights and connections
#     4. Suggest potential areas of further exploration
    
#     Documents:
#     {combined_text[:15000]}  # Increased input limit
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         print(f"Error generating summary: {e}")
#         return "Comprehensive analysis could not be generated."


import markdown2  # Make sure to install this: pip install markdown2

def generate_enhanced_summary(documents):
    """
    Generate a comprehensive summary with markdown formatting
    
    :param documents: List of document texts
    :return: Markdown-formatted summary
    """
    # Combine all documents
    combined_text = " ".join(documents)
    
    # Use Gemini for advanced summarization
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Enhanced prompt for comprehensive markdown summary
    prompt = f"""Create a well-structured markdown-formatted summary of the following documents:

## Key Insights

- Use clear, concise bullet points
- Highlight main themes and topics
- Provide context and significance

## Detailed Analysis

Break down the content into sections with clear headings. Use markdown formatting including:
- Headers
- Bullet points
- Emphasis (bold/italic)
- Code blocks if relevant

Documents:
{combined_text[:15000]}  # Increased input limit
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "# Summary Error\n\nA comprehensive analysis could not be generated."

        
def generate_contextual_qa(context, query):
    """
    Generate a sophisticated question-answer response
    
    :param context: Relevant context from similar documents
    :param query: User's query
    :return: Nuanced and contextual answer
    """
    # Use Gemini for advanced question answering
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""Provide a comprehensive, nuanced response to the query based on the given context:

Context Overview:
{context}

Detailed Query: {query}

Instructions:
- Analyze the query in depth
- Provide a well-structured, informative response
- If the answer is not directly available, explain why
- Suggest related information or alternative approaches
- Maintain academic rigor and clarity
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "A comprehensive answer could not be generated at this time."
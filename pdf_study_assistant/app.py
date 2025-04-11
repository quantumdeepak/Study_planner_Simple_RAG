import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
# from dotenv import load_dotenvclear
from pdf_processor import (
    extract_pdf_text, 
    generate_enhanced_summary, 
    generate_contextual_qa
)

from study_planner import (
    generate_study_plan, 
    generate_advanced_study_plan  # Add this line to import the new function
)

import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from pdf_processor import (
    extract_pdf_text, 
    generate_enhanced_summary, 
    generate_contextual_qa
)
from vector_db import VectorDatabase
from study_planner import (
    generate_study_plan,  # Keep the original import
    generate_advanced_study_plan  # Add the new import
)


from vector_db import VectorDatabase
from study_planner import generate_study_plan

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global application state management
class ApplicationState:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ApplicationState, cls).__new__(cls)
            cls._instance.documents = []
            cls._instance.vector_db = None
            cls._instance.uploaded_files = []
        return cls._instance
    
    def add_documents(self, new_documents, new_files):
        self.documents.extend(new_documents)
        self.uploaded_files.extend(new_files)
        self.vector_db = VectorDatabase(self.documents)
    
    def reset(self):
        self.documents = []
        self.vector_db = None
        self.uploaded_files = []

# Global state
app_state = ApplicationState()

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_pdfs():
#     if 'files' not in request.files:
#         return jsonify({"error": "No file part"}), 400
    
#     files = request.files.getlist('files')
    
#     # Extract text from PDFs
#     documents = []
#     uploaded_files = []
#     for file in files:
#         if file.filename == '':
#             continue
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filepath)
#         doc_text = extract_pdf_text(filepath)
#         documents.append(doc_text)
#         uploaded_files.append(file.filename)
    
#     # Update global application state
#     app_state.add_documents(documents, uploaded_files)
    
#     return jsonify({
#         "message": f"{len(documents)} PDFs processed successfully",
#         "files": uploaded_files
#     }), 200

@app.route('/upload', methods=['POST'])
def upload_pdfs():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files')
    
    # Extract text from PDFs
    documents = []
    uploaded_files = []
    for file in files:
        if file.filename == '':
            continue
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            doc_text = extract_pdf_text(filepath)
            documents.append(doc_text)
            uploaded_files.append(file.filename)
        except Exception as e:
            print(f"Error processing file {file.filename}: {e}")
    
    # Check if any documents were processed
    if not documents:
        return jsonify({"error": "No valid documents processed"}), 400
    
    # Update global application state
    try:
        app_state.add_documents(documents, uploaded_files)
    except Exception as e:
        print(f"Error adding documents: {e}")
        return jsonify({"error": "Failed to process documents"}), 500
    
    return jsonify({
        "message": f"{len(documents)} PDFs processed successfully",
        "files": uploaded_files
    }), 200

@app.route('/list_files')
def list_files():
    return jsonify({
        "files": app_state.uploaded_files
    }), 200

# @app.route('/generate_summary')
# def generate_pdf_summary():
#     if not app_state.documents:
#         return jsonify({"error": "No documents uploaded"}), 400
    
#     summary = generate_enhanced_summary(app_state.documents)
#     return render_template('summary.html', summary=summary)


import markdown2  # Add this import

@app.route('/generate_summary')
def generate_pdf_summary():
    if not app_state.documents:
        return jsonify({"error": "No documents uploaded"}), 400
    
    summary = generate_enhanced_summary(app_state.documents)
    
    # Convert markdown to HTML
    html_summary = markdown2.markdown(summary, extras=['tables', 'fenced-code-blocks'])
    
    return render_template('summary.html', summary=html_summary)

@app.route('/question_answer', methods=['GET', 'POST'])
def question_answer():
    if request.method == 'POST':
        query = request.form['query']
        
        if not app_state.vector_db:
            return jsonify({"error": "No documents processed"}), 400
        
        # Get similar documents
        similar_docs = app_state.vector_db.get_similar_doc_texts(query, top_k=3)
        
        # Generate answer using LLM with context
        context = "\n\n".join(similar_docs)
        answer = generate_contextual_qa(context, query)
        
        return render_template('question_answer.html', query=query, answer=answer)
    
    return render_template('question_answer.html')

# @app.route('/study_plan', methods=['GET', 'POST'])
# def study_plan():
#     if request.method == 'POST':
#         # Get study preferences from user
#         study_hours = int(request.form.get('study_hours', 2))
#         total_weeks = int(request.form.get('total_weeks', 4))
        
#         # Generate personalized study plan
#         plan = generate_study_plan(
#             app_state.documents, 
#             study_hours_per_day=study_hours, 
#             total_weeks=total_weeks
#         )
        
#         return render_template('study_plan.html', plan=plan)
    
#     return render_template('study_plan_input.html')


# @app.route('/study_plan', methods=['GET', 'POST'])
# def study_plan():
#     if request.method == 'POST':
#         # Get study preferences from user
#         study_hours = int(request.form.get('study_hours', 2))
#         total_weeks = int(request.form.get('total_weeks', 4))
        
#         # Generate advanced personalized study plan
#         plan = generate_advanced_study_plan(
#             app_state.documents, 
#             study_hours_per_day=study_hours, 
#             total_weeks=total_weeks
#         )
        
#         return render_template('study_plan.html', plan=plan)
    
#     return render_template('study_plan_input.html')




@app.route('/study_plan', methods=['GET', 'POST'])
def study_plan():
    if request.method == 'POST':
        # Ensure documents exist before generating plan
        if not app_state.documents:
            return jsonify({"error": "No documents uploaded"}), 400
        
        # Get study preferences from user
        study_hours = int(request.form.get('study_hours', 2))
        total_weeks = int(request.form.get('total_weeks', 4))
        
        # Generate advanced personalized study plan
        try:
            plan = generate_advanced_study_plan(
                app_state.documents, 
                study_hours_per_day=study_hours, 
                total_weeks=total_weeks
            )
            
            return render_template('study_plan.html', plan=plan)
        except Exception as e:
            # Fallback to basic plan if advanced generation fails
            print(f"Error in advanced study plan: {e}")
            plan = generate_study_plan(
                app_state.documents, 
                study_hours_per_day=study_hours, 
                total_weeks=total_weeks
            )
            return render_template('study_plan.html', plan=plan)
    
    return render_template('study_plan_input.html')

@app.route('/reset', methods=['POST'])
def reset_application():
    app_state.reset()
    return jsonify({"message": "Application state reset successfully"}), 200

@app.route('/uploaded_files')
def uploaded_files():
    return render_template('uploaded_files.html')

@app.route('/delete_file', methods=['DELETE'])
def delete_file():
    file_name = request.args.get('name')
    if not file_name:
        return jsonify({"error": "No file specified"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        app_state.uploaded_files.remove(file_name)  # Remove from the global state
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "File not found"}), 404

from study_planner import generate_study_plan
from mcq import generate_topic_list, generate_mcqs

# import google.generativeai as genai
# from flask import render_template, jsonify, request
# from flask import url_for
# @app.route('/generate_topics')
# def generate_topics():
#     """
#     Generate list of topics from uploaded documents
#     """
#     if not app_state.documents:
#         return jsonify({"error": "No documents uploaded"}), 400
    
#     # Use Gemini to generate topics
#     model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
#     prompt = f"""From the following documents, generate a comprehensive list of 10 key topics:

# Criteria for topic selection:
# - Must be specific and actionable
# - Derive from the core content of the documents
# - Cover different aspects and depth levels
# - Ensure topics are distinct and non-overlapping

# Documents:
# {' '.join(app_state.documents)[:10000]}

# Output Format:
# - Provide topics as a simple list of topic names
# - Each topic should be concise and descriptive
# """
    
#     try:
#         response = model.generate_content(prompt)
        
#         # Parse topics from response
#         topics = []
#         for line in response.text.split('\n'):
#             # Clean and filter topics
#             topic = line.strip().lstrip('- ')
#             if topic and len(topic) > 3:
#                 topics.append(topic)
        
#         # Limit to 10 topics
#         topics = topics[:10]
        
#         return render_template('topics.html', topics=topics)
    
#     except Exception as e:
#         print(f"Error generating topics: {e}")
#         return jsonify({"error": "Failed to generate topics"}), 500

# @app.route('/generate_mcq/<topic>')
# def generate_mcq(topic):
#     """
#     Generate Multiple Choice Questions for a specific topic
#     """
#     if not app_state.documents:
#         return jsonify({"error": "No documents uploaded"}), 400
    
#     # Use Gemini to generate MCQs
#     model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
#     prompt = f"""Generate 10 multiple-choice questions about the topic: "{topic}"

# Use the following documents as context:
# {' '.join(app_state.documents)[:15000]}

# Requirements for MCQs:
# - Create challenging and varied questions
# - Include 4 answer options for each question
# - Mark the correct answer
# - Ensure questions test different levels of understanding
# - Cover key aspects of the topic

# Output Format:
# For each question, provide:
# 1. Question text
# 2. 4 options (A, B, C, D)
# 3. Correct answer
# 4. Brief explanation of the correct answer
# """
    
#     try:
#         response = model.generate_content(prompt)
        
#         # Parse MCQs
#         mcqs = []
#         current_mcq = {}
#         lines = response.text.split('\n')
        
#         for line in lines:
#             line = line.strip()
#             if line.startswith('Q'):
#                 if current_mcq:
#                     mcqs.append(current_mcq)
#                 current_mcq = {'question': line}
#             elif line.startswith('A.') or line.startswith('B.') or line.startswith('C.') or line.startswith('D.'):
#                 if 'options' not in current_mcq:
#                     current_mcq['options'] = []
#                 current_mcq['options'].append(line)
#             elif line.startswith('Correct:'):
#                 current_mcq['correct'] = line.split('Correct:')[1].strip()
#             elif line.startswith('Explanation:'):
#                 current_mcq['explanation'] = line.split('Explanation:')[1].strip()
        
#         # Add last MCQ
#         if current_mcq:
#             mcqs.append(current_mcq)
        
#         # Limit to 10 MCQs
#         mcqs = mcqs[:10]
        
#         return render_template('mcq.html', topic=topic, mcqs=mcqs)
    
#     except Exception as e:
#         print(f"Error generating MCQs: {e}")
#         return jsonify({"error": "Failed to generate MCQs"}), 500


from mcq import generate_topic_list, generate_mcqs
@app.route('/generate_topics')
def generate_topics():
    """
    Generate list of topics from uploaded documents
    """
    if not app_state.documents:
        return jsonify({"error": "No documents uploaded"}), 400
    
    try:
        # Use the generate_topic_list function from mcq module
        topics = generate_topic_list(app_state.documents)
        
        return render_template('topics.html', topics=topics)
    
    except Exception as e:
        print(f"Error generating topics: {e}")
        return jsonify({"error": "Failed to generate topics"}), 500




# @app.route('/generate_mcq/<topic>')
# def generate_mcq(topic):
#     if not app_state.documents:
#         return jsonify({"error": "No documents uploaded"}), 400
    
#     try:
#         context = ' '.join(app_state.documents)
#         mcqs = generate_mcqs(topic, context=context, number=5)
#         return render_template('mcq.html', topic=topic, mcqs=mcqs)
#     except Exception as e:
#         return jsonify({"error": f"Failed to generate MCQs: {e}"}), 500


@app.route('/generate_mcq/<topic>')
def generate_mcq(topic):
    mode = request.args.get('mode', 'mcq')
    if not app_state.documents:
        return jsonify({"error": "No documents uploaded"}), 400
    
    try:
        context = ' '.join(app_state.documents)
        if mode == 'chat':
            return render_template('mcq.html', topic=topic, mcqs=[], mode='chat')
        else:
            mcqs = generate_mcqs(topic, context=context)
            return render_template('mcq.html', topic=topic, mcqs=mcqs, mode='mcq')
    except Exception as e:
        return jsonify({"error": f"Failed to generate content: {e}"}), 500



@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    try:
        # Clear files from upload directory
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")

        # Reset application state
        app_state.reset()
        
        return jsonify({
            "message": "All files cleared successfully",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"Error clearing files: {str(e)}",
            "status": "error"
        }), 500

from chat_handler import ChatHandler
chat_handler = ChatHandler()

@app.route('/chat_message', methods=['POST'])
def chat_message():
    data = request.get_json()
    topic = data.get('topic')
    message = data.get('message')
    is_new_chat = data.get('isNewChat', False)
    
    if is_new_chat:
        context = ' '.join(app_state.documents)
        response = chat_handler.start_chat(topic, context)
    else:
        response = chat_handler.handle_message(message)
        
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
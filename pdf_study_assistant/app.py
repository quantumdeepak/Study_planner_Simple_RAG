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

if __name__ == '__main__':
    app.run(debug=True)
# Flask PDF Processing and Study Planner Application

## Overview
This application provides advanced features for processing PDF documents, generating enhanced summaries, answering context-specific questions, and creating personalized study plans. It also includes the capability to generate topics and multiple-choice questions (MCQs) for educational purposes.

---

## Features

1. **Upload PDFs**
   - Upload multiple PDF files for text extraction and processing.
   ![Upload PDFs](image1)

2. **Generate Enhanced Summaries**
   - Create detailed summaries from the uploaded documents using AI-enhanced methods.
   ![Generate Enhanced Summaries](image2)

3. **Contextual Question & Answering**
   - Ask specific questions about the content of the uploaded documents and get accurate answers based on the context.
   ![Contextual Question & Answering](image3)

4. **Study Planner**
   - Generate a personalized study plan based on user preferences like study hours per day and total weeks available.
   ![Study Planner](image4)

5. **Advanced Study Plan**
   - If advanced AI-enhanced study planning fails, the application falls back to a simpler study plan generator.
   ![Advanced Study Plan](image5)

6. **List Uploaded Files**
   - View all the uploaded files in the application.
   ![List Uploaded Files](image6)

7. **Generate Topics**
   - Extract key topics from the uploaded documents for a structured study approach.
   ![Generate Topics](image7)

8. **Generate MCQs**
   - Create multiple-choice questions for any selected topic to aid in learning and assessment.
   ![Generate MCQs](image8)

9. **Delete Files**
   - Remove uploaded files from the application as needed.
   ![Delete Files](image9)

10. **Reset Application State**
    - Reset the application state to clear all uploaded files and processed data.
    ![Reset Application State](image10)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-name.git](https://github.com/quantumdeepak/Study_planner_Simple_RAG
   cd your-repo-name
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add the following environment variables:
   ```env
   SECRET_KEY=your_secret_key
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Usage

1. **Upload PDFs**
   - Use the upload page to add PDFs to the application.

2. **Generate Summaries**
   - Navigate to the summary page to create enhanced summaries from the documents.

3. **Ask Questions**
   - Use the Q&A page to get answers based on the content of the uploaded PDFs.

4. **Create a Study Plan**
   - Go to the study planner and enter your preferences to get a tailored plan.

5. **Generate Topics and MCQs**
   - Select topics to generate key subject areas and related MCQs.

6. **Manage Files**
   - View, delete, or reset the application state as needed.

---

## Folder Structure

```
|-- uploads/               # Folder for uploaded PDF files
|-- templates/             # HTML templates for rendering pages
|-- static/                # Static files (CSS, JS, images)
|-- app.py                 # Main Flask application
|-- pdf_processor.py       # Module for processing PDF files
|-- study_planner.py       # Module for study plan generation
|-- vector_db.py           # Vector database integration
|-- mcq.py                 # Module for topic and MCQ generation
```

---

## Future Enhancements

- Add integration with external AI APIs for topic and MCQ generation.
- Improve the user interface for a better user experience.
- Support additional file formats for document uploads.

---

## Contributing

Contributions are welcome! Please create a pull request or raise an issue in the repository.

---

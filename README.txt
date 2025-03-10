# Django Job Application System

## Project Overview
This is a Django-based job application system that allows users to upload their resumes, extracts relevant information using NLP, and matches their profiles with job postings stored in a MongoDB database. If a resume matches a job posting above a certain similarity threshold, the job details will be displayed to the user.

## Features
- User form to collect name, contact info, email, job domain preference, and resume (PDF upload)
- Resume data parsing using NLP and embeddings
- Job matching algorithm that compares parsed resumes with job descriptions
- MongoDB integration for storing resumes and job postings
- Web-based interface for users to view matching jobs

## Technologies Used
- Django (Backend Framework)
- MongoDB (Database)
- HTML, CSS, JavaScript (Frontend)
- Python (Resume Parsing, NLP, and Data Processing)
- SpaCy (NLP library for resume extraction)

## Project Structure
```
Trial-project/
├── trialapp/  # Main Django app
│   ├── templates/
│   │   ├── index1.html  # Frontend form for resume upload
│   ├── views.py  # Handles form submission and resume processing
│   ├── models.py  # MongoDB models
│   ├── urls.py  # URL routing
├── static/  # Static files (CSS, JS)
├── media/  # Uploaded resume files
├── settings.py  # Django project settings
├── urls.py  # Project-level URL configuration
├── manage.py  # Django management script
```

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd resumeAnalyse
   ```

   ```
4. Configure MongoDB connection in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'djongo',
           'NAME': 'your_database_name',
       }
   }
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```
7. Open `http://127.0.0.1:8000/` in your browser to access the application.

## How It Works
1. The user fills in the form and uploads a resume.
2. The resume is parsed using NLP to extract skills, experience, and projects.
3. The extracted details are compared with job descriptions in MongoDB.
4. Matching job postings are displayed to the user.
5. The user can apply if their match percentage is above 60%.



python --version : Python 3.12.2

python -m django --version : 5.1.6



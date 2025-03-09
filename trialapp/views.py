import os
import spacy
import pdfplumber
import docx
import re
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pymongo import MongoClient
from django.http import JsonResponse

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update URI if needed
resume_db = client["ResumeDB"]  # Resume Database
job_db = client["kaggle_db"]  # Job Database

resume_collection = resume_db["ParsedResumes"]  # Resumes Collection
job_collection = job_db["job_postings"]  # Job Postings Collection
matched_collection = resume_db["MatchedJobs"]  # Collection to store matched jobs

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Define keywords for parsing
SKILL_KEYWORDS = {"Python", "Java", "C++", "Flask", "Django", "Machine Learning", "Deep Learning", "SQL", "NoSQL", "AWS", "Terraform", "Linux"}
EXPERIENCE_KEYWORDS = {"intern", "developer", "engineer", "full-time", "research"}
PROJECT_KEYWORDS = {"project", "developed", "implemented", "designed"}

# Threshold for job matching
THRESHOLD = 50  # Percentage match


def index(request):
    """Render the upload page."""
    return render(request, 'index1.html')

def page2(request):
    return render(request, 'page2.html')    


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_resume_details(text):
    """Extract skills, projects, and experience from resume text."""
    skills, projects, experience = set(), set(), set()
    
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        for skill in SKILL_KEYWORDS:
            if re.search(rf"\b{re.escape(skill)}\b", line, re.IGNORECASE):
                skills.add(skill)

        if any(word in line.lower() for word in PROJECT_KEYWORDS):
            projects.add(line)

        if any(word in line.lower() for word in EXPERIENCE_KEYWORDS):
            experience.add(line)

    return {
        "Projects": list(projects),
        "Experience": list(experience),
        "Skills": sorted(skills)
    }


def store_resume_in_mongodb(parsed_data):
    """Store parsed resume data in MongoDB."""
    result = resume_collection.insert_one(parsed_data)
    print(f"Resume data inserted with ID: {result.inserted_id}")
    return str(result.inserted_id)  # Return the MongoDB document ID


def calculate_match(resume_skills, job_skills):
    """Calculate skill match percentage between resume and job posting."""
    if not isinstance(job_skills, str):  
        job_skills = ""

    resume_set = set(resume_skills)
    job_set = set(job_skills.split(", "))  # Assuming skills are comma-separated

    if not job_set:
        return 0

    common_skills = resume_set.intersection(job_set)
    match_percentage = (len(common_skills) / len(job_set)) * 100
    return match_percentage


def match_resume_to_jobs(resume_id, resume_skills):
    """Find and store job postings that match the resume skills."""
    matched_jobs = []

    jobs = list(job_collection.find())  # Fetch all job postings
    for job in jobs:
        job_title = job.get("job_title", "Unknown Job")
        job_company = job.get("company", "Unknown Company")
        job_location = job.get("job_location", "Unknown Location")
        job_link = job.get("job_link", "#")
        job_skills = job.get("job_skills", "")

        match_score = calculate_match(resume_skills, job_skills)

        if match_score >= THRESHOLD:
            matched_jobs.append({
                "job_title": job_title,
                "company": job_company,
                "location": job_location,
                "job_link": job_link,
                "match_score": round(match_score, 2)
            })

    if matched_jobs:
        matched_collection.insert_one({
            "resume_id": resume_id,
            "matched_jobs": matched_jobs
        })
        print(f"Matched jobs stored for Resume ID: {resume_id}")

    return matched_jobs


def upload_and_analyze(request):
    """Handle resume upload, parse details, store in DB, and match with jobs."""
    if request.method == "POST" and request.FILES.get("resume"):
        uploaded_file = request.FILES["resume"]
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_path = os.path.join(default_storage.location, file_path)

        # Extract text based on file type
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(full_path)
        elif uploaded_file.name.endswith(".docx"):
            resume_text = extract_text_from_docx(full_path)
        else:
            return JsonResponse({"error": "Unsupported file format"}, status=400)

        # Parse resume details
        parsed_data = extract_resume_details(resume_text)
        resume_id = store_resume_in_mongodb(parsed_data)  # Store in DB and get ID

        # Match with jobs
        matched_jobs = match_resume_to_jobs(resume_id, parsed_data["Skills"])

        return JsonResponse({
            "message": "Resume parsed and matched successfully!",
            "matched_jobs": matched_jobs
        })

    return JsonResponse({"error": "No file uploaded"}, status=400)


def get_matched_jobs(request):
    """Fetch matched jobs from MongoDB and return as JSON."""
    matched_jobs = list(matched_collection.find({}, {"_id": 0}))  # Fetch all matched jobs, exclude MongoDB ID

    return JsonResponse({"results": matched_jobs}, safe=False)

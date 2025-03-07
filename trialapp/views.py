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
#from .resume_parser import parse_resume 

def index(request):
    return render(request, 'index1.html')

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Define skill, experience, and project keywords
SKILL_KEYWORDS = {"Python", "Java", "C++", "Flask", "Django", "Machine Learning", "Deep Learning", "SQL", "NoSQL", "AWS", "Terraform", "Linux"}
EXPERIENCE_KEYWORDS = {"intern", "developer", "engineer", "full-time", "research"}
PROJECT_KEYWORDS = {"project", "developed", "implemented", "designed"}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to extract resume details
def extract_resume_details(text):
    skills = set()
    projects = set()
    experience = set()
    
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Extract skills
        for skill in SKILL_KEYWORDS:
            if re.search(rf"\b{re.escape(skill)}\b", line, re.IGNORECASE):
                skills.add(skill)
        # Extract projects
        if any(word in line.lower() for word in PROJECT_KEYWORDS):
            projects.add(line)
        # Extract experience
        if any(word in line.lower() for word in EXPERIENCE_KEYWORDS):
            experience.add(line)

    return {
        "Projects": list(projects),
        "Experience": list(experience),
        "Skills": sorted(skills)
    }

# Function to store extracted data in MongoDB
def store_in_mongodb(data):
    client = MongoClient("mongodb://localhost:27017/")  # Change if using a remote server
    db = client["ResumeDB"]  # Database name
    collection = db["ParsedResumes"]  # Collection name
    result = collection.insert_one(data)
    print(f"Resume data inserted with ID: {result.inserted_id}")

# Django View to Handle Resume Upload & Analysis
def upload_and_analyze(request):
    if request.method == "POST" and request.FILES.get("resume"):
        uploaded_file = request.FILES["resume"]
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))
        full_path = os.path.join(default_storage.location, file_path)

        # Determine file type and extract text
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(full_path)
        elif uploaded_file.name.endswith(".docx"):
            resume_text = extract_text_from_docx(full_path)
        else:
            return JsonResponse({"error": "Unsupported file format"}, status=400)

        # Extract details and store in DB
        parsed_data = extract_resume_details(resume_text)
        store_in_mongodb(parsed_data)

        return JsonResponse({"message": "Resume parsed and stored successfully!"})

    return JsonResponse({"error": "No file uploaded"}, status=400)

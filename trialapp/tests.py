from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse
import json
from trialapp.views import resume_collection, matched_collection

class ResumeUploadTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        resume_collection.delete_many({})  # Clear existing data before each test
        matched_collection.delete_many({})

    def tearDown(self):
        resume_collection.delete_many({})  # Clean up after tests
        matched_collection.delete_many({})

      
 
    @patch('trialapp.views.default_storage.save')
    @patch('trialapp.views.default_storage.location', '/tmp')
    @patch('trialapp.views.extract_text_from_pdf')
    @patch('trialapp.views.extract_resume_details')
    @patch('trialapp.views.store_resume_in_mongodb')
    @patch('trialapp.views.match_resume_to_jobs')
    def test_upload_and_analyze(
        self,
        mock_match_resume_to_jobs,
        mock_store_resume_in_mongodb,
        mock_extract_resume_details,
        mock_extract_text_from_pdf,
        mock_save
    ):
        mock_save.return_value = 'uploads/test.pdf'
        mock_extract_text_from_pdf.return_value = 'Sample text from PDF'
        mock_extract_resume_details.return_value = {
            'Skills': ['Python', 'Django'],
            'Projects': ['Sample Project'],
            'Experience': ['Developer']
        }
        mock_store_resume_in_mongodb.return_value = '12345'
        mock_match_resume_to_jobs.return_value = [
            {'job_title': 'Software Engineer', 'match_score': 85}
        ]

        with open('/tmp/test.pdf', 'wb') as f:
            f.write(b'%PDF-1.4 sample pdf data')

        with open('/tmp/test.pdf', 'rb') as f:
            response = self.client.post(
                reverse('upload_and_analyze'),
                {'resume': f}
            )

        self.assertEqual(response.status_code, 302)  # Expect redirect to page2
        self.assertEqual(len(self.client.session['matched_jobs']), 1)
        self.assertEqual(self.client.session['matched_jobs'][0]['job_title'], 'Software Engineer')

    @patch('trialapp.views.matched_collection.find_one')
    def test_get_matched_jobs(self, mock_find_one):
        mock_find_one.return_value = {
            "resume_id": "12345",
            "matched_jobs": [
                {'job_title': 'Software Engineer', 'match_score': 90},
                {'job_title': 'Data Scientist', 'match_score': 85}
            ]
        }

        response = self.client.get(reverse('get_matched_jobs'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data['results'][0]['matched_jobs']), 2)
        self.assertEqual(data['results'][0]['matched_jobs'][0]['job_title'], 'Software Engineer')
        self.assertEqual(data['results'][0]['matched_jobs'][1]['job_title'], 'Data Scientist')

    @patch('trialapp.views.matched_collection.find_one')
    def test_get_matched_jobs_no_results(self, mock_find_one):
        mock_find_one.return_value = None

        response = self.client.get(reverse('get_matched_jobs'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 0)

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index1.html')

    def test_page2(self):
        session = self.client.session
        session['matched_jobs'] = [
            {'job_title': 'Software Engineer', 'match_score': 90}
        ]
        session.save()

        response = self.client.get(reverse('page2'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Software Engineer')

def test_upload_resume_page(self):
    with open('/tmp/test.pdf', 'wb') as f:
        f.write(b'%PDF-1.4 sample pdf data')

    with open('/tmp/test.pdf', 'rb') as f:
        response = self.client.post(reverse('upload_resume'), {'resume': f})

    self.assertEqual(response.status_code, 302)  # ✅ Expect redirect to page2


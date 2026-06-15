import axios from 'axios';
import { auth } from './firebase';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Attach Firebase ID Token to every request and inject user_id if needed
api.interceptors.request.use(async (config) => {
  if (auth.currentUser) {
    const token = await auth.currentUser.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
    
    // Auto-inject user_id into POST/PATCH/PUT requests if missing
    if (['post', 'patch', 'put'].includes(config.method)) {
      if (config.data instanceof FormData) {
        if (!config.data.has('user_id')) {
          config.data.append('user_id', auth.currentUser.uid);
        }
      } else {
        if (!config.data) config.data = {};
        if (!config.data.user_id) {
          config.data.user_id = auth.currentUser.uid;
        }
      }
    }
  }
  return config;
}, (error) => Promise.reject(error));

// Resume API
export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/resume/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Jobs API
export const searchJobs = (keywords, location, resumeId) => 
  api.post('/jobs/search', { keywords, location, resume_id: resumeId });

export const tailorResume = (jobId, resumeId) => 
  api.post(`/jobs/${jobId}/tailor`, { resume_id: resumeId });

export const generateCoverLetter = (jobId, resumeId, tone = "formal") => 
  api.post(`/jobs/${jobId}/cover-letter`, { resume_id: resumeId, tone });

// Applications API
export const getApplications = (userId) => 
  api.get(`/applications/${userId}`);

export const updateApplicationStatus = (applicationId, newStatus) => 
  api.patch(`/applications/${applicationId}/status`, { new_status: newStatus });

export const updateApplicationNotes = (applicationId, notes) => 
  api.patch(`/applications/${applicationId}/notes`, { notes });

// Outreach API
export const draftOutreach = (jobId, channel, recruiterName) => 
  api.post('/outreach/draft', { job_id: jobId, channel, recruiter_name: recruiterName });

export const approveOutreach = (applicationId, editedMessage = null) => 
  api.post(`/outreach/${applicationId}/approve`, { edited_message: editedMessage });

// Interview API
export const getInterviewQuestions = (jobId, resumeId) => 
  api.post(`/interview/${jobId}/questions`, { resume_id: resumeId });

export const evaluateMockAnswer = (question, answer, jobTitle, companyName, skill) => 
  api.post('/interview/mock-answer', { 
    question, 
    answer, 
    job_title: jobTitle, 
    company_name: companyName, 
    skill_being_tested: skill 
  });

export default api;

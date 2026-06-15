import React, { useState } from 'react';
import { searchJobs, tailorResume } from '../services/api';
import { Search, MapPin, Loader2, Target, AlertCircle, X, Save } from 'lucide-react';

const JobSearch = () => {
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Panel state
  const [selectedJob, setSelectedJob] = useState(null);
  const [tailoring, setTailoring] = useState(false);
  const [tailoredData, setTailoredData] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!keywords || !location) return;
    setLoading(true);
    setError('');
    try {
      const currentResumeId = localStorage.getItem('resume_id') || "default_resume_id";
      const res = await searchJobs(keywords, location, currentResumeId);
      setJobs(res.data.jobs.sort((a, b) => b.fit_score - a.fit_score));
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Search failed. Please try again.';
      setError(errorMsg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTailor = async (job) => {
    setSelectedJob(job);
    setTailoring(true);
    setTailoredData(null);
    try {
      const currentResumeId = localStorage.getItem('resume_id') || "default_resume_id";
      const res = await tailorResume(job.id || job.job_id, currentResumeId);
      setTailoredData(res.data);
    } catch (err) {
      console.error(err);
      alert('Failed to tailor resume');
    } finally {
      setTailoring(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'bg-green-100 text-green-800';
    if (score >= 45) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6 relative">
      <div className="bg-white shadow rounded-lg p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Find Your Next Role</h2>
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input 
              type="text" 
              placeholder="Job Title or Keywords (e.g., React Developer)" 
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
          <div className="flex-1 relative">
            <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input 
              type="text" 
              placeholder="Location (e.g., Remote, San Francisco)" 
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center min-w-[120px]"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
          <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
          <p className="font-medium">Scraping job boards and scoring matches...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 text-red-700 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" /> {error}
        </div>
      )}

      {!loading && jobs.length > 0 && (
        <div className="space-y-4">
          {jobs.map((job, idx) => (
            <div key={idx} className="bg-white shadow rounded-lg p-6 border border-gray-100 flex flex-col md:flex-row gap-6 hover:shadow-md transition-shadow">
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{job.title}</h3>
                    <p className="text-gray-600 font-medium">{job.company} • {job.location}</p>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mt-1">Source: {job.source}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full font-bold flex items-center ${getScoreColor(job.fit_score)}`}>
                    <Target className="w-4 h-4 mr-1" />
                    {job.fit_score} / 100
                  </div>
                </div>
                
                <p className="mt-4 text-gray-700 text-sm italic border-l-4 border-blue-200 pl-3">
                  "{job.verdict || "Good potential fit based on your profile."}"
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                  {(job.matching_skills || []).slice(0, 5).map(skill => (
                    <span key={skill} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded border border-green-100">
                      ✓ {skill}
                    </span>
                  ))}
                  {(job.missing_skills || []).slice(0, 3).map(skill => (
                    <span key={skill} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded border border-red-100">
                      ✗ {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col justify-center gap-3 border-t md:border-t-0 md:border-l border-gray-100 pt-4 md:pt-0 md:pl-6 min-w-[180px]">
                <button 
                  onClick={() => handleTailor(job)}
                  className="w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition"
                >
                  Tailor Resume
                </button>
                <button className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 text-sm font-medium rounded hover:bg-gray-50 transition">
                  Save to Tracker
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Side Panel for Tailoring */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 overflow-hidden">
          <div className="absolute inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setSelectedJob(null)} />
          <div className="fixed inset-y-0 right-0 max-w-2xl w-full flex">
            <div className="h-full bg-white w-full shadow-xl flex flex-col">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h2 className="text-xl font-bold text-gray-900">Tailoring Resume</h2>
                <button onClick={() => setSelectedJob(null)} className="text-gray-400 hover:text-gray-500">
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-6">
                {tailoring ? (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
                    <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
                    <p className="text-lg">AI is rewriting your resume for {selectedJob.company}...</p>
                  </div>
                ) : tailoredData ? (
                  <div className="space-y-6">
                    <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-900 mb-2">AI Changes Made:</h4>
                      <ul className="list-disc pl-5 space-y-1 text-sm text-blue-800">
                        {tailoredData.changes_made?.map((change, i) => <li key={i}>{change}</li>)}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Tailored Content:</h4>
                      <div className="bg-gray-50 p-4 rounded border border-gray-200 whitespace-pre-wrap text-sm font-mono text-gray-800 h-[400px] overflow-y-auto">
                        {tailoredData.tailored_resume}
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>

              {!tailoring && tailoredData && (
                <div className="p-6 border-t border-gray-200 bg-gray-50 flex justify-end gap-4">
                  <button onClick={() => setSelectedJob(null)} className="px-4 py-2 border border-gray-300 rounded text-gray-700 bg-white hover:bg-gray-50">
                    Cancel
                  </button>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center">
                    <Save className="w-4 h-4 mr-2" /> Approve & Save
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobSearch;

import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { auth } from '../services/firebase';
import { getApplications, uploadResume } from '../services/api';
import { Briefcase, FileText, Search, Clock, CheckCircle, Upload, ArrowRight, Loader2 } from 'lucide-react';

const Dashboard = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const fetchApps = async () => {
      try {
        if (auth.currentUser) {
          const res = await getApplications(auth.currentUser.uid);
          setApplications(res.data.applications || []);
        }
      } catch (err) {
        console.error("Failed to fetch applications", err);
      } finally {
        setLoading(false);
      }
    };
    fetchApps();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    try {
      const res = await uploadResume(file);
      // Save resume_id to local storage so search page can use it
      localStorage.setItem('resume_id', res.data.resume_id);
      alert(`Success! Uploaded ${file.name}. AI found ${res.data.word_count} words and the following sections: ${res.data.detected_sections.join(', ')}`);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to upload resume.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const stats = {
    total: applications.length,
    sent: applications.filter(a => ['applied', 'interviewing', 'offered', 'rejected'].includes(a.status)).length,
    interviews: applications.filter(a => a.status === 'interviewing').length,
    offers: applications.filter(a => a.status === 'offered').length,
  };

  const recentApps = [...applications]
    .sort((a, b) => new Date(b.last_updated || b.created_at) - new Date(a.last_updated || a.created_at))
    .slice(0, 5);

  const getStatusColor = (status) => {
    const colors = {
      discovered: 'bg-gray-100 text-gray-800',
      shortlisted: 'bg-blue-100 text-blue-800',
      resume_tailored: 'bg-purple-100 text-purple-800',
      applied: 'bg-yellow-100 text-yellow-800',
      interviewing: 'bg-orange-100 text-orange-800',
      offered: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {auth.currentUser?.displayName || auth.currentUser?.email?.split('@')[0]}!
        </h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
          <div className="text-gray-500 text-sm font-medium mb-1">Total Jobs Tracked</div>
          <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
          <div className="text-gray-500 text-sm font-medium mb-1">Applications Sent</div>
          <div className="text-3xl font-bold text-blue-600">{stats.sent}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
          <div className="text-gray-500 text-sm font-medium mb-1">Interviews Scheduled</div>
          <div className="text-3xl font-bold text-orange-600">{stats.interviews}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
          <div className="text-gray-500 text-sm font-medium mb-1">Offers Received</div>
          <div className="text-3xl font-bold text-green-600">{stats.offers}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Start */}
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100 lg:col-span-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Start</h2>
          <div className="space-y-3">
            <Link to="/search" className="flex items-center w-full px-4 py-3 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors group">
              <Search className="w-5 h-5 mr-3 text-blue-500" />
              <span className="font-medium">Search New Jobs</span>
              <ArrowRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
            <button 
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors group disabled:opacity-50"
            >
              {uploading ? (
                <Loader2 className="w-5 h-5 mr-3 text-blue-500 animate-spin" />
              ) : (
                <Upload className="w-5 h-5 mr-3 text-gray-500" />
              )}
              <span className="font-medium">{uploading ? 'Parsing with AI...' : 'Upload Master Resume'}</span>
              {!uploading && <ArrowRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />}
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              accept=".pdf,.doc,.docx" 
              className="hidden" 
            />
            <Link to="/applications" className="flex items-center w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors group">
              <Briefcase className="w-5 h-5 mr-3 text-gray-500" />
              <span className="font-medium">View Applications</span>
              <ArrowRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
          </div>
        </div>

        {/* Recent Apps */}
        <div className="bg-white rounded-lg shadow p-6 border border-gray-100 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Applications</h2>
            <Link to="/applications" className="text-sm text-blue-600 hover:text-blue-800 font-medium">View all</Link>
          </div>
          {loading ? (
            <div className="animate-pulse space-y-4">
              {[1,2,3].map(i => <div key={i} className="h-12 bg-gray-100 rounded" />)}
            </div>
          ) : recentApps.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No applications tracked yet. Time to start searching!
            </div>
          ) : (
            <div className="space-y-4">
              {recentApps.map(app => (
                <div key={app.application_id} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-50 rounded-lg mr-4">
                      <Briefcase className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">{app.job_title}</h3>
                      <p className="text-xs text-gray-500">{app.company}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium uppercase tracking-wider ${getStatusColor(app.status)}`}>
                      {app.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

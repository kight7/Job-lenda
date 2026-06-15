import React, { useEffect, useState } from 'react';
import { getApplications, updateApplicationStatus, updateApplicationNotes } from '../services/api';
import { auth } from '../services/firebase';
import { Loader2, FileText, PlusCircle, MessageSquare } from 'lucide-react';

const STATUSES = [
  { id: 'discovered', label: 'Discovered', color: 'bg-gray-100 text-gray-800' },
  { id: 'shortlisted', label: 'Shortlisted', color: 'bg-blue-100 text-blue-800' },
  { id: 'resume_tailored', label: 'Resume Tailored', color: 'bg-purple-100 text-purple-800' },
  { id: 'applied', label: 'Applied', color: 'bg-yellow-100 text-yellow-800' },
  { id: 'interviewing', label: 'Interviewing', color: 'bg-orange-100 text-orange-800' },
  { id: 'offered', label: 'Offered', color: 'bg-green-100 text-green-800' },
  { id: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' }
];

const Applications = () => {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  
  const [noteModal, setNoteModal] = useState({ open: false, appId: null, notes: '' });

  useEffect(() => {
    fetchApps();
  }, []);

  const fetchApps = async () => {
    try {
      if (auth.currentUser) {
        const res = await getApplications(auth.currentUser.uid);
        setApps(res.data.applications || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      // Optimistic update
      setApps(apps.map(a => a.application_id === appId ? { ...a, status: newStatus } : a));
      await updateApplicationStatus(appId, newStatus);
    } catch (err) {
      console.error('Failed to update status', err);
      fetchApps(); // Revert on failure
    }
  };

  const handleSaveNote = async () => {
    try {
      await updateApplicationNotes(noteModal.appId, noteModal.notes);
      setApps(apps.map(a => a.application_id === noteModal.appId ? { ...a, notes: noteModal.notes } : a));
      setNoteModal({ open: false, appId: null, notes: '' });
    } catch (err) {
      console.error('Failed to save note', err);
    }
  };

  const filteredApps = filter === 'ALL' ? apps : apps.filter(a => a.status === filter);

  if (loading) {
    return <div className="flex justify-center py-20"><Loader2 className="w-10 h-10 animate-spin text-blue-600" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Application Tracker</h1>
          <p className="text-gray-500 mt-1">Manage your pipeline and interview process.</p>
        </div>
        
        {/* Filter */}
        <select 
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 py-2 pl-3 pr-10 text-sm bg-white"
        >
          <option value="ALL">All Statuses</option>
          {STATUSES.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
      </div>

      <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job Details</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredApps.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                    No applications found.
                  </td>
                </tr>
              ) : filteredApps.map(app => (
                <tr key={app.application_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-sm font-bold text-gray-900">{app.job_title}</div>
                    <div className="text-sm text-gray-500">{app.company}</div>
                    {app.notes && (
                      <div className="mt-1 flex items-start text-xs text-gray-400">
                        <MessageSquare className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" /> 
                        <span className="truncate max-w-xs">{app.notes}</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={app.status}
                      onChange={(e) => handleStatusChange(app.application_id, e.target.value)}
                      className={`text-xs font-semibold rounded-full px-3 py-1 border-0 cursor-pointer focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${STATUSES.find(s => s.id === app.status)?.color || 'bg-gray-100'}`}
                    >
                      {STATUSES.map(s => <option key={s.id} value={s.id} className="bg-white text-gray-900">{s.label}</option>)}
                    </select>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(app.last_updated || app.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium space-x-3">
                    <button 
                      onClick={() => setNoteModal({ open: true, appId: app.application_id, notes: app.notes || '' })}
                      className="text-gray-400 hover:text-blue-600 transition"
                      title="Add Note"
                    >
                      <PlusCircle className="w-5 h-5 inline" />
                    </button>
                    <button className="text-gray-400 hover:text-blue-600 transition" title="View Full App">
                      <FileText className="w-5 h-5 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Note Modal */}
      {noteModal.open && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Application Notes</h3>
            <textarea
              className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder="Add interview notes, contacts, or thoughts here..."
              value={noteModal.notes}
              onChange={(e) => setNoteModal({ ...noteModal, notes: e.target.value })}
            />
            <div className="mt-4 flex justify-end gap-3">
              <button 
                onClick={() => setNoteModal({ open: false, appId: null, notes: '' })} 
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition"
              >
                Cancel
              </button>
              <button 
                onClick={handleSaveNote} 
                className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
              >
                Save Note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Applications;

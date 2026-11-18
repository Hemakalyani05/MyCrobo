import React, { useEffect, useState } from 'react';
import { X, History, ExternalLink, Calendar, CheckCircle2 } from 'lucide-react';

export default function ScanHistoryModal({ onSelectScan, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/history')
      .then((res) => res.json())
      .then((data) => {
        setHistory(data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 70) return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    if (score >= 50) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-red-400 bg-red-500/10 border-red-500/30';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl p-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <History className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Audit Scan History</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto my-4 space-y-2.5">
          {loading ? (
            <div className="text-center py-8 text-xs text-slate-400">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-400">No past audit scans recorded yet.</div>
          ) : (
            history.map((scan) => (
              <div
                key={scan.scan_id}
                onClick={() => {
                  onSelectScan(scan.scan_id);
                  onClose();
                }}
                className="bg-slate-950/80 hover:bg-slate-900 border border-slate-800/80 hover:border-indigo-500/50 p-4 rounded-xl flex items-center justify-between cursor-pointer transition-all group"
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                      {scan.repo_name}
                    </h4>
                    <span className="text-[10px] font-mono text-slate-500 bg-slate-900 px-1.5 py-0.5 rounded">
                      {scan.source_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-[11px] text-slate-400 mt-1">
                    <span>{scan.created_at}</span>
                    <span>•</span>
                    <span>{scan.total_findings} findings</span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${getScoreColor(scan.security_score)}`}>
                    {scan.security_score} / 100 ({scan.grade})
                  </div>
                  <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-white" />
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

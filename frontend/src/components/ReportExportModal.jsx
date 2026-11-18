import React, { useState } from 'react';
import { X, Download, Copy, Check, FileText, Code2, Globe } from 'lucide-react';

export default function ReportExportModal({ report, onClose }) {
  const [copied, setCopied] = useState(false);
  const scanId = report.scan_id;

  const handleDownload = (format) => {
    window.open(`/api/export/${scanId}?format=${format}`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">Export Audit Report</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-400">
          Download or export the complete security and code quality review report for <strong className="text-slate-200">{report.metadata.repo_name}</strong>.
        </p>

        <div className="space-y-3">
          {/* HTML Standalone Report */}
          <div className="bg-slate-950 border border-slate-800 hover:border-indigo-500/50 p-4 rounded-xl flex items-center justify-between transition-all">
            <div className="flex items-center space-x-3">
              <Globe className="w-5 h-5 text-cyan-400" />
              <div>
                <h4 className="text-sm font-semibold text-white">Standalone Interactive HTML Report</h4>
                <p className="text-xs text-slate-400">Self-contained styled report with metrics, charts & findings</p>
              </div>
            </div>
            <button
              onClick={() => handleDownload('html')}
              className="flex items-center space-x-1 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
            >
              <Download className="w-3.5 h-3.5" />
              <span>HTML</span>
            </button>
          </div>

          {/* Markdown Report */}
          <div className="bg-slate-950 border border-slate-800 hover:border-indigo-500/50 p-4 rounded-xl flex items-center justify-between transition-all">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-indigo-400" />
              <div>
                <h4 className="text-sm font-semibold text-white">GitHub-Flavored Markdown Report</h4>
                <p className="text-xs text-slate-400">Ready to paste into GitHub Issues, PR summaries, or wikis</p>
              </div>
            </div>
            <button
              onClick={() => handleDownload('markdown')}
              className="flex items-center space-x-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Markdown</span>
            </button>
          </div>

          {/* Raw JSON */}
          <div className="bg-slate-950 border border-slate-800 hover:border-indigo-500/50 p-4 rounded-xl flex items-center justify-between transition-all">
            <div className="flex items-center space-x-3">
              <Code2 className="w-5 h-5 text-emerald-400" />
              <div>
                <h4 className="text-sm font-semibold text-white">Machine-Readable JSON</h4>
                <p className="text-xs text-slate-400">Raw structured data for CI/CD pipeline integration</p>
              </div>
            </div>
            <button
              onClick={() => handleDownload('json')}
              className="flex items-center space-x-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
            >
              <Download className="w-3.5 h-3.5" />
              <span>JSON</span>
            </button>
          </div>
        </div>

        <div className="flex justify-end pt-2">
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

import React, { useState } from 'react';
import { ShieldAlert, Sparkles, AlertCircle, CheckCircle2, ChevronRight, X, Copy, Check, Wrench, Search, Filter } from 'lucide-react';

export default function FindingsExplorer({ findings, scanId, onApplyPatch }) {
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedPatch, setCopiedPatch] = useState(false);
  const [applying, setApplying] = useState(false);
  const [patchSuccess, setPatchSuccess] = useState(false);

  // Filter findings
  const filtered = findings.filter((f) => {
    if (categoryFilter !== 'all' && f.category !== categoryFilter) return false;
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const match =
        f.title.toLowerCase().includes(q) ||
        f.file_path.toLowerCase().includes(q) ||
        f.explanation.toLowerCase().includes(q) ||
        (f.cwe_id && f.cwe_id.toLowerCase().includes(q));
      if (!match) return false;
    }
    return true;
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'critical':
        return 'bg-red-500/15 text-red-400 border-red-500/30';
      case 'high':
        return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
      case 'medium':
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      default:
        return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
    }
  };

  const getCategoryBadge = (cat) => {
    switch (cat) {
      case 'security':
        return 'bg-red-950/60 text-red-300 border-red-800/40';
      case 'slop':
        return 'bg-purple-950/60 text-purple-300 border-purple-800/40';
      case 'gaps':
        return 'bg-cyan-950/60 text-cyan-300 border-cyan-800/40';
      case 'loose_ends':
        return 'bg-amber-950/60 text-amber-300 border-amber-800/40';
      default:
        return 'bg-emerald-950/60 text-emerald-300 border-emerald-800/40';
    }
  };

  const handleCopyDiff = (patch) => {
    navigator.clipboard.writeText(patch);
    setCopiedPatch(true);
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  const handleApplyFix = async (finding) => {
    if (!finding.diff_patch) return;
    setApplying(true);
    try {
      const res = await fetch('/api/patch/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: finding.file_path,
          diff_patch: finding.diff_patch,
          scan_id: scanId
        })
      });
      if (res.ok) {
        setPatchSuccess(true);
        if (onApplyPatch) onApplyPatch(finding);
        setTimeout(() => setPatchSuccess(false), 3000);
      } else {
        alert("Patch could not be applied automatically. You can copy the diff patch manually.");
      }
    } catch (err) {
      alert("Error applying patch: " + err.message);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Audit Findings & AI Remediation</h2>
          <p className="text-xs text-slate-400 mt-1">
            Showing {filtered.length} of {findings.length} findings across security, slop, gaps, and dependencies.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search findings or files..."
            className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-200 outline-none"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6 bg-slate-900/60 p-2 rounded-xl border border-slate-800">
        {/* Category Tabs */}
        <div className="flex flex-wrap gap-1">
          {['all', 'security', 'slop', 'gaps', 'loose_ends', 'dependencies'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                categoryFilter === cat
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>

        {/* Severity Pills */}
        <div className="flex items-center space-x-1.5">
          <span className="text-[11px] text-slate-500 mr-1 flex items-center space-x-1">
            <Filter className="w-3 h-3" />
            <span>Severity:</span>
          </span>
          {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium uppercase border ${
                severityFilter === sev
                  ? 'border-indigo-400 bg-indigo-500/20 text-white'
                  : 'border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="text-center py-12 bg-slate-900/40 rounded-2xl border border-slate-800">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-200">No findings match this filter</p>
            <p className="text-xs text-slate-400 mt-1">Try relaxing your search terms or filters.</p>
          </div>
        ) : (
          filtered.map((f) => (
            <div
              key={f.id}
              onClick={() => setSelectedFinding(f)}
              className="bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/50 rounded-xl p-4.5 cursor-pointer transition-all flex items-start justify-between gap-4 group"
            >
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getSeverityBadge(f.severity)}`}>
                    {f.severity}
                  </span>
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded border uppercase tracking-wider ${getCategoryBadge(f.category)}`}>
                    {f.category.replace('_', ' ')}
                  </span>
                  {f.cwe_id && (
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
                      {f.cwe_id}
                    </span>
                  )}
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                  {f.title}
                </h3>

                <p className="text-xs text-slate-400 line-clamp-2">
                  {f.explanation}
                </p>

                <div className="flex items-center space-x-3 text-[11px] text-slate-500 font-mono pt-1">
                  <span>📍 {f.file_path}:{f.line_number}</span>
                  {f.diff_patch && (
                    <span className="text-emerald-400 flex items-center space-x-1">
                      <Sparkles className="w-3 h-3" />
                      <span>AI Patch Available</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="self-center">
                <div className="w-8 h-8 rounded-lg bg-slate-950 flex items-center justify-center text-slate-400 group-hover:text-white group-hover:bg-indigo-600 transition-all">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Modal / Drawer */}
      {selectedFinding && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
            {/* Modal Header */}
            <div className="sticky top-0 z-10 px-6 py-4 bg-slate-950/90 backdrop-blur border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getSeverityBadge(selectedFinding.severity)}`}>
                  {selectedFinding.severity}
                </span>
                <span className={`text-[10px] font-medium px-2 py-0.5 rounded border uppercase ${getCategoryBadge(selectedFinding.category)}`}>
                  {selectedFinding.category.replace('_', ' ')}
                </span>
                {selectedFinding.cwe_id && (
                  <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    {selectedFinding.cwe_id}
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedFinding(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              <div>
                <h2 className="text-lg font-bold text-white">{selectedFinding.title}</h2>
                <p className="text-xs text-indigo-400 font-mono mt-1">
                  Location: {selectedFinding.file_path}:{selectedFinding.line_number}
                </p>
              </div>

              {/* Explanation & Evidence */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Vulnerability Explanation</h4>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
                  {selectedFinding.explanation}
                </p>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Detected Evidence</h4>
                <p className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                  {selectedFinding.evidence}
                </p>
              </div>

              {/* Code Snippet */}
              {selectedFinding.snippet && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Source Code Context</h4>
                  <pre className="bg-[#050811] text-indigo-200 p-4 rounded-xl text-xs font-mono overflow-x-auto border border-slate-800">
                    <code>{selectedFinding.snippet}</code>
                  </pre>
                </div>
              )}

              {/* Remediation Guidance */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Remediation Steps</h4>
                <p className="text-xs text-slate-300 bg-indigo-950/20 border border-indigo-500/20 p-4 rounded-xl">
                  {selectedFinding.remediation}
                </p>
              </div>

              {/* Unified Diff Patch */}
              {selectedFinding.diff_patch && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center space-x-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Synthesized AI Diff Patch</span>
                    </h4>
                    <button
                      onClick={() => handleCopyDiff(selectedFinding.diff_patch)}
                      className="text-xs flex items-center space-x-1 text-slate-400 hover:text-white"
                    >
                      {copiedPatch ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedPatch ? 'Copied' : 'Copy Diff'}</span>
                    </button>
                  </div>

                  <pre className="bg-[#02050e] text-xs font-mono p-4 rounded-xl overflow-x-auto border border-slate-800">
                    {selectedFinding.diff_patch.split('\n').map((line, idx) => {
                      let color = 'text-slate-400';
                      if (line.startsWith('+') && !line.startsWith('+++')) color = 'text-emerald-400 bg-emerald-950/20';
                      if (line.startsWith('-') && !line.startsWith('---')) color = 'text-red-400 bg-red-950/20';
                      if (line.startsWith('@@')) color = 'text-cyan-400';
                      return (
                        <div key={idx} className={`${color} px-1 rounded`}>
                          {line}
                        </div>
                      );
                    })}
                  </pre>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 px-6 py-4 bg-slate-950/90 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-400">
                Confidence: <strong className="text-white">{Math.round(selectedFinding.confidence * 100)}%</strong>
              </span>

              <div className="flex items-center space-x-3">
                {selectedFinding.diff_patch && (
                  <button
                    disabled={applying}
                    onClick={() => handleApplyFix(selectedFinding)}
                    className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-50"
                  >
                    {patchSuccess ? (
                      <>
                        <Check className="w-3.5 h-3.5" />
                        <span>Patch Applied to File!</span>
                      </>
                    ) : (
                      <>
                        <Wrench className="w-3.5 h-3.5" />
                        <span>{applying ? 'Applying...' : 'Apply Fix to File'}</span>
                      </>
                    )}
                  </button>
                )}

                <button
                  onClick={() => setSelectedFinding(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

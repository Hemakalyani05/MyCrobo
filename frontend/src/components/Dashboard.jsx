import React from 'react';
import { Shield, ShieldAlert, Cpu, Sparkles, AlertTriangle, Layers, FileCode, CheckCircle, Clock } from 'lucide-react';

export default function Dashboard({ report }) {
  if (!report) return null;

  const { summary, metadata, agent_analysis, duration_seconds } = report;

  // Grade color mapping
  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A+':
      case 'A':
        return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
      case 'B':
        return 'text-blue-400 border-blue-500/40 bg-blue-500/10';
      case 'C':
        return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
      case 'D':
        return 'text-orange-400 border-orange-500/40 bg-orange-500/10';
      default:
        return 'text-red-400 border-red-500/40 bg-red-500/10';
    }
  };

  const getScoreStroke = (score) => {
    if (score >= 85) return '#10b981';
    if (score >= 70) return '#3b82f6';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Security Score Card */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Security Score</span>
            <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getGradeColor(summary.grade)}`}>
              Grade {summary.grade}
            </span>
          </div>

          <div className="flex items-center justify-center my-6">
            <div className="relative w-40 h-40 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke="#1e293b"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke={getScoreStroke(summary.security_score)}
                  strokeWidth="8"
                  strokeDasharray="264"
                  strokeDashoffset={264 - (264 * summary.security_score) / 100}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center text-center">
                <span className="text-4xl font-extrabold text-white tracking-tight">{summary.security_score}</span>
                <span className="text-[11px] text-slate-400 font-medium">/ 100</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800">
            <span>Target: <strong className="text-slate-200">{metadata.repo_name}</strong></span>
            <span>Duration: <strong className="text-slate-200">{duration_seconds}s</strong></span>
          </div>
        </div>

        {/* Severities & Categories Breakdown */}
        <div className="lg:col-span-8 space-y-6">
          {/* Severity Counters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <span className="text-[11px] font-semibold text-red-400 uppercase tracking-wider">Critical</span>
              <div className="text-2xl font-bold text-red-300 mt-1">{summary.by_severity.critical || 0}</div>
              <span className="text-[10px] text-slate-400">Immediate action required</span>
            </div>
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4">
              <span className="text-[11px] font-semibold text-orange-400 uppercase tracking-wider">High</span>
              <div className="text-2xl font-bold text-orange-300 mt-1">{summary.by_severity.high || 0}</div>
              <span className="text-[10px] text-slate-400">Severe exploit risks</span>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
              <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">Medium</span>
              <div className="text-2xl font-bold text-amber-300 mt-1">{summary.by_severity.medium || 0}</div>
              <span className="text-[10px] text-slate-400">Quality & design flaws</span>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
              <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider">Low / Info</span>
              <div className="text-2xl font-bold text-blue-300 mt-1">{(summary.by_severity.low || 0) + (summary.by_severity.info || 0)}</div>
              <span className="text-[10px] text-slate-400">Tech debt & hygiene</span>
            </div>
          </div>

          {/* Category Counters */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">Audit Disciplines</h4>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[11px] text-slate-400">Security</span>
                <div className="text-lg font-bold text-white mt-0.5">{summary.by_category.security || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[11px] text-slate-400">AI Slop</span>
                <div className="text-lg font-bold text-purple-300 mt-0.5">{summary.by_category.slop || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[11px] text-slate-400">Coding Gaps</span>
                <div className="text-lg font-bold text-cyan-300 mt-0.5">{summary.by_category.gaps || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[11px] text-slate-400">Loose Ends</span>
                <div className="text-lg font-bold text-amber-300 mt-0.5">{summary.by_category.loose_ends || 0}</div>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <span className="text-[11px] text-slate-400">Dependencies</span>
                <div className="text-lg font-bold text-emerald-300 mt-0.5">{summary.by_category.dependencies || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Architecture & AI Analysis Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Architecture & Tech Stack Card */}
        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center space-x-2 mb-4">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">Architecture & Technology Stack</h3>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Source Files: <strong className="text-slate-200">{metadata.total_files}</strong></span>
                <span>Lines of Code: <strong className="text-slate-200">{metadata.total_lines}</strong></span>
              </div>
            </div>

            {/* Language Bar */}
            <div>
              <span className="text-[11px] text-slate-400 block mb-1.5 font-medium">Language Breakdown</span>
              <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden flex">
                {metadata.languages.map((l, idx) => {
                  const colors = ['bg-indigo-500', 'bg-cyan-400', 'bg-amber-400', 'bg-purple-500', 'bg-emerald-400'];
                  return (
                    <div
                      key={l.language}
                      title={`${l.language}: ${l.percentage}%`}
                      style={{ width: `${l.percentage}%` }}
                      className={`${colors[idx % colors.length]}`}
                    />
                  );
                })}
              </div>
              <div className="mt-2.5 flex flex-wrap gap-2">
                {metadata.languages.map((l) => (
                  <span key={l.language} className="text-[11px] bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-slate-300">
                    {l.language}: <strong className="text-white">{l.percentage}%</strong> ({l.lines_count} lines)
                  </span>
                ))}
              </div>
            </div>

            {/* Frameworks */}
            <div>
              <span className="text-[11px] text-slate-400 block mb-1.5 font-medium">Detected Frameworks & Libraries</span>
              <div className="flex flex-wrap gap-1.5">
                {metadata.frameworks.length > 0 ? (
                  metadata.frameworks.map((fw) => (
                    <span key={fw} className="text-xs bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-0.5 rounded-full font-medium">
                      {fw}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 italic">Generic architecture (No standard framework markers)</span>
                )}
              </div>
            </div>

            {/* Manifests */}
            <div>
              <span className="text-[11px] text-slate-400 block mb-1.5 font-medium">Package Manifests Parsed</span>
              <div className="flex flex-wrap gap-1.5">
                {metadata.manifests.map((m) => (
                  <span key={m} className="text-[11px] bg-slate-950 text-slate-400 px-2 py-0.5 rounded font-mono border border-slate-800">
                    {m}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* AI Agent Executive Analysis */}
        <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-semibold text-white">AI Agent Executive Assessment</h3>
            </div>
            <div className="bg-[#070b14] border border-slate-800/80 rounded-xl p-4 text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-line">
              {agent_analysis}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>False Positives Filtered: <strong className="text-emerald-400">{summary.false_positives_filtered}</strong></span>
            <span>Remediation Patches Generated: <strong className="text-cyan-400">{report.findings.filter(f => f.diff_patch).length}</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}

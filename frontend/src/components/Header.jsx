import React from 'react';
import { ShieldAlert, Settings, History, Sparkles, Terminal, FileText } from 'lucide-react';

export default function Header({ onOpenSettings, onOpenHistory, onReset, activeReport, onExportReport }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-30 px-6 py-3.5 flex items-center justify-between">
      <div className="flex items-center space-x-3 cursor-pointer" onClick={onReset}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
          <div className="w-full h-full bg-[#0a0f1d] rounded-[10px] flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg text-white tracking-tight">CodeSentinel</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">AI Agent</span>
          </div>
          <p className="text-xs text-slate-400">Architecture-Agnostic Code Security & Quality Auditor</p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {activeReport && (
          <button
            onClick={onExportReport}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 transition-all hover:text-white"
          >
            <FileText className="w-3.5 h-3.5 text-indigo-400" />
            <span>Export Report</span>
          </button>
        )}

        <button
          onClick={onOpenHistory}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 transition-all hover:text-white"
        >
          <History className="w-3.5 h-3.5 text-cyan-400" />
          <span>Audit History</span>
        </button>

        <button
          onClick={onOpenSettings}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 transition-all hover:text-white"
        >
          <Settings className="w-3.5 h-3.5 text-slate-400" />
          <span>AI Provider Settings</span>
        </button>
      </div>
    </header>
  );
}

import React, { useEffect, useRef } from 'react';
import { Terminal, Shield, Sparkles, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export default function LiveProgressTerminal({ logs, currentStage, progressPercent, isScanning }) {
  const terminalEndRef = useRef(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="max-w-5xl mx-auto my-8 px-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Terminal Header */}
        <div className="px-5 py-3 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-green-500/80"></div>
            </div>
            <div className="flex items-center space-x-2 pl-3">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-xs font-mono font-medium text-slate-300">CodeSentinel Agent Telemetry</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-mono text-indigo-400 font-semibold">{progressPercent}%</span>
            {isScanning ? (
              <span className="flex items-center space-x-1 text-[11px] text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Running</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3" />
                <span>Completed</span>
              </span>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-950 h-1.5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Current Stage Indicator */}
        <div className="px-5 py-2.5 bg-slate-900/60 border-b border-slate-800/60 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
            <span className="text-slate-400">Current Phase:</span>
            <span className="text-slate-200 font-medium">{currentStage || "Preparing scan..."}</span>
          </div>
        </div>

        {/* Log Output */}
        <div className="p-5 font-mono text-xs max-h-64 overflow-y-auto space-y-1.5 bg-[#070b14]">
          {logs.map((log, idx) => (
            <div key={idx} className="flex items-start space-x-2">
              <span className="text-slate-600 select-none">›</span>
              <span className="text-indigo-400/80 font-medium">[{log.stage}]</span>
              <span className="text-slate-300">{log.message}</span>
            </div>
          ))}
          <div ref={terminalEndRef} />
        </div>
      </div>
    </div>
  );
}

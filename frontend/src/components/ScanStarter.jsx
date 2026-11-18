import React, { useState } from 'react';
import { Play, Folder, Github, Code2, Sparkles, AlertTriangle, Cpu, Layers } from 'lucide-react';

export default function ScanStarter({ onStartScan, isScanning }) {
  const [activeTab, setActiveTab] = useState('samples');
  const [localPath, setLocalPath] = useState('/Users/jnavyagowthami/MyCrobo/sample_repos/vulnerable-python');
  const [githubUrl, setGithubUrl] = useState('');
  const [snippetCode, setSnippetCode] = useState(`import os
import sqlite3

def get_user_data(username):
    # set query string
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    # SQL Injection risk
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    # TODO: Add authentication checks
    return cursor.fetchall()
`);
  const [snippetLang, setSnippetLang] = useState('python');

  const sampleRepos = [
    {
      id: 'vulnerable-python',
      name: 'Python Microservice',
      stack: 'FastAPI + SQLite + PyPI',
      badgeColor: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
      description: 'SQL injection, exposed AWS access keys, swallowed exceptions, echo comments & vulnerable requests.',
      flaws: ['SQL Injection', 'Hardcoded AWS Keys', 'Empty Except: Pass', 'CVE-2023-32681']
    },
    {
      id: 'vulnerable-node',
      name: 'Node.js Express App',
      stack: 'Express + ChildProcess + npm',
      badgeColor: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
      description: 'OS command injection via exec, reflected XSS, empty catch blocks & vulnerable lodash prototype pollution.',
      flaws: ['Command Injection', 'Reflected XSS', 'Empty Catch {}', 'CVE-2020-8203']
    },
    {
      id: 'vulnerable-go',
      name: 'Go Web Service',
      stack: 'Go + Gin Framework',
      badgeColor: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400',
      description: 'Hardcoded API tokens, Sprintf SQL injection, ignored error return values & unfinished database stubs.',
      flaws: ['Hardcoded Tokens', 'Sprintf SQL Injection', 'Ignored Go Errors', 'CWE-391']
    }
  ];

  const handleStartSample = (sampleId) => {
    onStartScan({
      source_type: 'sample',
      target: sampleId
    });
  };

  const handleStartLocal = (e) => {
    e.preventDefault();
    if (!localPath.trim()) return;
    onStartScan({
      source_type: 'local',
      target: localPath.trim()
    });
  };

  const handleStartGithub = (e) => {
    e.preventDefault();
    if (!githubUrl.trim()) return;
    onStartScan({
      source_type: 'github',
      target: githubUrl.trim()
    });
  };

  const handleStartSnippet = (e) => {
    e.preventDefault();
    if (!snippetCode.trim()) return;
    onStartScan({
      source_type: 'snippet',
      target: snippetCode,
      language: snippetLang
    });
  };

  return (
    <div className="max-w-5xl mx-auto py-10 px-6">
      <div className="text-center mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Gen Architecture-Agnostic Code Auditor</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Audit Code Security, Slop & Implementation Gaps
        </h1>
        <p className="mt-3 text-slate-400 text-sm max-w-2xl mx-auto">
          Autonomous AI agent combining deterministic AST pattern analysis with deep reasoning to eliminate false positives, surface hidden vulnerabilities, and generate instant unified diff patches.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center mb-6">
        <div className="flex p-1 bg-slate-900 border border-slate-800 rounded-xl space-x-1">
          <button
            onClick={() => setActiveTab('samples')}
            className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'samples'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>1-Click Benchmark Demos</span>
          </button>
          <button
            onClick={() => setActiveTab('local')}
            className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'local'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Folder className="w-3.5 h-3.5" />
            <span>Local Directory</span>
          </button>
          <button
            onClick={() => setActiveTab('github')}
            className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'github'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Github className="w-3.5 h-3.5" />
            <span>GitHub Repository</span>
          </button>
          <button
            onClick={() => setActiveTab('snippet')}
            className={`flex items-center space-x-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'snippet'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Paste Snippet</span>
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl backdrop-blur-xl">
        {activeTab === 'samples' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Pre-Loaded Multi-Stack Benchmark Repositories</h3>
                <p className="text-xs text-slate-400">Instantly launch an autonomous audit against real multi-language vulnerabilities and AI slop.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {sampleRepos.map((repo) => (
                <div
                  key={repo.id}
                  className="bg-slate-950/60 border border-slate-800 hover:border-indigo-500/50 rounded-xl p-5 flex flex-col justify-between transition-all hover:shadow-xl hover:shadow-indigo-500/10 group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-[11px] font-medium px-2 py-0.5 rounded border ${repo.badgeColor}`}>
                        {repo.stack}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-white group-hover:text-indigo-300 transition-colors">
                      {repo.name}
                    </h4>
                    <p className="text-xs text-slate-400 mt-2 line-clamp-2">
                      {repo.description}
                    </p>

                    <div className="mt-4 flex flex-wrap gap-1.5">
                      {repo.flaws.map((flaw, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-800/80 text-slate-300 px-2 py-0.5 rounded border border-slate-700/50">
                          {flaw}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button
                    disabled={isScanning}
                    onClick={() => handleStartSample(repo.id)}
                    className="mt-5 w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run AI Audit</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'local' && (
          <form onSubmit={handleStartLocal} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Absolute Local Workspace Directory Path
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={localPath}
                  onChange={(e) => setLocalPath(e.target.value)}
                  placeholder="/Users/username/projects/my-app"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-slate-200 outline-none transition-all pr-24 font-mono"
                />
                <button
                  type="submit"
                  disabled={isScanning}
                  className="absolute right-1.5 top-1.5 bottom-1.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Start Audit</span>
                </button>
              </div>
            </div>

            <div className="pt-2">
              <span className="text-xs text-slate-400 mr-2">Quick presets:</span>
              <button
                type="button"
                onClick={() => setLocalPath('/Users/jnavyagowthami/MyCrobo/sample_repos/vulnerable-python')}
                className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md mr-2"
              >
                sample_repos/vulnerable-python
              </button>
              <button
                type="button"
                onClick={() => setLocalPath('/Users/jnavyagowthami/MyCrobo/sample_repos/vulnerable-node')}
                className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md mr-2"
              >
                sample_repos/vulnerable-node
              </button>
              <button
                type="button"
                onClick={() => setLocalPath('/Users/jnavyagowthami/MyCrobo/sample_repos/vulnerable-go')}
                className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md"
              >
                sample_repos/vulnerable-go
              </button>
            </div>
          </form>
        )}

        {activeTab === 'github' && (
          <form onSubmit={handleStartGithub} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Public GitHub Repository URL
              </label>
              <div className="relative">
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/org/repository"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-slate-200 outline-none transition-all pr-24 font-mono"
                />
                <button
                  type="submit"
                  disabled={isScanning || !githubUrl.trim()}
                  className="absolute right-1.5 top-1.5 bottom-1.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Clone & Audit</span>
                </button>
              </div>
              <p className="text-[11px] text-slate-400 mt-2">
                Clones shallow repository (<code className="text-slate-300">--depth 1</code>), performs auto-detection of languages & frameworks, and executes full agent scan.
              </p>
            </div>
          </form>
        )}

        {activeTab === 'snippet' && (
          <form onSubmit={handleStartSnippet} className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">Code Snippet Sandbox</label>
              <select
                value={snippetLang}
                onChange={(e) => setSnippetLang(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1 outline-none"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="go">Go</option>
                <option value="java">Java</option>
                <option value="rust">Rust</option>
              </select>
            </div>

            <textarea
              rows={8}
              value={snippetCode}
              onChange={(e) => setSnippetCode(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl p-3 text-xs font-mono text-slate-200 outline-none resize-none"
            />

            <button
              type="submit"
              disabled={isScanning || !snippetCode.trim()}
              className="w-full flex items-center justify-center space-x-2 py-2 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Audit Snippet</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

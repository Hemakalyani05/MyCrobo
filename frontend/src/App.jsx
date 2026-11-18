import React, { useState, useEffect } from 'react';
import Header from './components/Header.jsx';
import ScanStarter from './components/ScanStarter.jsx';
import LiveProgressTerminal from './components/LiveProgressTerminal.jsx';
import Dashboard from './components/Dashboard.jsx';
import FindingsExplorer from './components/FindingsExplorer.jsx';
import SettingsModal from './components/SettingsModal.jsx';
import ScanHistoryModal from './components/ScanHistoryModal.jsx';
import ReportExportModal from './components/ReportExportModal.jsx';

export default function App() {
  const [report, setReport] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [currentStage, setCurrentStage] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [logs, setLogs] = useState([]);
  
  // Modals
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showExport, setShowExport] = useState(false);

  // AI settings
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('codesentinel_settings');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return {
      ai_model: 'heuristic',
      gemini_api_key: '',
      openai_api_key: '',
      ollama_url: 'http://localhost:11434',
      verify_with_ai: true
    };
  });

  const handleSaveSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('codesentinel_settings', JSON.stringify(newSettings));
  };

  const handleStartScan = async (scanReq) => {
    setIsScanning(true);
    setReport(null);
    setProgressPercent(0);
    setCurrentStage('Initializing Agent Engine');
    setLogs([]);

    const payload = {
      ...scanReq,
      ai_model: settings.ai_model,
      gemini_api_key: settings.gemini_api_key,
      openai_api_key: settings.openai_api_key,
      ollama_url: settings.ollama_url,
      verify_with_ai: settings.verify_with_ai
    };

    try {
      const response = await fetch('/api/scan/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // keep remainder

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.replace('data: ', ''));
              
              if (event.stage) setCurrentStage(event.stage);
              if (typeof event.progress_percent === 'number') {
                setProgressPercent(event.progress_percent);
              }

              if (event.message) {
                setLogs((prev) => [...prev, { stage: event.stage, message: event.message }]);
              }

              if (event.type === 'complete' && event.data?.report) {
                setReport(event.data.report);
                setIsScanning(false);
              } else if (event.type === 'error') {
                alert("Scan Error: " + event.message);
                setIsScanning(false);
              }
            } catch (err) {
              console.error("SSE parse error", err);
            }
          }
        }
      }
    } catch (error) {
      alert("Failed to communicate with CodeSentinel backend: " + error.message);
      setIsScanning(false);
    }
  };

  const handleSelectHistoricalScan = async (scanId) => {
    try {
      const res = await fetch(`/api/scan/${scanId}`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        setLogs([]);
        setProgressPercent(100);
      }
    } catch (e) {
      alert("Error fetching report: " + e.message);
    }
  };

  const handleReset = () => {
    setReport(null);
    setIsScanning(false);
    setLogs([]);
    setProgressPercent(0);
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans">
      <Header
        onOpenSettings={() => setShowSettings(true)}
        onOpenHistory={() => setShowHistory(true)}
        onReset={handleReset}
        activeReport={report}
        onExportReport={() => setShowExport(true)}
      />

      <main className="flex-1 pb-16">
        {/* If no active report and not scanning, show starter */}
        {!report && !isScanning && (
          <ScanStarter onStartScan={handleStartScan} isScanning={isScanning} />
        )}

        {/* Live terminal shown when scanning or when logs exist */}
        {(isScanning || (logs.length > 0 && !report)) && (
          <LiveProgressTerminal
            logs={logs}
            currentStage={currentStage}
            progressPercent={progressPercent}
            isScanning={isScanning}
          />
        )}

        {/* Active Audit Report Dashboard and Findings */}
        {report && (
          <div className="space-y-6 animate-fadeIn">
            <Dashboard report={report} />
            <FindingsExplorer findings={report.findings} scanId={report.scan_id} />
          </div>
        )}
      </main>

      {/* Modals */}
      {showSettings && (
        <SettingsModal
          settings={settings}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}

      {showHistory && (
        <ScanHistoryModal
          onSelectScan={handleSelectHistoricalScan}
          onClose={() => setShowHistory(false)}
        />
      )}

      {showExport && report && (
        <ReportExportModal
          report={report}
          onClose={() => setShowExport(false)}
        />
      )}
    </div>
  );
}

import React, { useState } from 'react';
import { X, Key, Cpu, Sparkles, Check } from 'lucide-react';

export default function SettingsModal({ settings, onSave, onClose }) {
  const [form, setForm] = useState({
    ai_model: settings.ai_model || 'heuristic',
    gemini_api_key: settings.gemini_api_key || '',
    openai_api_key: settings.openai_api_key || '',
    ollama_url: settings.ollama_url || 'http://localhost:11434',
    verify_with_ai: settings.verify_with_ai !== false
  });
  const [saved, setSaved] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">AI Provider Configuration</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Reasoning Engine Mode
            </label>
            <select
              value={form.ai_model}
              onChange={(e) => setForm({ ...form, ai_model: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 outline-none"
            >
              <option value="heuristic">Built-in Expert Heuristic (Zero Config / Offline Mode)</option>
              <option value="gemini">Google Gemini 2.5 Flash (via API Key)</option>
              <option value="openai">OpenAI GPT-4o-mini (via API Key)</option>
              <option value="ollama">Local Ollama (CodeLlama / Mistral)</option>
            </select>
            <p className="text-[11px] text-slate-400 mt-1">
              {form.ai_model === 'heuristic' && "⚡ High-speed deterministic rules and contextual heuristics. Runs 100% offline with 0 API keys!"}
              {form.ai_model === 'gemini' && "✨ Uses Google Generative AI API for ultra-fast deep semantic verification."}
              {form.ai_model === 'openai' && "🧠 Uses OpenAI GPT-4o-mini for code reasoning and remediation."}
              {form.ai_model === 'ollama' && "🖥️ Uses self-hosted Ollama model for private local AI auditing."}
            </p>
          </div>

          {form.ai_model === 'gemini' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Gemini API Key
              </label>
              <input
                type="password"
                value={form.gemini_api_key}
                onChange={(e) => setForm({ ...form, gemini_api_key: e.target.value })}
                placeholder="AIzaSy..."
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono outline-none"
              />
            </div>
          )}

          {form.ai_model === 'openai' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                OpenAI API Key
              </label>
              <input
                type="password"
                value={form.openai_api_key}
                onChange={(e) => setForm({ ...form, openai_api_key: e.target.value })}
                placeholder="sk-proj-..."
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono outline-none"
              />
            </div>
          )}

          {form.ai_model === 'ollama' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Ollama Endpoint URL
              </label>
              <input
                type="text"
                value={form.ollama_url}
                onChange={(e) => setForm({ ...form, ollama_url: e.target.value })}
                placeholder="http://localhost:11434"
                className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono outline-none"
              />
            </div>
          )}

          <div className="flex items-center space-x-2 pt-2">
            <input
              type="checkbox"
              id="verify"
              checked={form.verify_with_ai}
              onChange={(e) => setForm({ ...form, verify_with_ai: e.target.checked })}
              className="rounded border-slate-800 text-indigo-600 focus:ring-0 bg-slate-950"
            />
            <label htmlFor="verify" className="text-xs text-slate-300 select-none">
              Enable False-Positive Reduction & Diff Patch Synthesis
            </label>
          </div>

          <div className="flex justify-end space-x-2 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5"
            >
              {saved ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-300" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Settings</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

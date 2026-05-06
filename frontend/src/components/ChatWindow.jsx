import { useState, useRef, useEffect } from 'react';
import api from '../services/api';

export default function ChatWindow({ fileId, onSeek }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState('');
  
  const messagesEndRef = useRef(null);

  // Clear messages when file selection changes, or load custom greetings
  useEffect(() => {
    setMessages([]);
    setSummary('');
    setError('');
    if (fileId) {
      setMessages([
        {
          sender: 'assistant',
          text: "I've loaded and indexed your document! Ask me anything about its content, or click 'Generate Summary' to see a quick recap.",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [fileId]);

  // Autoscroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || !fileId || isLoading) return;

    const userMessage = {
      sender: 'user',
      text: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      const response = await api.post('/chat', {
        query: userMessage.text,
        file_id: fileId
      });

      const { answer, sources, timestamps } = response.data;

      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: answer,
          sources: sources || [],
          timestamps: timestamps || [],
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (err) {
      console.error('Chat processing failed:', err);
      const detail = err.response?.data?.detail || 'Failed to retrieve answer from agent.';
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!fileId || isSummarizing) return;

    setIsSummarizing(true);
    setError('');
    
    try {
      const response = await api.post('/summarize', {
        file_id: fileId
      });
      setSummary(response.data.summary);
      
      // Also append summary to the chat log
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `**Document Summary:**\n\n${response.data.summary}`,
          timestamp: new Date().toISOString(),
          isSummary: true
        }
      ]);
    } catch (err) {
      console.error('Summarize failed:', err);
      const detail = err.response?.data?.detail || 'Failed to generate document summary.';
      setError(detail);
    } finally {
      setIsSummarizing(false);
    }
  };

  const formatTime = (seconds) => {
    if (seconds === null || seconds === undefined) return '';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col h-[600px] bg-slate-900/30 border border-slate-900 rounded-3xl overflow-hidden shadow-2xl">
      {/* Header Panel */}
      <div className="bg-slate-900/60 border-b border-slate-900 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3 text-left">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <div>
            <h3 className="font-bold text-slate-200 text-sm">AI Assistant</h3>
            <p className="text-slate-500 text-xs mt-0.5">RAG Query Agent Enabled</p>
          </div>
        </div>
        
        {fileId && (
          <button
            onClick={handleGenerateSummary}
            disabled={isSummarizing}
            className={`text-xs px-3 py-1.5 rounded-lg border font-bold flex items-center space-x-1.5 transition-all duration-300 ${
              isSummarizing
                ? 'bg-violet-500/10 border-violet-500/20 text-violet-400 pointer-events-none'
                : 'bg-slate-850 border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 hover:bg-slate-800'
            }`}
          >
            {isSummarizing ? (
              <>
                <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-violet-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Summarizing...</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Generate Summary</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar">
        {fileId ? (
          <>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${
                  msg.sender === 'user' ? 'items-end' : 'items-start'
                } space-y-1.5 animate-fadeIn`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm text-left leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-violet-600 text-white rounded-tr-none shadow-md shadow-violet-600/10'
                      : 'bg-slate-800/60 border border-slate-700/40 text-slate-100 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                  
                  {/* Embedded Whisper Timestamps chips */}
                  {msg.sender === 'assistant' && msg.timestamps && msg.timestamps.length > 0 && (
                    <div className="mt-3.5 pt-2.5 border-t border-slate-700/50">
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wide">
                        Relevant Media Segments
                      </p>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {msg.timestamps.map((ts, tIdx) => (
                          <button
                            key={tIdx}
                            onClick={() => onSeek && onSeek(ts.start)}
                            className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 hover:bg-violet-600 hover:text-white hover:border-violet-600 transition-all duration-200 text-violet-400 font-mono text-[11px] font-semibold cursor-pointer"
                            title="Play from this timestamp"
                          >
                            <svg className="w-3 h-3 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>
                              {formatTime(ts.start)} - {formatTime(ts.end)}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <span className="text-[10px] text-slate-600 px-1 font-mono">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}

            {/* Typing Loader Indicator */}
            {isLoading && (
              <div className="flex flex-col items-start space-y-1.5">
                <div className="bg-slate-800/60 border border-slate-700/40 text-slate-100 rounded-2xl rounded-tl-none px-5 py-3.5 flex items-center space-x-1.5 shadow-inner">
                  <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}

            {/* Error Message banner inside chat */}
            {error && (
              <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl p-3.5 text-xs text-left">
                <strong>Error:</strong> {error}
              </div>
            )}
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 max-w-sm mx-auto my-auto">
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl text-slate-500">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="font-bold text-slate-300">
              Chat Interface Locked
            </h3>
            <p className="text-slate-500 text-xs leading-relaxed">
              Upload a document or select an indexed document from the history list on the left to start prompting the agent.
            </p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Panel */}
      <form onSubmit={handleSendMessage} className="bg-slate-900/60 border-t border-slate-900 p-4">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={!fileId || isLoading}
            placeholder={
              fileId
                ? "Ask a question about this document..."
                : "Unlock chat by selecting a document"
            }
            className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500/50 disabled:opacity-50 transition-all duration-300"
          />
          <button
            type="submit"
            disabled={!fileId || !inputValue.trim() || isLoading}
            className="p-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-30 text-white rounded-2xl transition-all duration-300 flex items-center justify-center shadow-lg shadow-violet-500/10"
          >
            <svg className="w-5 h-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}

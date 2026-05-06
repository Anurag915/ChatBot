import { useState } from 'react';
import FileIngestion from './components/FileIngestion';
import ChatWindow from './components/ChatWindow';
import MediaPlayer from './components/MediaPlayer';
import Auth from './components/Auth';

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('jwt_token') || null);

  const [activeFileId, setActiveFileId] = useState(() => {
    try {
      const savedFiles = localStorage.getItem('uploaded_files');
      if (savedFiles) {
        const filesList = JSON.parse(savedFiles);
        return filesList[0]?.file_id || null;
      }
    } catch (e) {
      console.error(e);
    }
    return null;
  });

  const [seekTrigger, setSeekTrigger] = useState(null);

  // If unauthenticated, guard the screen and render Auth switcher
  if (!token) {
    return <Auth onLoginSuccess={setToken} />;
  }

  // Resolve the full active file object from history
  const getActiveFile = () => {
    try {
      const savedFiles = localStorage.getItem('uploaded_files');
      if (savedFiles) {
        const filesList = JSON.parse(savedFiles);
        return filesList.find(f => f.file_id === activeFileId) || null;
      }
    } catch (e) {
      console.error(e);
    }
    return null;
  };

  const activeFile = getActiveFile();

  const handleSeek = (time) => {
    setSeekTrigger({ time, trigger: Date.now() });
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setToken(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col scrollbar selection:bg-violet-500/30 selection:text-violet-300 animate-fadeIn">
      {/* Premium Navigation Header */}
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-900/80 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <span className="font-extrabold text-lg bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            OmniChat RAG
          </span>
          <span className="text-xs bg-violet-500/10 border border-violet-500/20 text-violet-400 px-2 py-0.5 rounded-full font-semibold">
            v1.0
          </span>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogout}
          className="text-xs px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 hover:bg-slate-850 transition-all duration-300 font-bold flex items-center space-x-1.5 cursor-pointer"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Sign Out</span>
        </button>
      </header>

      {/* Main Work Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: File Management & Media Playback */}
        <div className="lg:col-span-5 space-y-6">
          <section className="bg-slate-900/30 border border-slate-900 rounded-3xl p-6 shadow-xl space-y-6">
            <div className="text-left space-y-2">
              <h2 className="text-xl font-extrabold text-slate-100 tracking-tight">
                Ingest Multimedia Document
              </h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                Upload a document or media file to generate contextual vector embeddings. Your agent will dynamically query chunks based on this file.
              </p>
            </div>
            <FileIngestion activeFileId={activeFileId} onFileSelect={setActiveFileId} />
          </section>

          {/* Dynamic Media Player */}
          {activeFile && (activeFile.file_type === 'audio' || activeFile.file_type === 'video') && (
            <MediaPlayer activeFile={activeFile} seekTrigger={seekTrigger} />
          )}
        </div>

        {/* Right Column: Chat Window */}
        <section className="lg:col-span-7">
          <ChatWindow fileId={activeFileId} onSeek={handleSeek} />
        </section>
      </main>
    </div>
  );
}

export default App;

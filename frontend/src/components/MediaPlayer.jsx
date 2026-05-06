import { useEffect, useRef, useState } from 'react';

export default function MediaPlayer({ activeFile, seekTrigger }) {
  const mediaRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Parse file information
  if (!activeFile || (activeFile.file_type !== 'audio' && activeFile.file_type !== 'video')) {
    return null;
  }

  const suffix = activeFile.file_name.substring(activeFile.file_name.lastIndexOf('.'));
  const mediaUrl = `http://localhost:8000/uploads/${activeFile.file_id}${suffix}`;

  // Seek and play on trigger
  useEffect(() => {
    if (seekTrigger && mediaRef.current) {
      mediaRef.current.currentTime = seekTrigger.time;
      mediaRef.current.play()
        .then(() => setIsPlaying(true))
        .catch(err => console.error("Auto play failed:", err));
    }
  }, [seekTrigger]);

  const handlePlayPause = () => {
    if (!mediaRef.current) return;
    if (isPlaying) {
      mediaRef.current.pause();
      setIsPlaying(false);
    } else {
      mediaRef.current.play()
        .then(() => setIsPlaying(true))
        .catch(err => console.error(err));
    }
  };

  const handleTimeUpdate = () => {
    if (mediaRef.current) {
      setCurrentTime(mediaRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (mediaRef.current) {
      setDuration(mediaRef.current.duration);
    }
  };

  const handleSeekChange = (e) => {
    const seekTime = parseFloat(e.target.value);
    if (mediaRef.current) {
      mediaRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-slate-900/40 border border-slate-900 rounded-3xl p-6 shadow-xl space-y-4 text-left animate-fadeIn">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-slate-950 rounded-xl border border-slate-800 text-violet-400">
            {activeFile.file_type === 'audio' ? (
              <svg className="w-5 h-5 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </div>
          <div>
            <h3 className="font-bold text-slate-200 text-sm truncate max-w-xs">
              {activeFile.file_name}
            </h3>
            <p className="text-slate-500 text-xs mt-0.5 capitalize">{activeFile.file_type} Player</p>
          </div>
        </div>
      </div>

      {/* HTML5 Media Node */}
      <div className="relative rounded-2xl overflow-hidden bg-slate-950 border border-slate-900 flex items-center justify-center">
        {activeFile.file_type === 'video' ? (
          <video
            ref={mediaRef}
            src={mediaUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            className="w-full h-auto max-h-[240px] object-contain aspect-video"
            controls
          />
        ) : (
          <div className="py-8 px-4 w-full flex flex-col items-center justify-center bg-gradient-to-b from-slate-900 to-slate-950">
            <audio
              ref={mediaRef}
              src={mediaUrl}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              className="hidden"
            />
            
            {/* Visualizer animation during play */}
            <div className="flex items-end justify-center space-x-1 h-12 mb-4">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className={`w-1 bg-violet-500 rounded-full transition-all duration-300 ${
                    isPlaying ? 'animate-bounce' : 'h-2'
                  }`}
                  style={{
                    animationDelay: `${i * 100}ms`,
                    animationDuration: '1.2s',
                    height: isPlaying ? `${Math.floor(Math.random() * 32) + 8}px` : '6px'
                  }}
                />
              ))}
            </div>

            {/* Custom Audio Control Bar */}
            <div className="w-full flex items-center space-x-4 px-2">
              <button
                onClick={handlePlayPause}
                className="p-3 bg-violet-600 hover:bg-violet-500 rounded-full text-white transition-all duration-300 shadow-md shadow-violet-500/10"
              >
                {isPlaying ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M6.75 5.25a.75.75 0 01.75-.75H9a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H7.5a.75.75 0 01-.75-.75V5.25zm7.5 0A.75.75 0 0115 4.5h1.5a.75.75 0 01.75.75v13.5a.75.75 0 01-.75.75H15a.75.75 0 01-.75-.75V5.25z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clipRule="evenodd" />
                  </svg>
                )}
              </button>

              <div className="flex-1 space-y-1">
                <input
                  type="range"
                  min="0"
                  max={duration || 100}
                  value={currentTime}
                  onChange={handleSeekChange}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-violet-500"
                />
                <div className="flex justify-between text-[11px] font-mono text-slate-500">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

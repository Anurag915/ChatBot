import { useState, useEffect } from 'react';
import api from '../services/api';

export default function FileIngestion({ onFileSelect, activeFileId }) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');

  // Load file history from localStorage on mount
  useEffect(() => {
    const savedFiles = localStorage.getItem('uploaded_files');
    if (savedFiles) {
      try {
        setFiles(JSON.parse(savedFiles));
      } catch (e) {
        console.error('Error parsing stored files:', e);
      }
    }
  }, []);

  // Persist files list to localStorage
  const saveFiles = (updatedFiles) => {
    setFiles(updatedFiles);
    localStorage.setItem('uploaded_files', JSON.stringify(updatedFiles));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      uploadFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      uploadFile(selectedFile);
    }
  };

  const uploadFile = async (file) => {
    // Validate file type
    const validExtensions = ['.pdf', '.mp3', '.wav', '.mp4', '.mkv', '.avi'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validExtensions.includes(fileExtension) && !file.type.startsWith('audio/') && !file.type.startsWith('video/') && file.type !== 'application/pdf') {
      setErrorMessage('Unsupported file type. Please upload a PDF, Audio, or Video file.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
      });

      const { file_id, file_name, file_type } = response.data;
      
      const newFileRecord = {
        file_id,
        file_name,
        file_type,
        uploadedAt: new Date().toISOString(),
        size: formatBytes(file.size),
      };

      const updatedFiles = [newFileRecord, ...files.filter(f => f.file_id !== file_id)];
      saveFiles(updatedFiles);
      
      // Auto-activate the newly uploaded file
      if (onFileSelect) {
        onFileSelect(file_id);
      }
    } catch (err) {
      console.error('Upload failed:', err);
      const detail = err.response?.data?.detail || 'An unexpected error occurred during upload.';
      setErrorMessage(detail);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const formatBytes = (bytes, decimals = 2) => {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  const getFileIcon = (fileType) => {
    if (fileType?.includes('pdf') || fileType === 'pdf') {
      return (
        <svg className="w-6 h-6 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      );
    } else if (fileType?.includes('audio') || fileType === 'audio') {
      return (
        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      );
    } else {
      return (
        <svg className="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      );
    }
  };

  const removeFile = (e, fileId) => {
    e.stopPropagation();
    const updatedFiles = files.filter(f => f.file_id !== fileId);
    saveFiles(updatedFiles);
    if (activeFileId === fileId && onFileSelect) {
      onFileSelect(updatedFiles[0]?.file_id || null);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Dropzone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center transition-all duration-300 ${
          isDragging
            ? 'border-violet-500 bg-violet-500/10 scale-[1.01]'
            : 'border-slate-700 bg-slate-800/40 hover:border-slate-600 hover:bg-slate-800/60'
        }`}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
          disabled={isUploading}
          accept=".pdf,audio/*,video/*"
        />
        
        <label
          htmlFor="file-upload"
          className={`cursor-pointer flex flex-col items-center space-y-4 text-center ${
            isUploading ? 'pointer-events-none' : ''
          }`}
        >
          {isUploading ? (
            <div className="relative flex flex-col items-center">
              {/* Spinning Ring */}
              <div className="w-16 h-16 rounded-full border-4 border-slate-700 border-t-violet-500 animate-spin mb-4" />
              <div className="absolute top-4 font-mono font-bold text-sm text-violet-400">
                {uploadProgress}%
              </div>
              <p className="text-slate-300 font-medium">Extracting & indexing document...</p>
              <p className="text-slate-500 text-xs mt-1">Please keep this window open</p>
            </div>
          ) : (
            <>
              <div className="p-4 bg-slate-800 rounded-2xl border border-slate-700 shadow-inner group-hover:scale-110 transition-transform duration-300">
                <svg className="w-8 h-8 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <div>
                <p className="text-slate-200 font-semibold text-lg">
                  Drag & drop your files here
                </p>
                <p className="text-slate-400 text-sm mt-1">
                  Or <span className="text-violet-400 hover:underline">browse files</span> from your computer
                </p>
                <p className="text-slate-500 text-xs mt-3">
                  Supports PDF, MP3, WAV, MP4, MKV (Max 100MB)
                </p>
              </div>
            </>
          )}
        </label>
      </div>

      {/* Upload Error Message */}
      {errorMessage && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl p-4 flex items-start space-x-3 text-sm animate-shake">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Uploaded Files History List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-slate-300 font-bold text-sm tracking-wide uppercase">
              Indexed Documents ({files.length})
            </h3>
            <button
              onClick={() => saveFiles([])}
              className="text-slate-500 hover:text-rose-400 text-xs font-semibold transition-colors duration-200"
            >
              Clear History
            </button>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1 scrollbar">
            {files.map((file) => (
              <div
                key={file.file_id}
                onClick={() => onFileSelect && onFileSelect(file.file_id)}
                className={`group flex items-center justify-between p-3.5 rounded-xl border transition-all duration-300 cursor-pointer ${
                  activeFileId === file.file_id
                    ? 'bg-violet-500/10 border-violet-500/40 shadow-[0_0_15px_rgba(139,92,246,0.05)]'
                    : 'bg-slate-800/40 border-slate-700/50 hover:bg-slate-800/80 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center space-x-3.5 overflow-hidden">
                  <div className="p-2 bg-slate-900 rounded-lg border border-slate-800">
                    {getFileIcon(file.file_type)}
                  </div>
                  <div className="text-left overflow-hidden">
                    <p className="text-slate-200 font-semibold text-sm truncate max-w-xs sm:max-w-md">
                      {file.file_name}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-slate-500 mt-1">
                      <span>{file.size}</span>
                      <span>•</span>
                      <span>{new Date(file.uploadedAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {activeFileId === file.file_id ? (
                    <span className="flex h-2.5 w-2.5 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-violet-500"></span>
                    </span>
                  ) : (
                    <span className="opacity-0 group-hover:opacity-100 text-xs text-violet-400 font-bold transition-all duration-300">
                      Use File
                    </span>
                  )}
                  
                  <button
                    onClick={(e) => removeFile(e, file.file_id)}
                    className="p-1 hover:bg-slate-700 rounded text-slate-500 hover:text-rose-400 transition-colors duration-200"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

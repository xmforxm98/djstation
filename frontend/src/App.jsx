import React, { useState, useRef, useEffect } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Download, Music, Wand2, BookOpen, X, Terminal, Cpu, Zap, Cloud } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

// --- Docs Component (Grok Style - Fixed & Refined) ---
const DocsView = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-[100] flex bg-black text-gray-200 font-sans overscroll-none">
      {/* Sidebar - Fixed Width */}
      <div className="w-64 border-r border-gray-800 bg-neutral-900 p-6 hidden md:flex flex-col h-full">
        <div className="mb-8 flex items-center gap-2">
          <div className="w-6 h-6 bg-blue-600 rounded-md shadow-[0_0_10px_rgba(37,99,235,0.5)]"></div>
          <span className="font-bold text-white tracking-widest text-sm">DJ STATION DOCS</span>
        </div>

        <nav className="space-y-1">
          {['Getting Started', 'Overview', 'Authentication', 'API Reference', 'SDKs'].map((item) => (
            <div key={item} className={`px-3 py-2 text-sm rounded cursor-pointer transition-colors ${item === 'Overview' ? 'text-white bg-white/10' : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`}>
              {item}
            </div>
          ))}
        </nav>

        <div className="mt-auto pt-6 border-t border-gray-800">
          <button onClick={onClose} className="text-gray-400 hover:text-white text-sm flex items-center gap-2 w-full px-2 py-2 rounded hover:bg-white/5 transition-colors">
            <X className="w-4 h-4" /> Close Docs
          </button>
        </div>
      </div>

      {/* Main Content - Scrollable */}
      <div className="flex-1 overflow-y-auto bg-black p-8 md:p-16 h-full">
        <div className="max-w-4xl mx-auto pb-20">
          <div className="mb-16">
            <h5 className="text-blue-500 text-sm mb-4 font-mono uppercase tracking-wider">Getting started</h5>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-8 tracking-tight">Welcome to API</h1>
            <p className="text-xl text-gray-400 leading-relaxed max-w-2xl">
              Integrate professional-grade audio mixing into your applications.
              Our API enables seamless beat-matching, harmonic mixing, and intelligent looping using advanced signal processing.
            </p>
          </div>

          {/* Feature Highlight Card */}
          <div className="grid md:grid-cols-2 gap-6 mb-20">
            <div className="col-span-2 relative group overflow-hidden rounded-2xl border border-gray-800 bg-gradient-to-br from-gray-900 to-black p-1">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative z-10 bg-neutral-900/50 backdrop-blur-sm p-8 h-full rounded-xl">
                <div className="flex justify-between items-start mb-6">
                  <h3 className="text-2xl font-bold text-white">DJ Engine Alpha</h3>
                  <span className="bg-blue-900/30 text-blue-400 text-xs px-2 py-1 rounded border border-blue-800/50">v1.2.0</span>
                </div>
                <p className="text-gray-400 mb-8 max-w-md">Our flagship mixing engine, optimized for high-fidelity transitions and real-time analysis.</p>

                <div className="grid grid-cols-2 gap-y-6 gap-x-12 border-t border-gray-800 pt-6">
                  <div>
                    <span className="text-xs text-gray-500 block mb-1 font-mono uppercase">Latency</span>
                    <span className="text-white font-mono text-xl">&lt; 200ms</span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block mb-1 font-mono uppercase">Format</span>
                    <span className="text-white font-mono text-xl">WAV / MP3</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <h2 className="text-3xl font-bold text-white mb-8">Jump right in</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Terminal, title: "Quickstart", desc: "Get your API Key and make your first mix request." },
              { icon: Cpu, title: "Analysis", desc: "Detect BPM, Key, and Energy levels via AI." },
              { icon: Cloud, title: "Storage", desc: "Learn about our ephemeral secure storage policy." }
            ].map((card, idx) => (
              <div key={idx} className="group p-6 rounded-2xl cursor-pointer bg-neutral-900 border border-gray-800 transition-all hover:border-gray-600 hover:bg-neutral-800">
                <div className="w-12 h-12 rounded-xl bg-gray-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <card.icon className="w-6 h-6 text-gray-300" />
                </div>
                <h3 className="text-white text-lg font-bold mb-3">{card.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{card.desc}</p>
                <div className="mt-4 text-blue-500 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                  Learn more &rarr;
                </div>
              </div>
            ))}
          </div>

          <div className="mt-24 pt-8 border-t border-gray-800 text-gray-600 text-sm flex justify-between font-mono">
            <p>© 2026 DJ Station API Services</p>
            <p>All systems operational</p>
          </div>
        </div>
      </div>
    </div>
  );
};


// --- Sky Theme Components ---

const FileUploader = ({ onFileSelect, label, trackId, icon }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'audio/*': ['.mp3', '.wav', '.flac', '.m4a'] },
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(trackId, acceptedFiles[0]);
      }
    },
    maxFiles: 1
  });

  return (
    <div
      {...getRootProps()}
      className={`relative h-40 rounded-3xl transition-all flex flex-col items-center justify-center cursor-pointer border border-white/40
        ${isDragActive ? 'bg-white/60 scale-105 shadow-xl' : 'bg-white/20 hover:bg-white/40 hover:scale-[1.02]'}
      `}
    >
      <input {...getInputProps()} />
      <div className="z-10 text-center text-slate-700">
        <div className="bg-white/50 w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-sm text-blue-600">
          {icon || <Music className="w-6 h-6" />}
        </div>
        <p className="text-sm font-bold tracking-tight">{label}</p>
        <p className="text-xs text-slate-500 mt-1 opacity-70">
          {isDragActive ? 'Release to upload' : 'MPEG-3 • WAV • FLAC'}
        </p>
      </div>
    </div>
  );
};

const FloatingTrackCard = ({ track, onRemove }) => {
  if (!track) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      className="bg-white/60 backdrop-blur-xl p-4 rounded-3xl border border-white/50 shadow-lg flex items-center gap-4 relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-3 opacity-10">
        <Music className="w-24 h-24 rotate-12" />
      </div>

      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 z-10">
        <Music className="w-7 h-7 text-white" />
      </div>
      <div className="flex-1 min-w-0 z-10">
        <h4 className="font-bold text-slate-800 truncate">{track.file.name}</h4>
        <div className="flex gap-3 text-xs font-semibold text-slate-500 mt-1">
          {track.analysis ? (
            <>
              <span className="flex items-center gap-1 bg-white/50 px-2 py-1 rounded-lg">
                <Zap className="w-3 h-3 text-yellow-500" />
                {track.analysis.bpm.toFixed(1)} <span className="text-slate-400">BPM</span>
              </span>
              <span className="flex items-center gap-1 bg-white/50 px-2 py-1 rounded-lg">
                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                {track.analysis.camelot}
              </span>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </div>
          )}
        </div>
      </div>
      <button
        onClick={onRemove}
        className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-200 hover:bg-slate-300 text-slate-600 transition-colors z-10"
      >
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
};

const SkyButton = ({ onClick, disabled, children, secondary }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`
      relative overflow-hidden group
      px-8 py-4 rounded-2xl font-bold text-lg transition-all transform
      ${secondary
        ? 'bg-white/40 text-slate-700 hover:bg-white/60'
        : 'bg-slate-900 text-white hover:bg-slate-800 shadow-xl shadow-blue-900/10'
      }
      ${disabled ? 'opacity-50 cursor-not-allowed transform-none' : 'hover:-translate-y-1 active:translate-y-0'}
    `}
  >
    <div className="relative z-10 flex items-center justify-center gap-2">
      {children}
    </div>
  </button>
);

// --- AdSense Component ---
const AdBanner = ({ slotId }) => {
  useEffect(() => {
    try {
      // Check if adsbygoogle is available and script is loaded
      if (window.adsbygoogle) {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      }
    } catch (e) {
      console.error("AdSense Error:", e);
    }
  }, []);

  return (
    <div className="my-6 w-full max-w-4xl mx-auto overflow-hidden rounded-2xl bg-white/10 flex items-center justify-center min-h-[100px] border border-white/5 border-dashed">
      <ins className="adsbygoogle"
        style={{ display: 'block', width: '100%' }}
        data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
        data-ad-slot={slotId}
        data-ad-format="auto"
        data-full-width-responsive="true"></ins>
      {/* Fallback Label for Dev Mode */}
      <span className="absolute text-[10px] text-slate-400 font-mono tracking-widest pointer-events-none opacity-20">ADSENSE AD SPACE</span>
    </div>
  );
};


// --- Main App ---

function App() {
  const [tracks, setTracks] = useState({ track1: null, track2: null });
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState('mix');
  const [showDocs, setShowDocs] = useState(false);

  // API Client with Auth Header
  const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: { 'X-API-Key': 'sk_demo_pro_99999' }
  });

  const handleFileUpload = async (trackId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setTracks(prev => ({ ...prev, [trackId]: { file, analysis: null } }));
      const uploadRes = await apiClient.post('/upload', formData);
      const fileId = uploadRes.data.file_id;
      const analyzeRes = await apiClient.get(`/analyze/${fileId}`);

      setTracks(prev => ({
        ...prev,
        [trackId]: {
          file,
          fileId,
          analysis: analyzeRes.data
        }
      }));

    } catch (err) {
      console.error(err);
      alert("Upload failed. Is the backend running?");
    }
  };

  const handleAction = async () => {
    setIsProcessing(true);
    setResult(null);

    try {
      let res;
      if (mode === 'mix') {
        res = await apiClient.post('/mix', null, {
          params: {
            track1_id: tracks.track1.fileId,
            track2_id: tracks.track2.fileId,
            transition_style: 'classic'
          }
        });
      } else {
        res = await apiClient.post('/extend', null, {
          params: {
            file_id: tracks.track1.fileId,
            duration: '30m'
          }
        });
      }

      const { output_id } = res.data;
      setResult(`http://localhost:8000/api/download/${output_id}`);

    } catch (err) {
      console.error(err);
      alert("Processing failed.");
    } finally {
      setIsProcessing(false);
    }
  };

  if (showDocs) {
    return <DocsView onClose={() => setShowDocs(false)} />;
  }

  return (
    <div className="min-h-screen bg-sky-gradient overflow-hidden relative">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-400/20 blur-[120px] rounded-full mix-blend-overlay"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-white/40 blur-[120px] rounded-full mix-blend-overlay"></div>
      </div>

      <nav className="relative z-20 px-6 py-6 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center text-white font-bold">D</div>
          <span className="font-bold text-slate-800 tracking-tight">DJ STATION</span>
        </div>
        <div className="flex gap-4">
          <button onClick={() => setShowDocs(true)} className="flex items-center gap-2 text-slate-600 font-medium bg-white/40 hover:bg-white/60 px-4 py-2 rounded-xl transition-all">
            <BookOpen className="w-4 h-4" /> Docs
          </button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-5xl relative z-10 flex flex-col items-center">

        {/* Top Ad */}
        <AdBanner slotId="YOUR_TOP_SLOT_ID" />

        {/* Floating Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="floating-card p-2 w-full max-w-4xl"
        >
          <div className="bg-white/40 rounded-[24px] p-8 md:p-12 backdrop-blur-sm">

            {/* Mode Switcher */}
            <div className="flex justify-center mb-10">
              <div className="bg-slate-200/50 p-1 rounded-2xl inline-flex gap-1 shadow-inner">
                <button
                  onClick={() => setMode('mix')}
                  className={`px-8 py-3 rounded-xl font-bold text-sm transition-all ${mode === 'mix' ? 'bg-white shadow-md text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
                >
                  Mix Tracks
                </button>
                <button
                  onClick={() => setMode('extend')}
                  className={`px-8 py-3 rounded-xl font-bold text-sm transition-all ${mode === 'extend' ? 'bg-white shadow-md text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
                >
                  Extend Loop
                </button>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 mb-10 items-start">
              {/* Input A */}
              <div className="space-y-4">
                {!tracks.track1 ? (
                  <FileUploader
                    label={mode === 'mix' ? "Track A" : "Source Track"}
                    trackId="track1"
                    onFileSelect={handleFileUpload}
                    icon={<Music className="w-6 h-6 text-blue-600" />}
                  />
                ) : (
                  <FloatingTrackCard
                    track={tracks.track1}
                    onRemove={() => setTracks(prev => ({ ...prev, track1: null }))}
                  />
                )}
              </div>

              {/* Input B (Mix Mode Only) */}
              <div className="space-y-4">
                {mode === 'mix' ? (
                  !tracks.track2 ? (
                    <FileUploader
                      label="Track B"
                      trackId="track2"
                      onFileSelect={handleFileUpload}
                      icon={<Music className="w-6 h-6 text-indigo-600" />}
                    />
                  ) : (
                    <FloatingTrackCard
                      track={tracks.track2}
                      onRemove={() => setTracks(prev => ({ ...prev, track2: null }))}
                    />
                  )
                ) : (
                  <div className="h-full min-h-[160px] flex flex-col justify-center items-center bg-white/20 rounded-3xl border border-white/30 text-center p-6">
                    <span className="text-3xl font-bold text-slate-700 mb-2">30 min</span>
                    <span className="text-slate-500 font-medium">Target Loop Duration</span>
                    <p className="text-xs text-slate-400 mt-2 max-w-[200px]">Optimal intro/outro points will be automatically detected.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Main Action */}
            <div className="flex justify-center pb-4">
              <SkyButton
                onClick={handleAction}
                disabled={isProcessing || !tracks.track1 || (mode === 'mix' && !tracks.track2)}
              >
                {isProcessing ? (
                  <><Wand2 className="w-5 h-5 animate-spin" /> Processing Media...</>
                ) : (
                  <><Wand2 className="w-5 h-5" /> {mode === 'mix' ? 'Generate Mix' : 'Extend Track'}</>
                )}
              </SkyButton>
            </div>

          </div>
        </motion.div>

        {/* Result Pop-in */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              className="mt-8 w-full max-w-2xl bg-white rounded-3xl shadow-2xl p-2 z-20"
            >
              <div className="bg-slate-50 rounded-[20px] p-6 text-center border border-slate-100">
                <h3 className="text-xl font-bold text-slate-800 mb-2">Your Mix is Ready!</h3>
                <p className="text-slate-500 mb-6 text-sm">Download your high-fidelity audio file below.</p>

                <a
                  href={result}
                  download
                  className="inline-flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white font-bold px-8 py-3 rounded-xl transition-all shadow-lg shadow-green-200"
                >
                  <Download className="w-5 h-5" />
                  Download .MP3
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bottom Ad */}
        <AdBanner slotId="YOUR_BOTTOM_SLOT_ID" />

        <div className="mt-12 opacity-60">
          <div className="bg-white/20 px-6 py-3 rounded-full text-xs font-semibold text-slate-500 tracking-wider">
            POWERED BY PYTHON AUDIO ENGINE
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;

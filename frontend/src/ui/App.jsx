import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, ArrowRight, ArrowDown, Settings, Download, RefreshCw, Video, Play, Pause } from "lucide-react";
import { MandelbrotCanvas } from "./MandelbrotCanvas";

export function App() {
  const [form, setForm] = useState({ 
    songTitle: "", 
    artistName: "",
    model: "auto",
    palette: "auto",
    depth: 5
  });
  const [audioFile, setAudioFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [exportingVideo, setExportingVideo] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);
  const audioDataRef = useRef(0.0);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const setupAudioContext = () => {
    if (!audioRef.current) return;
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      sourceRef.current = audioContextRef.current.createMediaElementSource(audioRef.current);
      sourceRef.current.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);
      
      const updateAudioData = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const average = sum / dataArray.length;
          audioDataRef.current = average / 255.0;
        }
        requestAnimationFrame(updateAudioData);
      };
      updateAudioData();
    }
  };

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        setupAudioContext();
        if (audioContextRef.current.state === 'suspended') {
          audioContextRef.current.resume();
        }
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleExportVideo = async () => {
    setExportingVideo(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("song_title", form.songTitle);
      if (form.artistName) formData.append("artist_name", form.artistName);
      if (audioFile) formData.append("audio_file", audioFile);
      formData.append("override_model", form.model);
      formData.append("override_palette", form.palette);
      if (form.depth) formData.append("override_depth", form.depth);

      const res = await fetch("/api/export_video", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("VIDEO EXPORT FAILED.");
      }

      const data = await res.json();
      setVideoUrl(data.video_url);
    } catch (err) {
      setError(err.message || "SYSTEM ERROR.");
    } finally {
      setExportingVideo(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    if(e) e.preventDefault();
    setError("");

    if (!form.songTitle.trim()) {
      setError("SONG TITLE REQUIRED.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("song_title", form.songTitle);
      if (form.artistName) formData.append("artist_name", form.artistName);
      if (audioFile) formData.append("audio_file", audioFile);
      
      formData.append("override_model", form.model);
      formData.append("override_palette", form.palette);
      if (form.depth) formData.append("override_depth", form.depth);

      const res = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "SYNTHESIS FAILED.");
      }

      const data = await res.json();
      data.image_url = data.image_url + "?t=" + new Date().getTime();
      setResult(data);
      
      setTimeout(() => {
        window.scrollTo({ top: window.innerHeight * 0.9, behavior: 'smooth' });
      }, 500);

    } catch (err) {
      setError(err.message || "SYSTEM ERROR.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToNext = (e) => {
    e.preventDefault();
    const currentScroll = window.scrollY;
    const windowHeight = window.innerHeight;
    const nextSection = Math.ceil((currentScroll + 10) / windowHeight) * windowHeight;
    window.scrollTo({ top: nextSection, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#F4F4F5] font-['Space_Grotesk'] overflow-x-hidden selection:bg-white selection:text-black relative transition-colors duration-1000">
      
      {/* DYNAMIC BACKGROUND */}
      <AnimatePresence>
        {result ? (
          <motion.div 
            key="fractal-bg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 2 }}
            className="fixed inset-0 z-0 pointer-events-none"
          >
            <div className="absolute inset-0 bg-black/70 z-10 backdrop-blur-3xl"></div>
            <img 
              src={result.image_url} 
              alt="Background" 
              className="w-full h-full object-cover opacity-60 mix-blend-screen scale-110"
            />
          </motion.div>
        ) : (
          <motion.div 
            key="default-bg"
            className="fixed inset-0 z-0 pointer-events-none overflow-hidden"
          >
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-900/20 blur-[120px] rounded-full mix-blend-screen animate-pulse duration-10000"></div>
            <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-purple-900/10 blur-[150px] rounded-full mix-blend-screen animate-pulse duration-7000 delay-1000"></div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative z-10">
        {/* HERO SECTION */}
        <section className="min-h-screen flex flex-col justify-center px-8 lg:px-24 py-12">
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            className="text-5xl md:text-8xl font-medium tracking-tighter uppercase mb-16 leading-none font-['Outfit'] drop-shadow-2xl"
          >
            Fractal<br />Resonance
          </motion.h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 w-full max-w-7xl">
            {/* Main Inputs */}
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-7 flex flex-col gap-10"
            >
              <input
                name="songTitle"
                placeholder="SONG TITLE *"
                value={form.songTitle}
                onChange={handleChange}
                autoComplete="off"
                className="w-full bg-transparent border-b border-white/30 pb-4 text-3xl font-light focus:outline-none focus:border-white transition-colors placeholder:text-white/40 drop-shadow-md"
              />
              <input
                name="artistName"
                placeholder="ARTIST"
                value={form.artistName}
                onChange={handleChange}
                autoComplete="off"
                className="w-full bg-transparent border-b border-white/30 pb-4 text-3xl font-light focus:outline-none focus:border-white transition-colors placeholder:text-white/40 drop-shadow-md"
              />
              
              <div 
                onClick={() => fileInputRef.current?.click()}
                className="flex justify-between items-center py-4 border-b border-white/30 cursor-pointer text-white/70 hover:text-white transition-colors group drop-shadow-md"
              >
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="audio/*" hidden />
                <span className="text-sm tracking-[0.2em] uppercase group-hover:tracking-[0.25em] transition-all duration-500">
                  {audioFile ? audioFile.name : "ATTACH AUDIO [OPTIONAL]"}
                </span>
                <Upload size={18} className="group-hover:-translate-y-1 transition-transform" />
              </div>
            </motion.div>

            {/* Premium Control Panel */}
            <motion.div 
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-5 relative group"
            >
              <div className="absolute inset-0 bg-white/5 blur-xl group-hover:bg-white/10 transition-colors duration-700 rounded-3xl"></div>
              <div className="relative bg-black/50 backdrop-blur-2xl border border-white/20 p-8 rounded-3xl flex flex-col gap-8 shadow-2xl">
                <div className="flex items-center gap-3 text-xs tracking-[0.2em] text-white/80 uppercase border-b border-white/20 pb-4 font-['Outfit']">
                  <Settings size={16} />
                  <span>Mathematics Override</span>
                </div>
                
                <div className="flex flex-col gap-3 group/select">
                  <label className="text-[10px] text-white/50 uppercase tracking-[0.2em]">Fractal Engine</label>
                  <select name="model" value={form.model} onChange={handleChange} className="bg-white/10 border border-white/20 rounded-lg p-3 text-sm focus:outline-none focus:border-white/50 transition-colors appearance-none cursor-pointer backdrop-blur-sm">
                    <option value="auto">Auto (Analyzed)</option>
                    <option value="organic_tree">Organic Tree</option>
                    <option value="sierpinski">Sierpinski Geometry</option>
                    <option value="dragon_curve">Dragon Curve</option>
                    <option value="mandelbrot">Mandelbrot Set</option>
                    <option value="koch_snowflake">Koch Snowflake</option>
                  </select>
                </div>

                <div className="flex flex-col gap-3 group/select">
                  <label className="text-[10px] text-white/50 uppercase tracking-[0.2em]">Chromatic Profile</label>
                  <select name="palette" value={form.palette} onChange={handleChange} className="bg-white/10 border border-white/20 rounded-lg p-3 text-sm focus:outline-none focus:border-white/50 transition-colors appearance-none cursor-pointer backdrop-blur-sm">
                    <option value="auto">Auto (Analyzed)</option>
                    <option value="cool">Cool (Blues)</option>
                    <option value="warm">Warm (Reds)</option>
                    <option value="vibrant">Vibrant (Multi)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-4">
                  <div className="flex justify-between text-[10px] text-white/50 uppercase tracking-[0.2em]">
                    <label>Recursion Depth</label>
                    <span className="text-white/90">{form.depth}</span>
                  </div>
                  <input 
                    type="range" name="depth" min="3" max="14" 
                    value={form.depth} onChange={handleChange} 
                    className="w-full cursor-pointer accent-white bg-white/20 h-1 rounded-full appearance-none hover:bg-white/40 transition-colors" 
                  />
                </div>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <button 
              onClick={handleSubmit} 
              disabled={loading} 
              className="mt-16 bg-white text-black px-10 py-5 rounded-full font-['Outfit'] font-semibold tracking-[0.2em] uppercase flex items-center justify-between w-full max-w-md hover:bg-gray-200 hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 shadow-[0_0_40px_rgba(255,255,255,0.3)]"
            >
              {loading ? "SYNTHESIZING..." : "GENERATE FRACTAL"}
              {!loading && <ArrowRight size={18} />}
            </button>
          </motion.div>

          {result && !loading && (
            <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/70 text-xs tracking-[0.2em] animate-bounce cursor-pointer hover:text-white transition-colors" onClick={scrollToNext}>
              <span>SCROLL</span>
              <ArrowDown size={16} />
            </div>
          )}
        </section>

        {/* RESULTS SECTIONS */}
        {result && !loading && (
          <>
            {/* ARTWORK SECTION */}
            <section className="min-h-screen flex flex-col justify-center px-8 lg:px-24 py-24 relative">
              <motion.div
                initial={{ opacity: 0, y: 100 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              >
                <h2 className="text-xs text-white/70 tracking-[0.3em] mb-12 uppercase font-['Outfit'] drop-shadow-md">
                  01 // VISUAL SIGNATURE
                </h2>
                
                <div className="w-full aspect-square md:aspect-[21/9] max-h-[75vh] rounded-3xl flex items-center justify-center overflow-hidden bg-black/60 backdrop-blur-2xl border border-white/20 relative group shadow-2xl">
                  {result.fractal.model === "mandelbrot" && result.fractal.math_details?.shader_uniforms ? (
                    <div className="w-full h-full cursor-grab active:cursor-grabbing">
                      <MandelbrotCanvas uniforms={result.fractal.math_details.shader_uniforms} audioData={audioDataRef} />
                    </div>
                  ) : (
                    <img src={result.image_url} alt="Fractal Art" className="w-full h-full object-contain mix-blend-screen" />
                  )}
                  
                  {/* Action Bar Overlay */}
                  <div className="absolute bottom-0 left-0 w-full p-8 bg-gradient-to-t from-black via-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex flex-wrap justify-center gap-4">
                    {audioFile && (
                      <>
                        <audio 
                          ref={audioRef} 
                          src={URL.createObjectURL(audioFile)} 
                          onEnded={() => setIsPlaying(false)}
                          crossOrigin="anonymous"
                        />
                        <button onClick={togglePlay} className="bg-white hover:bg-gray-200 text-black px-6 py-3 rounded-full text-xs tracking-widest uppercase flex items-center gap-2 transition-all duration-300 shadow-xl">
                          {isPlaying ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Play</>}
                        </button>
                      </>
                    )}
                    <button onClick={handleSubmit} className="bg-white/20 hover:bg-white text-white hover:text-black px-6 py-3 rounded-full text-xs tracking-widest uppercase flex items-center gap-2 transition-all duration-300 backdrop-blur-md border border-white/30">
                      <RefreshCw size={14} /> Regenerate
                    </button>
                    <a href={result.image_url} download={`Fractal-${result.song_title}.png`} className="bg-white/20 hover:bg-white text-white hover:text-black px-6 py-3 rounded-full text-xs tracking-widest uppercase flex items-center gap-2 transition-all duration-300 backdrop-blur-md border border-white/30">
                      <Download size={14} /> PNG
                    </a>
                    <button onClick={handleExportVideo} disabled={exportingVideo} className="bg-white hover:bg-gray-200 text-black px-6 py-3 rounded-full text-xs tracking-widest uppercase flex items-center gap-2 transition-all duration-300 shadow-xl disabled:opacity-50">
                      {exportingVideo ? <><RefreshCw size={14} className="animate-spin" /> Rendering...</> : <><Video size={14} /> MP4 Video</>}
                    </button>
                  </div>
                </div>
                
                {videoUrl && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mt-8 text-center">
                    <a href={videoUrl} download={`Fractal-${result.song_title}.mp4`} className="text-white hover:text-gray-300 underline tracking-[0.2em] uppercase text-xs">
                      Video Ready: Click to Download MP4
                    </a>
                  </motion.div>
                )}
              </motion.div>
            </section>

            {/* DATA SECTION */}
            <section className="min-h-screen flex flex-col justify-center px-8 lg:px-24 py-24 relative">
              <motion.div
                initial={{ opacity: 0, y: 100 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                className="bg-black/50 backdrop-blur-xl border border-white/10 rounded-3xl p-12 shadow-2xl"
              >
                <h2 className="text-xs text-white/70 tracking-[0.3em] mb-16 border-b border-white/20 pb-6 uppercase font-['Outfit']">
                  02 // TOPOLOGY DATA
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-16">
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">TRACK</span>
                    <span className="text-3xl font-light tracking-tight">{result.song_title}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">MATHEMATICS</span>
                    <span className="text-3xl font-light tracking-tight capitalize">{result.fractal.model.replace('_', ' ')}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">BPM</span>
                    <span className="text-3xl font-light tracking-tight">{result.features.bpm || "120"}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">SYMMETRY</span>
                    <span className="text-3xl font-light tracking-tight">{result.features.symmetry_score?.toFixed(2)}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">CHROMATICS</span>
                    <span className="text-3xl font-light tracking-tight capitalize">{result.fractal.color_palette}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">SEED HASH</span>
                    <span className="text-lg font-mono text-white/60 truncate">{result.fractal.seed}</span>
                  </div>
                </div>
              </motion.div>
            </section>

            {/* LYRICS SECTION */}
            {result.lyrics && (
              <section className="min-h-screen flex flex-col justify-center px-8 lg:px-24 py-24 relative">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                >
                  <h2 className="text-xs text-white/70 tracking-[0.3em] mb-16 uppercase font-['Outfit'] text-center drop-shadow-md">
                    03 // SOURCE TEXT
                  </h2>
                  <div className="font-['Inter'] text-xl md:text-2xl leading-[2.5] text-white/90 whitespace-pre-wrap max-w-4xl mx-auto text-center font-light drop-shadow-lg bg-black/40 p-12 rounded-3xl backdrop-blur-md border border-white/10">
                    {result.lyrics}
                  </div>
                </motion.div>
              </section>
            )}

            {/* MATHEMATICS SECTION */}
            {result.fractal.math_details && (
              <section className="min-h-screen flex flex-col justify-center px-8 lg:px-24 py-24 relative pb-48">
                <motion.div
                  initial={{ opacity: 0, y: 100 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                  className="bg-white/5 backdrop-blur-2xl border border-white/20 rounded-3xl p-12 lg:p-20 shadow-2xl max-w-5xl mx-auto w-full"
                >
                  <h2 className="text-xs text-white/70 tracking-[0.3em] mb-16 border-b border-white/20 pb-6 uppercase font-['Outfit']">
                    04 // THE MATHEMATICS
                  </h2>
                  
                  <div className="flex flex-col gap-16">
                    {/* Equation */}
                    <div className="flex flex-col gap-4">
                      <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">Core Equation / Rules</span>
                      <div className="font-mono text-2xl md:text-4xl text-white tracking-tight break-words">
                        {result.fractal.math_details.equation}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
                      {/* Description */}
                      <div className="flex flex-col gap-4">
                        <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">Mathematical Theory</span>
                        <p className="font-['Inter'] text-lg text-white/80 leading-relaxed font-light">
                          {result.fractal.math_details.description}
                        </p>
                      </div>

                      {/* Dynamic Variables */}
                      <div className="flex flex-col gap-4">
                        <span className="text-[10px] text-white/50 tracking-[0.2em] uppercase font-['Outfit']">Acoustic Mutation Vectors</span>
                        <div className="bg-black/50 p-6 rounded-2xl border border-white/10">
                          <p className="font-mono text-sm text-white/90 leading-loose">
                            {result.fractal.math_details.dynamic_variables}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </section>
            )}
          </>
        )}
      </div>

      <AnimatePresence>
        {loading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-lg flex flex-col items-center justify-center z-50"
          >
            <div className="w-24 h-24 border-t-2 border-l-2 border-white rounded-full animate-spin mb-8"></div>
            <div className="text-2xl tracking-[0.5em] font-light animate-pulse uppercase font-['Outfit']">
              SYNTHESIZING
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

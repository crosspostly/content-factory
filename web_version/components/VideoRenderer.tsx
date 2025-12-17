
import React, { useEffect, useRef, useState } from 'react';
import { Scenario, Track, ProjectMode, ScriptureContent, HoroscopeContent, VitalityContent, VideoFormat } from '../types';
import JSZip from 'jszip';
import { MediaService } from '../services/mediaService';

interface VideoRendererProps {
  mode?: ProjectMode;
  videoFormat: VideoFormat;
  scenario?: Scenario | null;
  scripture?: ScriptureContent | null;
  horoscope?: HoroscopeContent | null;
  vitality?: VitalityContent | null;
  images: Record<string, string>;
  track: Track;
  voiceoverUrl?: string | null;
  onReset: () => void;
}

type FrameType = 'THUMBNAIL_FLASH' | 'SPLIT_VS' | 'ANIMAL_A' | 'ANIMAL_B' | 'VICTORY' | 
                 'SHORTS_SCENE' | 
                 'CHAPTER_INTRO' | 'CHAPTER_CONTENT' | 'GLOBAL_INTRO' | 'GLOBAL_OUTRO' | 'ERROR_FALLBACK';

interface VideoFrame {
  type: FrameType;
  imageMain?: string;
  imageA?: string;
  imageB?: string;
  text?: string;
  subText?: string;
  duration: number;
  startScale?: number;
  endScale?: number;
  startPanX?: number; 
  endPanX?: number;
  shakeIntensity?: number;
  highlight?: boolean;
}

// Union type for asset cache
type MediaAsset = HTMLImageElement | HTMLVideoElement;

const mediaService = new MediaService();

// --- TEXT UTILS ---

/**
 * Splits text into lines based on canvas width and font size.
 */
const getWrappedLines = (ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] => {
    const words = text.split(' ');
    const lines = [];
    let currentLine = words[0];

    for (let i = 1; i < words.length; i++) {
        const word = words[i];
        const width = ctx.measureText(currentLine + " " + word).width;
        if (width < maxWidth) {
            currentLine += " " + word;
        } else {
            lines.push(currentLine);
            currentLine = word;
        }
    }
    lines.push(currentLine);
    return lines;
};

// Chunk text roughly for timing, but rendering handles visual wrapping
const chunkText = (text: string, maxWords: number = 6): string[] => {
    if (!text) return [];
    const words = text.split(' ');
    const chunks = [];
    for (let i = 0; i < words.length; i += maxWords) {
        chunks.push(words.slice(i, i + maxWords).join(' '));
    }
    return chunks;
};

const buildTimeline = (props: VideoRendererProps, duration: number, log: (msg: string) => void): VideoFrame[] => {
    const { mode, scenario, scripture, horoscope, vitality, images, videoFormat } = props;
    const frames: VideoFrame[] = [];
    const totalMs = duration * 1000;
    const imgKeys = Object.keys(images).filter(k => k !== 'thumbnail');
    
    let imgIdx = 0;
    const getNextImg = () => {
        const key = imgKeys[imgIdx % imgKeys.length];
        imgIdx++;
        return images[key];
    };

    // --- 1. THUMBNAIL INJECTION (0.1s) ---
    if (images['thumbnail']) {
        frames.push({ 
            type: 'THUMBNAIL_FLASH', 
            imageMain: images['thumbnail'], 
            duration: 100, 
            startScale: 1.0, endScale: 1.0 
        });
    }

    try {
        // === CHRISTIAN MODE ===
        if (mode === 'CHRISTIAN' && scripture) {
             // Treat Marathon and Standard Long Form similarly in renderer - they just have different content structure
             if (scripture.chapters) {
                // LONG FORM LOGIC (Chapters)
                const chapters = scripture.chapters;
                const introDur = 5000;
                const outroDur = 5000;
                
                // Allocate remaining time to content
                const contentDuration = totalMs - introDur - outroDur;
                
                // Calculate total "weight" of text
                let totalItems = 0;
                chapters.forEach(c => totalItems += (c.items?.length || 0));
                
                const timePerItem = contentDuration / (totalItems || 1);

                // Intro
                frames.push({ 
                    type: 'GLOBAL_INTRO', 
                    imageMain: getNextImg(), 
                    text: scripture.title, 
                    duration: introDur, 
                    startScale: 1.0, endScale: 1.05 
                });

                // Chapters
                chapters.forEach((chap) => {
                    (chap.items || []).forEach((item) => {
                        frames.push({
                            type: 'CHAPTER_CONTENT',
                            imageMain: getNextImg(),
                            text: item.content_spoken, // The prayer/decree
                            subText: item.title,       // The heading/verse ref
                            duration: timePerItem,
                            startScale: 1.0,
                            endScale: 1.05
                        });
                    });
                });

                // Outro
                frames.push({ 
                    type: 'GLOBAL_OUTRO', 
                    imageMain: getNextImg(), 
                    text: "SUBSCRIBE FOR MORE", 
                    duration: outroDur, 
                    startScale: 1.05, endScale: 1.1 
                });

             } else {
                // SHORTS LOGIC
                const hook = scripture.title || "Prayer";
                const body = scripture.reflection || "";
                
                frames.push({
                    type: 'SHORTS_SCENE',
                    imageMain: getNextImg(),
                    text: hook,
                    subText: "Watch until the end",
                    duration: 3000,
                    startScale: 1.0, endScale: 1.05,
                    highlight: true
                });

                const chunks = chunkText(body, 5); // 5 words per chunk for readability
                const durPerChunk = (totalMs - 4000) / chunks.length; // Reserve 3s start, 1s end

                chunks.forEach((chunk, i) => {
                    const swapImg = i % 2 === 0; // Change image every other chunk
                    frames.push({
                        type: 'SHORTS_SCENE',
                        imageMain: swapImg ? getNextImg() : frames[frames.length-1].imageMain,
                        text: chunk,
                        duration: durPerChunk,
                        startScale: swapImg ? 1.0 : 1.05,
                        endScale: swapImg ? 1.05 : 1.10
                    });
                });
             }
        }
        
        // === GENERIC FALLBACK ===
        else {
             // Just show something
             frames.push({ type: 'SHORTS_SCENE', imageMain: getNextImg(), text: "GENERATING PREVIEW...", duration: totalMs, startScale: 1.0, endScale: 1.1 });
        }

    } catch (err) {
        console.error("Timeline build error", err);
        log("❌ Error building timeline");
    }

    if (frames.length === 0) {
        frames.push({ type: 'ERROR_FALLBACK', text: "RENDERING ERROR", subText: "No content generated", duration: 5000 });
    }

    return frames;
};

// Function to draw image
const drawAsset = (ctx: CanvasRenderingContext2D, asset: MediaAsset, width: number, height: number, progress: number, frame: VideoFrame) => {
    if (asset instanceof HTMLImageElement) {
        const scale = (frame.startScale || 1) + ((frame.endScale || 1.1) - (frame.startScale || 1)) * progress;
        ctx.save(); 
        ctx.translate(width/2, height/2); 
        ctx.scale(scale, scale); 
        ctx.translate(-width/2, -height/2);
        ctx.drawImage(asset, 0, 0, width, height); 
        ctx.restore();
    }
};

const renderFrame = (ctx: CanvasRenderingContext2D, frame: VideoFrame, width: number, height: number, progress: number, assets: Record<string, MediaAsset>, format: VideoFormat) => {
    // 1. CLEAR & BACKGROUND
    ctx.fillStyle = 'black'; ctx.fillRect(0,0,width,height);
    
    // 2. DRAW IMAGE
    const asset = frame.imageMain ? assets[frame.imageMain] : null;
    if (asset) {
        drawAsset(ctx, asset, width, height, progress, frame);
    } else {
         const gradient = ctx.createLinearGradient(0, 0, 0, height);
         gradient.addColorStop(0, '#1a1a1a');
         gradient.addColorStop(1, '#000000');
         ctx.fillStyle = gradient;
         ctx.fillRect(0,0,width,height);
    }
    
    // 3. CINEMATIC OVERLAY (Crucial for text contrast)
    ctx.fillStyle = 'rgba(0, 0, 0, 0.4)'; 
    ctx.fillRect(0, 0, width, height);

    // 4. TEXT RENDERING
    if (frame.text) {
        const isHorizontal = format === 'HORIZONTAL';
        
        // FONT CONFIG
        const baseSize = isHorizontal ? 60 : 80;
        ctx.font = `900 ${baseSize}px Inter`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // MEASURE & WRAP
        // Horizontal Safe Zone: 80% width. Vertical Safe Zone: 85% width.
        const maxTextWidth = width * (isHorizontal ? 0.8 : 0.85);
        const lines = getWrappedLines(ctx, frame.text.toUpperCase(), maxTextWidth);
        const lineHeight = baseSize * 1.3;
        const totalTextHeight = lines.length * lineHeight;

        // POSITIONING LOGIC
        let startY = 0;

        if (isHorizontal) {
            // HORIZONTAL: LOWER THIRD
            // Place text at bottom, leaving ~100px padding from edge
            startY = height - 150 - totalTextHeight;
            
            // Draw Subtitle Background Bar for Horizontal
            const padding = 40;
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            // Full width bar looks more cinematic for long form
            ctx.fillRect(0, startY - padding, width, totalTextHeight + (padding * 2));
        } else {
            // VERTICAL: CENTER
            startY = (height / 2) - (totalTextHeight / 2);
        }

        // DRAW TEXT LINES
        lines.forEach((line, i) => {
            const y = startY + (i * lineHeight);
            
            // Styles
            ctx.shadowColor = 'black';
            ctx.shadowBlur = isHorizontal ? 0 : 20; // Remove shadow if using black bar
            ctx.lineWidth = 8;
            ctx.strokeStyle = 'black';
            ctx.fillStyle = frame.highlight ? '#FFD700' : 'white';

            // Stroke (Outline)
            ctx.strokeText(line, width / 2, y);
            
            // Fill
            ctx.fillText(line, width / 2, y);
        });

        // SUBTEXT / TITLE (Usually smaller)
        if (frame.subText) {
            ctx.font = `700 ${baseSize * 0.5}px Cinzel`;
            ctx.fillStyle = '#FFD700'; // Gold
            ctx.shadowBlur = 0;
            ctx.lineWidth = 0;
            
            if (isHorizontal) {
                // Place subtext ABOVE the main text block
                ctx.fillText(frame.subText.toUpperCase(), width / 2, startY - 60);
            } else {
                // Place subtext BELOW the main text block
                ctx.fillText(frame.subText.toUpperCase(), width / 2, startY + totalTextHeight + 30);
            }
        }
    }
};

export const VideoRenderer: React.FC<VideoRendererProps> = (props) => {
  const { mode, videoFormat, voiceoverUrl, images, track, onReset } = props;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const framesRef = useRef<VideoFrame[]>([]);
  const startTimeRef = useRef(0);
  const [isReady, setIsReady] = useState(false);
  const [hasAutoStarted, setHasAutoStarted] = useState(false);
  const [statusMsg, setStatusMsg] = useState("Initializing...");
  const [renderLogs, setRenderLogs] = useState<string[]>([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const voiceBufferRef = useRef<AudioBuffer | null>(null);
  const bgmBufferRef = useRef<AudioBuffer | null>(null);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const audioSourcesRef = useRef<AudioBufferSourceNode[]>([]);

  const WIDTH = videoFormat === 'HORIZONTAL' ? 1920 : 1080;
  const HEIGHT = videoFormat === 'HORIZONTAL' ? 1080 : 1920;
  const mediaCache = useRef<Record<string, MediaAsset>>({});

  const addLog = (msg: string) => {
      console.log(`[Renderer] ${msg}`);
      setRenderLogs(prev => [...prev.slice(-4), msg]); 
      setStatusMsg(msg);
  };

  const fetchAndDecode = async (ctx: AudioContext, url: string, name: string): Promise<AudioBuffer | null> => {
      if (!url) return null;
      addLog(`⬇️ Downloading ${name}...`);
      try {
          // Use MediaService to download with Multi-Proxy Chain
          const blob = await mediaService.downloadAsset(url);
          const arrayBuffer = await blob.arrayBuffer();
          return await ctx.decodeAudioData(arrayBuffer);
      } catch (e: any) {
          addLog(`❌ Failed to load ${name} (All Proxies Failed): ${e.message}`);
          return null;
      }
  };

  useEffect(() => {
     addLog("Step 1: Initializing Assets...");
     const load = async () => {
         const CtxClass = window.AudioContext || (window as any).webkitAudioContext;
         const ctx = new CtxClass();
         audioCtxRef.current = ctx;

         // Load Visuals
         const urls = Array.from(new Set(Object.values(images))).filter((u): u is string => typeof u === 'string');
         await Promise.all(urls.map(url => new Promise((resolve) => {
             const img = new Image(); 
             img.crossOrigin = "anonymous"; // Important for CORS
             img.src = url; 
             img.onload = () => { mediaCache.current[url] = img; resolve(null); }; 
             img.onerror = () => { resolve(null); };
         })));
         
         // LOAD AUDIO
         const [voiceBuf, bgmBuf] = await Promise.all([
             voiceoverUrl ? fetchAndDecode(ctx, voiceoverUrl, "Voiceover") : Promise.resolve(null),
             track && track.audio ? fetchAndDecode(ctx, track.audio, "Music") : Promise.resolve(null)
         ]);
         
         voiceBufferRef.current = voiceBuf;
         bgmBufferRef.current = bgmBuf;

         // Duration Logic
         let finalDuration = 20;
         if (voiceBuf) finalDuration = voiceBuf.duration + 2;
         else if (bgmBuf) finalDuration = 30;

         // SMART DURATION CAPPING for Shorts (Issue #59)
         if (videoFormat === 'VERTICAL' && finalDuration > 60) {
             const maxDuration = 59.9; // Safe limit just under 60s for YouTube Shorts
             const originalDuration = finalDuration;
             
             if (finalDuration > 120) {
                 // For videos over 2 minutes, cap to max duration
                 finalDuration = maxDuration;
                 addLog(`🕒 Capped duration to ${finalDuration}s for Shorts (was ${originalDuration.toFixed(1)}s)`);
             } else {
                 // For shorter videos, scale proportionally to fit under the limit
                 finalDuration = Math.min(finalDuration * (maxDuration / 60), maxDuration);
                 addLog(`⚡ Scaled duration to ${finalDuration.toFixed(1)}s for Shorts (was ${originalDuration.toFixed(1)}s)`);
             }
         }

         addLog(`Step 2: Building Timeline (${finalDuration.toFixed(1)}s)...`);
         framesRef.current = buildTimeline(props, finalDuration, addLog);
         
         setIsReady(true);
         setStatusMsg("Ready. Assets Loaded.");
     };
     load();
     return () => { if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') audioCtxRef.current.close(); }
  }, [props.mode, images, voiceoverUrl, track]);

  const setupAudioMix = async (): Promise<MediaStreamTrack[]> => {
      audioSourcesRef.current.forEach(s => { try { s.stop(); } catch(e){} });
      audioSourcesRef.current = [];
      
      const ctx = audioCtxRef.current;
      if (!ctx) return [];
      const dest = ctx.createMediaStreamDestination();
      
      const totalDuration = framesRef.current.reduce((acc, f) => acc + f.duration, 0) / 1000;

      if (voiceBufferRef.current) {
          const source = ctx.createBufferSource();
          source.buffer = voiceBufferRef.current;
          source.connect(dest);
          source.start(0);
          audioSourcesRef.current.push(source);
      }

      if (bgmBufferRef.current) {
          const source = ctx.createBufferSource();
          source.buffer = bgmBufferRef.current;
          source.loop = true; 
          const gain = ctx.createGain();
          gain.gain.value = 0.3; 
          source.connect(gain);
          gain.connect(dest);
          source.start(0);
          source.stop(ctx.currentTime + totalDuration);
          audioSourcesRef.current.push(source);
      }
      return dest.stream.getAudioTracks();
  };

  const renderLoop = (ctx: CanvasRenderingContext2D) => {
      let animId = 0;
      const loop = () => {
          if (!isPlaying) return;
          const now = Date.now();
          const elapsedTotal = (now - startTimeRef.current);
          let accum = 0;
          let activeFrame = framesRef.current[0];
          
          if (!activeFrame) { setIsPlaying(false); return; }

          for (let f of framesRef.current) {
              if (elapsedTotal < accum + f.duration) { activeFrame = f; break; }
              accum += f.duration;
          }
          
          if (elapsedTotal > accum + activeFrame.duration) { 
              setIsPlaying(false); stopRecording(); return; 
          } 

          const progress = (elapsedTotal - accum) / activeFrame.duration;
          renderFrame(ctx!, activeFrame, WIDTH, HEIGHT, progress, mediaCache.current, videoFormat);
          animId = requestAnimationFrame(loop);
      };
      loop();
      return () => cancelAnimationFrame(animId);
  };

  useEffect(() => {
      if (!isPlaying || !isReady || !canvasRef.current) return;
      const ctx = canvasRef.current.getContext('2d');
      const cancelLoop = renderLoop(ctx!);
      return () => { cancelLoop && cancelLoop(); };
  }, [isPlaying, isReady]);

  const startRecording = async () => {
      if (!canvasRef.current) return;
      setStatusMsg("Rendering...");
      setIsRecording(true);
      chunksRef.current = [];
      
      if (audioCtxRef.current && audioCtxRef.current.state === 'suspended') await audioCtxRef.current.resume();

      const audioTracks = await setupAudioMix();
      const canvasStream = canvasRef.current.captureStream(30); 
      const combinedStream = new MediaStream([ ...canvasStream.getVideoTracks(), ...audioTracks ]);
      const mimeType = MediaRecorder.isTypeSupported('video/webm; codecs=vp9') ? 'video/webm; codecs=vp9' : 'video/webm';
      const recorder = new MediaRecorder(combinedStream, { mimeType, videoBitsPerSecond: 5000000 });

      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      recorder.onstop = () => {
          setStatusMsg("Finalizing...");
          const blob = new Blob(chunksRef.current, { type: mimeType });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `Project_${Date.now()}.webm`;
          a.click();
          setIsRecording(false);
          setStatusMsg("Downloaded.");
      };

      mediaRecorderRef.current = recorder;
      startTimeRef.current = Date.now();
      recorder.start();
      setIsPlaying(true);
  };

  const stopRecording = () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') mediaRecorderRef.current.stop();
      setIsPlaying(false);
  };

  useEffect(() => {
    if (isReady && !hasAutoStarted && !isRecording && !isPlaying) {
        setHasAutoStarted(true);
        setTimeout(() => startRecording(), 500);
    }
  }, [isReady, hasAutoStarted, isRecording, isPlaying]);

  // --- ZIP EXPORT LOGIC ---
  const handleExportZip = async () => {
      setStatusMsg("Packaging ZIP...");
      const zip = new JSZip();
      const assets = zip.folder("assets");
      const scriptName = "render_project";

      // 1. SAVE IMAGES
      let mainImage = "bg.png";
      let imgCounter = 0;
      for (const [key, dataUrl] of Object.entries(images)) {
          if (!dataUrl) continue;
          const base64Data = (dataUrl as string).split(',')[1];
          const fileName = `image_${imgCounter}.png`;
          if (imgCounter === 0) mainImage = fileName; // Use first image as main
          assets?.file(fileName, base64Data, {base64: true});
          imgCounter++;
      }

      // 2. SAVE VOICEOVER
      let hasVoice = false;
      if (voiceoverUrl) {
          try {
             // Voiceover usually comes from Gemini as Blob/Base64, but we fetch it to be sure
             const blob = await mediaService.downloadAsset(voiceoverUrl);
             assets?.file("voiceover.wav", blob);
             hasVoice = true;
          } catch(e) { addLog("Failed to zip voiceover"); }
      }

      // 3. SAVE MUSIC (CORS ROBUSTNESS)
      let hasMusic = false;
      let failedMusicUrl = "";

      if (track && track.audio) {
          try {
              if (track.audio.startsWith('data:')) {
                  // Handle Base64 Audio
                  const base64Data = track.audio.split(',')[1];
                  assets?.file("music.mp3", base64Data, {base64: true});
                  hasMusic = true;
              } else {
                  // Try Fetching URL with MULTI-PROXY CHAIN
                  const blob = await mediaService.downloadAsset(track.audio);
                  assets?.file("music.mp3", blob);
                  hasMusic = true;
              }
          } catch(e) { 
              addLog("⚠️ Music CORS failed completely.");
              failedMusicUrl = track.audio;
              zip.file("MISSING_MUSIC.txt", `The music file could not be downloaded due to browser security (CORS).\n\n1. Download it here: ${track.audio}\n2. Rename to 'music.mp3'\n3. Move to 'assets' folder.`);
          }
      }

      // 4. GENERATE FFMPEG SCRIPT
      const aspect = videoFormat === 'HORIZONTAL' ? '1920:1080' : '1080:1920';
      
      let ffmpegCmd = `ffmpeg -y -loop 1 -i assets/${mainImage}`;
      if (hasVoice) ffmpegCmd += ` -i assets/voiceover.wav`;
      
      // If music failed, we don't include it in the FFmpeg command automatically
      // BUT we comment it out so user can uncomment it easily
      if (hasMusic) {
          ffmpegCmd += ` -stream_loop -1 -i assets/music.mp3`;
      } else if (failedMusicUrl) {
           ffmpegCmd += ` -stream_loop -1 -i assets/music.mp3`; // Assume user downloaded it manually
      }
      
      ffmpegCmd += ` -filter_complex "`;
      ffmpegCmd += `[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0005,1.5)':d=700:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=${aspect}[v];`;
      
      // Audio Mix
      if (hasVoice && (hasMusic || failedMusicUrl)) {
          ffmpegCmd += `[1:a]volume=1.0[v1];[2:a]volume=0.3[m1];[v1][m1]amix=inputs=2:duration=first:dropout_transition=2[a]"`;
          ffmpegCmd += ` -map "[v]" -map "[a]"`;
      } else if (hasVoice) {
           ffmpegCmd = ffmpegCmd.replace(/-filter_complex ".*"/, `-filter_complex "[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0005,1.5)':d=700:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=${aspect}[v]" -map "[v]" -map 1:a`);
      } else {
           ffmpegCmd = ffmpegCmd.replace(/-filter_complex ".*"/, `-filter_complex "[0:v]scale=8000:-1,zoompan=z='min(zoom+0.0005,1.5)':d=700:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',scale=${aspect}[v]" -map "[v]"`);
      }

      ffmpegCmd += ` -c:v libx264 -preset fast -tune stillimage -c:a aac -b:a 192k -shortest output.mp4`;

      zip.file("render_mac_linux.sh", `#!/bin/bash\n${ffmpegCmd}\necho "Done! Check output.mp4"`);
      zip.file("render_windows.bat", `@echo off\n${ffmpegCmd}\npause`);
      
      // 5. DOWNLOAD
      const content = await zip.generateAsync({type:"blob"});
      const url = URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Project_Bundle_${Date.now()}.zip`;
      a.click();

      // 6. EMERGENCY FALLBACK: Force download music if zip failed to include it
      if (failedMusicUrl) {
          setTimeout(() => {
              const confirm = window.confirm("CORS blocked the music download. Open the music file in a new tab so you can save it?");
              if (confirm) window.open(failedMusicUrl, '_blank');
          }, 1000);
      }

      setStatusMsg("ZIP Exported!");
  };

  return (
    <div className="flex flex-col items-center pb-20">
        <div className={`relative ${videoFormat === 'HORIZONTAL' ? 'aspect-video w-full' : 'aspect-[9/16] h-[600px]'} bg-black border-2 border-gray-800 rounded overflow-hidden`}>
            <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} className="w-full h-full object-cover" />
            {!isPlaying && !isRecording && (
                <div className="absolute inset-0 flex flex-col items-center justify-center cursor-pointer group bg-black/40 backdrop-blur-sm z-10" onClick={() => startRecording()}>
                    <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-md group-hover:scale-110 transition-transform mb-4">▶</div>
                    <div className="text-xs font-mono text-gray-300 bg-black/50 p-2 rounded max-w-xs text-center">{renderLogs.map((l, i) => <div key={i}>{l}</div>)}</div>
                </div>
            )}
        </div>
        <div className="mt-8 flex flex-col items-center gap-4">
            <div className="text-blue-400 font-mono text-xs uppercase tracking-widest">{statusMsg}</div>
            <div className="flex gap-4">
                <button className="px-6 py-3 bg-gray-800 text-gray-300 font-bold uppercase rounded hover:bg-gray-700 transition-colors" onClick={onReset}>New Project</button>
                <button className="px-6 py-3 bg-gold text-black font-bold uppercase rounded hover:bg-yellow-500 transition-colors shadow-lg animate-pulse-slow" onClick={handleExportZip}>
                    📦 Export Asset ZIP
                </button>
            </div>
            <p className="text-[10px] text-gray-500 max-w-md text-center">
                * Use "Export Asset ZIP" to download raw images, audio, and a render script. 
                Run the script locally to generate 4K video without browser memory limits.
                <br/><br/>
                <span className="text-blue-400">UPDATED:</span> Tries 3 different proxy layers to bypass CORS. If all fail, prompts you to download music manually.
            </p>
        </div>
    </div>
  );
};

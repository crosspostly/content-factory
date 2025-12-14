
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AppStep, Scenario, ScriptureContent, HoroscopeContent, VitalityContent, Track, ProjectMode, VideoFormat, Language } from './types';
import { GeminiService } from './services/geminiService';
import { JamendoService } from './services/jamendoService';
import { StockService } from './services/stockService';
import { StepWizard } from './components/StepWizard';
import { ScenarioView } from './components/ScenarioView';
import { ImageryGenerator } from './components/ImageryGenerator';
import { AudioSelector } from './components/AudioSelector';
import { VideoRenderer } from './components/VideoRenderer';

function App() {
  const [projectMode, setProjectMode] = useState<ProjectMode>('PREDATOR');
  const [videoFormat, setVideoFormat] = useState<VideoFormat>('VERTICAL');
  const [language, setLanguage] = useState<Language>('RUSSIAN');
  const [step, setStep] = useState<AppStep>(AppStep.SCENARIO);
  
  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [scripture, setScripture] = useState<ScriptureContent | null>(null);
  const [horoscope, setHoroscope] = useState<HoroscopeContent | null>(null);
  const [vitality, setVitality] = useState<VitalityContent | null>(null);
  
  const [generatedImages, setGeneratedImages] = useState<Record<string, string>>({});
  const [selectedTrack, setSelectedTrack] = useState<Track | null>(null);
  const [voiceoverUrl, setVoiceoverUrl] = useState<string | null>(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [isAutoPilot, setIsAutoPilot] = useState(false);
  
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const addLog = useCallback((msg: string) => {
      const timestamp = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second:'2-digit' });
      setLogs(prev => [...prev, `[${timestamp}] ${msg}`]);
  }, []);

  useEffect(() => {
      logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const geminiServiceRef = useRef(new GeminiService());
  const stockServiceRef = useRef(new StockService(''));
  const jamendoServiceRef = useRef(new JamendoService(''));

  const selectProjectMode = (mode: ProjectMode) => {
    if (mode === projectMode) {
        setIsMenuOpen(false);
        return;
    }
    setProjectMode(mode);
    handleReset(); // Use reset logic
    setIsMenuOpen(false);
    
    // Set default language based on mode
    if (mode === 'HOROSCOPE') setLanguage('RUSSIAN');
    else setLanguage('ENGLISH'); 
    
    addLog(`🔄 Project Switched: ${mode}`);
  };

  const handleReset = () => {
    setStep(AppStep.SCENARIO);
    setScenario(null); setScripture(null); setHoroscope(null); setVitality(null);
    setGeneratedImages({}); setSelectedTrack(null); setVoiceoverUrl(null);
    setIsAutoPilot(false);
    addLog("🔄 New Project Started (State Cleared)");
  };

  const generateContent = async (autoMode = false, customTopic?: string, isAd: boolean = false, variant: 'DEFAULT' | 'MARATHON' = 'DEFAULT') => {
    setIsLoading(true);
    if (autoMode) { setIsAutoPilot(true); addLog("🚀 ONE-CLICK AUTO PILOT INITIATED"); }
    else { addLog(`Starting content generation (${videoFormat} | ${language} | ${variant})...`); }

    try {
        if (projectMode === 'PREDATOR') {
            addLog("Generating Battle Scenario...");
            const result = await geminiServiceRef.current.generateScenario();
            setScenario(result);
            addLog(`✅ Scenario: "${result.title}"`);
        } else if (projectMode === 'CHRISTIAN') {
            addLog(`Generating Prayer Session (${variant} Mode)...`);
            const result = await geminiServiceRef.current.generateDevotional(videoFormat, variant);
            setScripture(result);
            addLog(`✅ Scripture: "${result.title}"`);
        } else if (projectMode === 'HOROSCOPE') {
            addLog(`🔍 Generating Horoscope (${language})...`);
            const result = await geminiServiceRef.current.generateHoroscope(videoFormat, language);
            setHoroscope(result);
            addLog(`✅ Horoscope: "${result.title}"`);
        } else if (projectMode === 'VITALITY') {
            addLog(`🎯 Generating Vitality Protocol (English)...`);
            const result = await geminiServiceRef.current.generateVitality(customTopic, isAd, videoFormat);
            setVitality(result);
            addLog(`✅ Vitality: "${result.title}"`);
        }
        
        if (autoMode) {
            addLog("Auto-Pilot: Proceeding to Visual Synthesis...");
            setTimeout(() => setStep(AppStep.IMAGERY), 1000);
        }
    } catch (e: any) {
        console.error(e);
        addLog(`❌ ERROR: ${e.message}`);
        setIsAutoPilot(false);
    } finally {
        setIsLoading(false);
    }
  };
  
  // --- MOCK SYSTEM FOR DEBUGGING WITHOUT API USAGE ---
  const createMockImage = (text: string, color: string) => {
      const canvas = document.createElement('canvas');
      canvas.width = 1080; canvas.height = 1920;
      const ctx = canvas.getContext('2d');
      if (ctx) {
          ctx.fillStyle = color; ctx.fillRect(0, 0, 1080, 1920);
          ctx.fillStyle = 'white'; ctx.font = 'bold 80px sans-serif'; ctx.textAlign = 'center';
          ctx.fillText(text, 540, 960);
          ctx.strokeStyle = 'white'; ctx.lineWidth = 20; ctx.strokeRect(50, 50, 980, 1820);
      }
      return canvas.toDataURL('image/jpeg', 0.5);
  };

  const runSystemTest = () => {
      addLog("🛠️ STARTING OFFLINE MOCK TEST (NO API USAGE)...");
      setIsLoading(true);

      // 1. Force Mode to Vitality (or current)
      if (projectMode !== 'VITALITY') {
          addLog("Switching to VITALITY for test...");
          setProjectMode('VITALITY');
      }

      // 2. Create Mock Content
      const mockVitality: VitalityContent = {
          title: "TEST PROTOCOL: GINGER",
          meta_description: "Mock description",
          video_generation_prompt: "Mock prompt",
          topic: "Ginger Tea",
          thumbnail_prompt: "Ginger",
          scenes: [
              { id: 1, micro_script: "Slice ginger.", voiceover: "First, slice the root.", overlay_text: "STEP 1: SLICE", image_prompt: "Ginger" },
              { id: 2, micro_script: "Boil water.", voiceover: "Boil for 10 mins.", overlay_text: "STEP 2: BOIL", image_prompt: "Water" },
              { id: 3, micro_script: "Drink warm.", voiceover: "Drink every morning.", overlay_text: "STEP 3: DRINK", image_prompt: "Cup" }
          ]
      };
      setVitality(mockVitality);
      addLog("✅ Mock Scenario Created");

      // 3. Create Mock Images (Base64)
      const mockImages: Record<string, string> = {
          "thumbnail": createMockImage("THUMBNAIL", "#1a1a1a"),
          "scene_0": createMockImage("SCENE 1: SLICE", "#8a0b0b"),
          "scene_1": createMockImage("SCENE 2: BOIL", "#0b4a8a"),
          "scene_2": createMockImage("SCENE 3: DRINK", "#0b8a4a")
      };
      setGeneratedImages(mockImages);
      addLog("✅ Mock Images Generated (Local Base64)");

      // 4. Set Audio (Use Data URI to avoid network errors)
      // This is a 1-second silent MP3 base64
      const silentMp3 = "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//NExAAAAANIAAAAAExhdmM1OC4xMzQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/zREQAAAAA0gAAAAAAAAD/80TEAAAAANIAAAAAAAA//NExAAAAANIAAAAAAAA//NExAAAAANIAAAAAAAA//NExAAAAANIAAAAAAAA";

      setSelectedTrack({
          id: 'test_track', name: 'Mock Audio (Offline)', artist_name: 'System', duration: 180, image: '',
          audio: silentMp3
      });
      setVoiceoverUrl(null); 
      addLog("✅ Mock Audio Set (Offline Mode)");

      // 5. Jump to Render
      setTimeout(() => {
          setIsLoading(false);
          setStep(AppStep.ASSEMBLY);
          addLog("🚀 Jumping to Renderer...");
      }, 500);
  };

  const getThemeColors = (mode: ProjectMode = projectMode) => {
      if (mode === 'PREDATOR') return { accent: 'text-blood', bg: 'bg-blood', border: 'border-blood', hover: 'hover:bg-blood/20' };
      if (mode === 'HOROSCOPE') return { accent: 'text-mystic', bg: 'bg-mystic', border: 'border-mystic', hover: 'hover:bg-mystic/20' };
      if (mode === 'VITALITY') return { accent: 'text-white', bg: 'bg-gray-700', border: 'border-gray-500', hover: 'hover:bg-gray-700/50' };
      return { accent: 'text-blue-500', bg: 'bg-blue-600', border: 'border-blue-500', hover: 'hover:bg-blue-600/20' };
  };
  const theme = getThemeColors();
  const PROJECTS: { id: ProjectMode; label: string; icon: string }[] = [
      { id: 'PREDATOR', label: 'Predator Battles', icon: '🦖' },
      { id: 'CHRISTIAN', label: 'Faith & Devotion', icon: '✝️' },
      { id: 'HOROSCOPE', label: 'Mystic Horoscope', icon: '🔮' },
      { id: 'VITALITY', label: 'Silver Vitality', icon: '🌿' },
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-gray-200 font-sans selection:bg-blood selection:text-white pb-32">
      <header className="fixed top-0 w-full z-50 border-b border-gray-900 bg-[#050505]/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2 select-none">
                    <div className={`w-8 h-8 rounded-sm flex items-center justify-center overflow-hidden transition-colors ${theme.bg}`}>
                        {isAutoPilot ? <div className="w-full h-1 bg-white animate-pulse"></div> : <span className="text-xs font-bold text-white uppercase">{projectMode[0]}</span>}
                    </div>
                    <h1 className="font-display font-black text-2xl tracking-tighter text-white">
                        {projectMode === 'PREDATOR' ? 'PREDATOR' : projectMode === 'HOROSCOPE' ? 'MYSTIC' : projectMode === 'VITALITY' ? 'SILVER' : 'FAITH'}
                        <span className={theme.accent}>.AI</span>
                    </h1>
                </div>
                <div className="relative">
                    <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-gray-800 bg-[#0a0a0a] text-xs uppercase font-bold tracking-widest text-gray-400 hover:text-white hover:border-gray-600 transition-all">
                      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                      {PROJECTS.find(p => p.id === projectMode)?.label}
                      <svg className={`w-3 h-3 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                    </button>
                    {isMenuOpen && (
                        <div className="absolute top-full left-0 mt-2 w-56 bg-[#0a0a0a] border border-gray-800 rounded-lg shadow-2xl overflow-hidden z-50 animate-fade-in">
                            <div className="p-2 space-y-1">
                                {PROJECTS.map(proj => {
                                    const projTheme = getThemeColors(proj.id);
                                    const isActive = projectMode === proj.id;
                                    return (
                                        <button key={proj.id} onClick={() => selectProjectMode(proj.id)} className={`w-full flex items-center gap-3 px-3 py-2 rounded text-left transition-colors ${isActive ? 'bg-gray-900 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-900'}`}>
                                            <span className="text-lg">{proj.icon}</span>
                                            <span className={`text-xs font-bold uppercase tracking-wider ${isActive ? projTheme.accent : ''}`}>{proj.label}</span>
                                            {isActive && <span className="ml-auto text-green-500">●</span>}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <div className="flex items-center gap-4">
                 {isAutoPilot && <span className="text-[10px] font-mono text-red-500 animate-pulse border border-red-900/50 px-2 py-0.5 rounded bg-red-900/10">AUTO-PILOT ENGAGED</span>}
            </div>
        </div>
        {isMenuOpen && <div className="fixed inset-0 z-40 bg-transparent" onClick={() => setIsMenuOpen(false)}></div>}
      </header>
      <main className="pt-28 px-6">
        <StepWizard currentStep={step} />
        {step === AppStep.SCENARIO && (
            <ScenarioView 
                mode={projectMode} videoFormat={videoFormat} setVideoFormat={setVideoFormat}
                language={language} setLanguage={setLanguage}
                scenario={scenario} scripture={scripture} horoscope={horoscope} vitality={vitality}
                isLoading={isLoading} onGenerate={(topic, isAd, variant) => generateContent(false, topic, isAd, variant)}
                onAutoPilot={() => generateContent(true)} onSystemTest={runSystemTest} onNext={() => setStep(AppStep.IMAGERY)}
            />
        )}
        {step === AppStep.IMAGERY && (scenario || scripture || horoscope || vitality) && (
            <ImageryGenerator 
                mode={projectMode} videoFormat={videoFormat}
                scenario={scenario} scripture={scripture} horoscope={horoscope} vitality={vitality}
                geminiService={geminiServiceRef.current} stockService={stockServiceRef.current}
                autoStart={isAutoPilot} onImagesReady={(imgs) => setGeneratedImages(imgs)} onNext={() => setStep(AppStep.AUDIO)} onLog={addLog}
            />
        )}
        {step === AppStep.AUDIO && (
            <AudioSelector 
                mode={projectMode} scripture={scripture} horoscope={horoscope} vitality={vitality}
                geminiService={geminiServiceRef.current} jamendoService={jamendoServiceRef.current}
                autoSelect={isAutoPilot} onTrackSelected={setSelectedTrack} onVoiceoverGenerated={setVoiceoverUrl} onNext={() => setStep(AppStep.ASSEMBLY)} onLog={addLog}
            />
        )}
        {step === AppStep.ASSEMBLY && (scenario || scripture || horoscope || vitality) && selectedTrack && (
            <VideoRenderer 
                mode={projectMode} videoFormat={videoFormat}
                scenario={scenario} scripture={scripture} horoscope={horoscope} vitality={vitality}
                images={generatedImages} track={selectedTrack} voiceoverUrl={voiceoverUrl}
                onReset={handleReset}
            />
        )}
      </main>
      <div className="fixed bottom-0 left-0 w-full bg-[#0a0a0a] border-t border-gray-800 h-32 z-40 overflow-hidden font-mono text-[10px] sm:text-xs shadow-[0_-10px_20px_rgba(0,0,0,0.5)]">
          <div className="w-full h-6 bg-gray-900 flex items-center px-4 justify-between border-b border-gray-800">
              <span className="text-gray-500 uppercase tracking-widest">System Terminal</span>
          </div>
          <div className="p-2 h-24 overflow-y-auto space-y-1 text-gray-400">
              {logs.map((log, i) => (<div key={i} className="hover:text-white transition-colors border-l-2 border-transparent hover:border-gray-600 pl-2"><span className={`${theme.accent} mr-2`}>{'>'}</span>{log}</div>))}
              <div ref={logsEndRef} />
          </div>
      </div>
    </div>
  );
}
export default App;

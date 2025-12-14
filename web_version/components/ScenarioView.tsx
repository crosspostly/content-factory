
import React, { useState } from 'react';
import { Scenario, ScriptureContent, HoroscopeContent, VitalityContent, ProjectMode, VideoFormat, Language } from '../types';

interface ScenarioViewProps {
  mode: ProjectMode;
  videoFormat: VideoFormat;
  setVideoFormat: (fmt: VideoFormat) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
  scenario: Scenario | null;
  scripture: ScriptureContent | null;
  horoscope: HoroscopeContent | null;
  vitality: VitalityContent | null;
  isLoading: boolean;
  onGenerate: (topic?: string, isAd?: boolean, variant?: 'DEFAULT' | 'MARATHON') => void;
  onAutoPilot: () => void;
  onSystemTest: () => void;
  onNext: () => void;
}

const MetadataCard: React.FC<{ title?: string, description?: string, videoPrompt?: string, tags?: string[], youtubeDescription?: string }> = ({ title, description, videoPrompt, tags, youtubeDescription }) => {
    if (!title) return null;
    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        // Alert or toast could go here
    };

    return (
        <div className="border border-gray-700 bg-[#0f0f0f] p-4 rounded-lg mt-6">
            <h4 className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-3 border-b border-gray-800 pb-2">Project Metadata</h4>
            <div className="grid gap-4">
                <div><span className="text-[10px] text-gray-500 uppercase">Title</span><div className="text-white font-bold">{title}</div></div>
                {description && <div><span className="text-[10px] text-gray-500 uppercase">Internal Note</span><div className="text-gray-400 text-sm leading-snug">{description}</div></div>}
                
                {/* TAGS SECTION */}
                {tags && tags.length > 0 && (
                    <div>
                        <div className="flex justify-between items-center mb-1">
                            <span className="text-[10px] text-gray-500 uppercase">YouTube Tags</span>
                            <button onClick={() => copyToClipboard(tags.join(', '))} className="text-[10px] text-blue-400 hover:text-white uppercase font-bold">Copy Tags</button>
                        </div>
                        <div className="bg-black/50 p-2 rounded text-xs text-gray-400 font-mono break-words leading-relaxed">
                            {tags.join(', ')}
                        </div>
                    </div>
                )}

                {/* YOUTUBE DESCRIPTION */}
                {youtubeDescription && (
                    <div>
                        <div className="flex justify-between items-center mb-1">
                            <span className="text-[10px] text-gray-500 uppercase">YouTube Description</span>
                            <button onClick={() => copyToClipboard(youtubeDescription)} className="text-[10px] text-blue-400 hover:text-white uppercase font-bold">Copy Desc</button>
                        </div>
                        <div className="bg-black/50 p-2 rounded text-xs text-gray-400 font-mono whitespace-pre-wrap max-h-32 overflow-y-auto">
                            {youtubeDescription}
                        </div>
                    </div>
                )}

                {videoPrompt && <div className="mt-2 bg-black p-3 rounded border border-gray-800"><div className="text-gray-500 text-[10px] mb-1 uppercase">Image Prompt</div><div className="text-gray-300 text-xs font-mono">{videoPrompt}</div></div>}
            </div>
        </div>
    );
};

// --- SUB COMPONENTS ---

const PredatorCard: React.FC<{ scenario: Scenario }> = ({ scenario }) => (
    <div className="border border-gray-800 bg-panel p-6 rounded-lg relative overflow-hidden">
        <h3 className="text-2xl font-display text-white mb-6 border-b border-gray-800 pb-4">{scenario.title}</h3>
        <div className="space-y-4">
            {(scenario.battles || []).map((battle) => (
                <div key={battle.round} className="flex items-center gap-4 p-4 bg-darkbg border border-gray-800 rounded">
                    <div className="w-12 h-12 flex items-center justify-center bg-gray-900 rounded font-mono text-blood font-bold text-lg">#{battle.round}</div>
                    <div className="flex-grow grid grid-cols-3 gap-4 items-center text-center">
                        <div className={`font-bold ${battle.winner === battle.animal_a ? 'text-gold' : 'text-gray-400'}`}>{battle.animal_a}</div>
                        <div className="text-xs text-gray-600 font-mono">VS</div>
                        <div className={`font-bold ${battle.winner === battle.animal_b ? 'text-gold' : 'text-gray-400'}`}>{battle.animal_b}</div>
                    </div>
                </div>
            ))}
        </div>
        <MetadataCard title={scenario.title} description={scenario.meta_description} videoPrompt={scenario.video_generation_prompt} />
    </div>
);

const FaithCard: React.FC<{ scripture: ScriptureContent }> = ({ scripture }) => (
    <div className="border border-gray-800 bg-panel p-8 rounded-lg relative overflow-hidden">
        <h3 className="text-3xl font-display text-white mb-2">{scripture.title}</h3>
        
        {/* MARATHON ARCHITECT PLAN DISPLAY */}
        {scripture.marathon_outline && (
            <div className="mb-8 mt-4">
                <div className="flex items-center gap-2 mb-3">
                    <span className="text-gold font-bold uppercase tracking-widest text-xs">The Seminary Syllabus (20 Chapters)</span>
                    <div className="h-[1px] bg-gray-800 flex-grow"></div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-60 overflow-y-auto bg-black/40 p-4 rounded border border-gray-800">
                    {scripture.marathon_outline.map((title, i) => {
                        const isCurrent = i === 0;
                        return (
                            <div key={i} className={`text-xs p-2 rounded flex items-center gap-3 ${isCurrent ? 'bg-blue-900/30 border border-blue-500/50 text-white font-bold' : 'text-gray-500'}`}>
                                <span className="font-mono opacity-50">{String(i+1).padStart(2, '0')}</span>
                                <span>{title}</span>
                                {isCurrent && <span className="ml-auto text-blue-400 text-[10px] uppercase">Generating</span>}
                            </div>
                        )
                    })}
                </div>
                <div className="mt-2 text-[10px] text-gray-500 italic text-center">
                    * Browser will generate Part 01. Use <code>node scripts/marathon_worker.js</code> to generate the rest.
                </div>
            </div>
        )}

        {scripture.chapters ? (
            <div className="space-y-4 mt-4">
                <span className="text-blue-500 text-xs font-bold uppercase">Theological Course Content</span>
                {(scripture.chapters || []).map((chap, i) => (
                    <div key={i} className="bg-[#0a0a0a] p-4 rounded border border-blue-900/30">
                        <div className="text-sm font-bold text-blue-400 mb-2">{chap.chapter_title}</div>
                        <div className="text-xs text-gray-400 italic mb-2">"{chap.chapter_intro}"</div>
                        {(chap.items || []).map((item, j) => (
                             <div key={j} className="ml-2 border-l-2 border-gray-800 pl-2 mt-2">
                                 <span className="text-white text-xs font-bold">{item.title}</span>
                                 <p className="text-gray-500 text-[10px]">{item.content_spoken}</p>
                             </div>
                        ))}
                    </div>
                ))}
            </div>
        ) : (
            <>
                <p className="text-blue-400 font-mono text-sm mb-6 uppercase tracking-widest">{scripture.reference}</p>
                <div className="bg-[#0a0a0a] p-6 rounded border-l-4 border-blue-600 mb-6"><p className="font-display text-xl text-gray-200 italic leading-relaxed">"{scripture.verse}"</p></div>
                <div className="space-y-2"><h4 className="text-xs uppercase text-gray-500 font-bold tracking-wider">Apologetics / Reflection:</h4><p className="text-gray-300 leading-relaxed">{scripture.reflection}</p></div>
            </>
        )}
        <MetadataCard 
            title={scripture.title} 
            description={scripture.meta_description} 
            videoPrompt={scripture.video_generation_prompt} 
            tags={scripture.tags}
            youtubeDescription={scripture.youtube_description}
        />
    </div>
);

const HoroscopeCard: React.FC<{ horoscope: HoroscopeContent }> = ({ horoscope }) => (
    <div className="border border-purple-900 bg-panel p-8 rounded-lg relative overflow-hidden shadow-[0_0_50px_rgba(139,92,246,0.1)]">
        <h3 className="text-3xl font-display text-white mb-6 leading-tight">{horoscope.title}</h3>
        {horoscope.chapters ? (
            <div className="space-y-4 mb-6">
                <span className="text-purple-400 text-xs font-bold uppercase">Long Form Forecast</span>
                {(horoscope.chapters || []).map((chap, idx) => (
                    <div key={idx} className="bg-[#0f0a15] p-4 rounded border border-purple-800/30">
                        <div className="text-sm uppercase text-purple-300 font-bold border-b border-purple-800/50 pb-2 mb-2">{chap.chapter_title}</div>
                        <div className="text-xs text-gray-400 italic mb-3">"{chap.chapter_intro}"</div>
                        <div className="grid grid-cols-2 gap-2">
                             {(chap.items || []).map((s, i) => <div key={i} className="text-[10px] bg-black/50 p-1 rounded"><span className="text-purple-400 font-bold">{s.title}:</span> {s.content_visual}</div>)}
                        </div>
                    </div>
                ))}
            </div>
        ) : (
            horoscope.signs && <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">{(horoscope.signs || []).map((item, idx) => <div key={idx} className="bg-[#0f0a15] p-3 rounded border border-purple-800/30"><div className="text-[10px] uppercase text-purple-400 font-bold mb-1">{item.sign}</div><div className="text-xs text-white leading-tight">{item.prediction_visual}</div></div>)}</div>
        )}
        <MetadataCard 
            title={horoscope.title} 
            description={horoscope.meta_description} 
            videoPrompt={horoscope.video_generation_prompt}
            tags={horoscope.tags}
            youtubeDescription={horoscope.youtube_description}
        />
    </div>
);

const VitalityCard: React.FC<{ vitality: VitalityContent }> = ({ vitality }) => (
    <div className="border border-gray-600 bg-black p-8 rounded-lg relative overflow-hidden shadow-[0_0_60px_rgba(255,255,255,0.05)]">
        <h3 className="text-3xl font-display text-white mb-6 border-b border-gray-800 pb-4">{vitality.title}</h3>
        <div className="mb-6 p-4 bg-[#0a0a0a] border border-gray-800 rounded"><div className="text-xs text-green-500 font-bold uppercase mb-2">Thumbnail Strategy</div><p className="text-gray-300 italic text-sm">"{vitality.thumbnail_prompt}"</p></div>

        {vitality.chapters ? (
             <div className="space-y-4">
                 <span className="text-white text-xs font-bold uppercase">Full Protocol (Long Form)</span>
                 {(vitality.chapters || []).map((chap, i) => (
                     <div key={i} className="bg-[#111] p-4 rounded border border-gray-700">
                         <div className="text-white font-bold mb-2">{chap.chapter_title}</div>
                         <div className="text-xs text-gray-400 mb-2">{chap.chapter_intro}</div>
                         {(chap.items || []).map((item, k) => (
                             <div key={k} className="ml-4 text-xs text-gray-500 list-disc display-list-item">{item.title}: {item.content_visual}</div>
                         ))}
                     </div>
                 ))}
             </div>
        ) : (
             <div className="space-y-4">{(vitality.scenes || []).map(scene => <div key={scene.id} className="flex items-start gap-4 p-4 bg-[#0a0a0a] rounded border border-gray-800"><div className="w-8 h-8 rounded-full bg-white text-black font-bold flex items-center justify-center text-sm flex-shrink-0">{scene.id}</div><div className="w-full"><div className="flex justify-between items-start mb-2"><span className="text-lg font-bold text-white font-display tracking-tight">{scene.overlay_text}</span></div><div className="mb-2 text-sm text-gray-300 font-serif border-l-2 border-gray-700 pl-3">{scene.micro_script}</div></div></div>)}</div>
        )}
        <MetadataCard 
            title={vitality.title} 
            description={vitality.meta_description} 
            videoPrompt={vitality.video_generation_prompt} 
            tags={vitality.tags}
            youtubeDescription={vitality.youtube_description}
        />
    </div>
);

// --- MAIN COMPONENT ---

export const ScenarioView: React.FC<ScenarioViewProps> = ({ mode, videoFormat, setVideoFormat, language, setLanguage, scenario, scripture, horoscope, vitality, isLoading, onGenerate, onAutoPilot, onSystemTest, onNext }) => {
  const [customTopic, setCustomTopic] = useState("");
  const [isAdMode, setIsAdMode] = useState(false);
  const [devotionalVariant, setDevotionalVariant] = useState<'DEFAULT' | 'MARATHON'>('DEFAULT');

  const isVitality = mode === 'VITALITY';
  const isChristian = mode === 'CHRISTIAN';
  
  let accentColor = 'text-blue-500';
  let buttonColor = 'bg-blue-600';
  if (mode === 'PREDATOR') { accentColor = 'text-blood'; buttonColor = 'bg-blood'; }
  else if (mode === 'HOROSCOPE') { accentColor = 'text-mystic'; buttonColor = 'bg-mystic'; }
  else if (isVitality) { accentColor = 'text-white'; buttonColor = 'bg-gray-800 border border-gray-600 hover:bg-gray-700'; }

  const hasContent = (mode === 'PREDATOR' && scenario) || (mode === 'CHRISTIAN' && scripture) || (mode === 'HOROSCOPE' && horoscope) || (mode === 'VITALITY' && vitality);

  const handleChristianModeSelect = (type: 'SHORTS' | 'LONG_DEFAULT' | 'LONG_MARATHON') => {
      if (type === 'SHORTS') {
          setVideoFormat('VERTICAL');
          setDevotionalVariant('DEFAULT');
      } else if (type === 'LONG_DEFAULT') {
          setVideoFormat('HORIZONTAL');
          setDevotionalVariant('DEFAULT');
      } else if (type === 'LONG_MARATHON') {
          setVideoFormat('HORIZONTAL');
          setDevotionalVariant('MARATHON');
      }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-display font-bold text-white tracking-widest uppercase"><span className={accentColor}>Step 1:</span> Generator</h2>
      </div>

      {!hasContent && (
        <div className="flex flex-col gap-6 py-10 items-center">
            
            {/* --- CHRISTIAN MODE SELECTION --- */}
            {isChristian && (
                <div className="w-full max-w-2xl bg-[#0a0a0a] border border-gray-800 rounded-xl p-4 flex flex-col md:flex-row gap-4">
                     <button 
                        onClick={() => handleChristianModeSelect('SHORTS')}
                        className={`flex-1 p-4 rounded-lg border transition-all text-left group ${videoFormat === 'VERTICAL' ? 'bg-blue-900/20 border-blue-500' : 'bg-[#111] border-gray-800 hover:border-gray-600'}`}
                     >
                         <div className="text-lg mb-1">📱 <span className="font-bold text-white uppercase">Truth Bombs</span></div>
                         <div className="text-[10px] text-gray-400">Shorts: Apologetics & Hard Truth. Vertical. Viral hook.</div>
                     </button>

                     <button 
                        onClick={() => handleChristianModeSelect('LONG_DEFAULT')}
                        className={`flex-1 p-4 rounded-lg border transition-all text-left group ${(videoFormat === 'HORIZONTAL' && devotionalVariant === 'DEFAULT') ? 'bg-blue-900/20 border-blue-500' : 'bg-[#111] border-gray-800 hover:border-gray-600'}`}
                     >
                         <div className="text-lg mb-1">🎥 <span className="font-bold text-white uppercase">Expository Sermon</span></div>
                         <div className="text-[10px] text-gray-400">Deep Theology. 25 Points. Horizontal. Reformed style.</div>
                     </button>

                     <button 
                        onClick={() => handleChristianModeSelect('LONG_MARATHON')}
                        className={`flex-1 p-4 rounded-lg border transition-all text-left group ${(videoFormat === 'HORIZONTAL' && devotionalVariant === 'MARATHON') ? 'bg-gold/10 border-gold' : 'bg-[#111] border-gray-800 hover:border-gray-600'}`}
                     >
                         <div className="text-lg mb-1">♾️ <span className="font-bold text-white uppercase text-gold">Seminary Course</span></div>
                         <div className="text-[10px] text-gray-400">Systematic Theology. 20 Chapters. <span className="text-gold font-bold">Infinite Series.</span></div>
                     </button>
                </div>
            )}

            {/* --- STANDARD FORMAT TOGGLE (Hidden for Christian Mode as it's handled above) --- */}
            {!isChristian && (
                <div className="flex items-center gap-4">
                    <div className="flex bg-[#121212] p-1 rounded-lg border border-gray-800">
                        <button onClick={() => setVideoFormat('VERTICAL')} className={`px-4 py-2 rounded text-xs font-bold uppercase transition-colors ${videoFormat === 'VERTICAL' ? 'bg-white text-black' : 'text-gray-500 hover:text-white'}`}>Shorts (9:16)</button>
                        <button onClick={() => setVideoFormat('HORIZONTAL')} className={`px-4 py-2 rounded text-xs font-bold uppercase transition-colors ${videoFormat === 'HORIZONTAL' ? 'bg-white text-black' : 'text-gray-500 hover:text-white'}`}>Video (16:9)</button>
                    </div>
                    
                    {/* Language Toggle */}
                    {mode === 'HOROSCOPE' && (
                        <div className="flex bg-[#121212] p-1 rounded-lg border border-gray-800">
                            <button onClick={() => setLanguage('RUSSIAN')} className={`px-4 py-2 rounded text-xs font-bold uppercase transition-colors ${language === 'RUSSIAN' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-white'}`}>RU</button>
                            <button onClick={() => setLanguage('ENGLISH')} className={`px-4 py-2 rounded text-xs font-bold uppercase transition-colors ${language === 'ENGLISH' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-white'}`}>EN</button>
                        </div>
                    )}
                </div>
            )}

            {isVitality && (
                <div className="w-full max-w-md flex flex-col gap-4">
                    <input type="text" placeholder="Enter Topic (e.g. Back Pain) or leave empty" className="w-full bg-[#0a0a0a] border border-gray-700 p-4 text-white rounded focus:border-white outline-none text-center" value={customTopic} onChange={(e) => setCustomTopic(e.target.value)} />
                    <div className="flex items-center justify-center gap-3 bg-[#111] p-3 rounded border border-gray-800 cursor-pointer hover:bg-[#1a1a1a] transition-colors" onClick={() => setIsAdMode(!isAdMode)}>
                        <div className={`w-12 h-6 rounded-full p-1 transition-colors ${isAdMode ? 'bg-blue-600' : 'bg-gray-700'}`}><div className={`w-4 h-4 bg-white rounded-full transition-transform ${isAdMode ? 'translate-x-6' : 'translate-x-0'}`}></div></div>
                        <div className="flex flex-col items-start"><span className={`text-sm font-bold uppercase ${isAdMode ? 'text-blue-400' : 'text-gray-400'}`}>{isAdMode ? "Partner Ad Mode (ON)" : "Viral Growth Mode (OFF)"}</span></div>
                    </div>
                </div>
            )}

            <div className="flex flex-col sm:flex-row justify-center items-center gap-6 w-full">
                <button onClick={() => onGenerate(customTopic || undefined, isAdMode, devotionalVariant)} disabled={isLoading} className="group relative px-8 py-4 bg-transparent border border-gray-700 text-gray-300 font-display font-bold uppercase tracking-[0.2em] hover:border-gray-500 hover:text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden w-full sm:w-auto">
                    <span className="relative z-10 flex items-center justify-center gap-3">{isLoading ? "Processing..." : "Generate Script"}</span>
                </button>
                <button onClick={onAutoPilot} disabled={isLoading} className={`group relative px-10 py-5 ${buttonColor} text-white font-display font-bold uppercase tracking-[0.2em] shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden w-full sm:w-auto`}>
                    <span className="relative z-10 flex items-center justify-center gap-3 text-lg">{isLoading ? "Initializing..." : <><span className={isVitality ? 'text-white' : 'text-gold'}>⚡</span> One-Click Auto Pilot</>}</span>
                </button>
            </div>
            {isVitality && (
                 <button onClick={onSystemTest} disabled={isLoading} className="mt-4 px-6 py-2 bg-gray-800 border border-gray-700 text-xs text-gray-400 uppercase tracking-widest hover:text-white hover:border-gray-500 transition-colors">
                     🛠️ MOCK TEST (NO API)
                 </button>
            )}
        </div>
      )}

      {hasContent && (
          <div className="space-y-6">
              {mode === 'PREDATOR' && scenario && <PredatorCard scenario={scenario} />}
              {mode === 'CHRISTIAN' && scripture && <FaithCard scripture={scripture} />}
              {mode === 'HOROSCOPE' && horoscope && <HoroscopeCard horoscope={horoscope} />}
              {mode === 'VITALITY' && vitality && <VitalityCard vitality={vitality} />}
              <div className="flex justify-end pt-4">
                <button onClick={onNext} className="px-6 py-3 bg-white text-black font-bold uppercase tracking-wider hover:bg-gray-200 transition-colors">Confirm & Proceed &rarr;</button>
            </div>
          </div>
      )}
    </div>
  );
};

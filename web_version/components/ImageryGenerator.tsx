
import React, { useEffect, useState, useRef } from 'react';
import { Scenario, GeneratedImage, ProjectMode, ScriptureContent, HoroscopeContent, VitalityContent, VideoFormat } from '../types';
import { GeminiService } from '../services/geminiService';
import { MediaService } from '../services/mediaService';

interface ImageryGeneratorProps {
  mode: ProjectMode;
  videoFormat: VideoFormat;
  scenario?: Scenario | null;
  scripture?: ScriptureContent | null;
  horoscope?: HoroscopeContent | null;
  vitality?: VitalityContent | null;
  geminiService: GeminiService;
  stockService: any; // Legacy prop kept for compatibility
  onImagesReady: (images: Record<string, string>) => void;
  onNext: () => void;
  autoStart?: boolean;
  onLog: (msg: string) => void;
}

const mediaService = new MediaService();

const getPredatorQueue = (scenario: Scenario): GeneratedImage[] => {
    const images: GeneratedImage[] = [];
    const uniqueAnimals = new Set<string>();
    (scenario.battles || []).forEach(b => { uniqueAnimals.add(b.animal_a); uniqueAnimals.add(b.animal_b); });
    uniqueAnimals.forEach(animal => images.push({ id: animal, url: '', status: 'pending', prompt: `Vertical 9:16. Subject: angry ${animal} roaring closeup. Dark background.` }));
    (scenario.battles || []).forEach(battle => images.push({ id: `${battle.winner}_vs_${battle.winner === battle.animal_a ? battle.animal_b : battle.animal_a}`, url: '', status: 'pending', prompt: `Vertical 9:16. Subject: ${battle.winner} fighting ${battle.winner === battle.animal_a ? battle.animal_b : battle.animal_a}. Cinematic.` }));
    return images;
};

const getLongFormQueue = (format: VideoFormat, chapters: any[], baseTheme: string, mode: string, title: string = ""): GeneratedImage[] => {
    const images: GeneratedImage[] = [];
    const isHorizontal = format === 'HORIZONTAL';
    const aspectRatio = isHorizontal ? "16:9" : "9:16";
    
    // Standardize prompt structure for easy extraction
    images.push({ id: 'intro_bg', url: '', status: 'pending', prompt: `${aspectRatio}. Subject: ${baseTheme}. Cinematic lighting.` });
    
    (chapters || []).forEach((chap, idx) => {
        images.push({ 
            id: `chapter_${idx}`, 
            url: '', 
            status: 'pending', 
            prompt: `${aspectRatio}. Subject: ${chap.chapter_title} abstract concept. Atmospheric.` 
        });
    });

    images.push({ id: 'outro_bg', url: '', status: 'pending', prompt: `${aspectRatio}. Subject: Sunset peace. Theme: ${baseTheme}.` });
    return images;
};

const getVitalityQueue = (format: VideoFormat, content: VitalityContent): GeneratedImage[] => {
    const images: GeneratedImage[] = [];
    const isHorizontal = format === 'HORIZONTAL';
    const aspectRatio = isHorizontal ? "16:9" : "9:16";
    // HARDCODED STYLE OVERRIDE
    const stylePrompt = "STYLE: Minimalist White Chalk drawing on a clean Black Blackboard. Medical schematic illustration.";

    if (content.chapters) {
        // Long Form
        images.push({ id: 'thumbnail', url: '', status: 'pending', prompt: `${aspectRatio}. ${stylePrompt} Subject: ${content.title} medical diagram.` });
        
        content.chapters.forEach((chap, idx) => {
             images.push({ 
                id: `chapter_${idx}`, 
                url: '', 
                status: 'pending', 
                prompt: `${aspectRatio}. ${stylePrompt} Subject: ${chap.chapter_title} anatomy.` 
            });
        });
    } else {
        // Shorts
        images.push({ id: 'thumbnail', url: '', status: 'pending', prompt: `Vertical 9:16. ${stylePrompt} Subject: ${content.title} diagram.` });
        (content.scenes || []).forEach((scene, idx) => {
            images.push({ 
                id: `scene_${idx}`, 
                url: '', 
                status: 'pending', 
                prompt: `Vertical 9:16. ${stylePrompt} Subject: ${scene.image_prompt}.` 
            });
        });
    }
    return images;
};

export const ImageryGenerator: React.FC<ImageryGeneratorProps> = ({ mode, videoFormat, scenario, scripture, horoscope, vitality, geminiService, onImagesReady, onNext, autoStart, onLog }) => {
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (images.length > 0) return;
    let initialImages: GeneratedImage[] = [];

    if (mode === 'PREDATOR' && scenario) {
        initialImages = getPredatorQueue(scenario);
    } else if (mode === 'CHRISTIAN' && scripture) {
        if (scripture.chapters) {
            initialImages = getLongFormQueue(videoFormat, scripture.chapters, scripture.visual_prompt, 'faith', scripture.title);
        } else {
            // INCREASED TO 8 IMAGES FOR SHORTS TO SUPPORT FAST CUTS (1-2s rule)
            for(let i=1; i<=8; i++) {
                initialImages.push({ 
                    id: `scene_${i}`, 
                    url: '', 
                    status: 'pending', 
                    // Varying the prompt slightly for each scene
                    prompt: `Vertical 9:16. Subject: ${scripture.visual_prompt}. Variation ${i} (Close-up or Wide angle). Golden Hour Lighting.` 
                });
            }
        }
    } else if (mode === 'HOROSCOPE' && horoscope) {
        if (horoscope.chapters) {
            initialImages = getLongFormQueue(videoFormat, horoscope.chapters, horoscope.visual_theme, 'horo', horoscope.title);
        } else {
             const theme = horoscope.visual_theme;
             ['intro_bg', 'element_fire', 'element_earth', 'element_air', 'element_water', 'outro_bg'].forEach(id => {
                 initialImages.push({ id, url: '', status: 'pending', prompt: `Vertical 9:16. Subject: ${theme} mystical abstract.` });
             });
        }
    } else if (mode === 'VITALITY' && vitality) {
        initialImages = getVitalityQueue(videoFormat, vitality);
    }

    setImages(initialImages);
    if(initialImages.length > 0) onLog(`Queue initialized: ${initialImages.length} assets.`);
  }, [mode, videoFormat, scenario, scripture, horoscope, vitality, images.length, onLog]);

  useEffect(() => {
    if (autoStart && images.length > 0 && !isGenerating && images.some(img => img.status === 'pending')) {
        onLog("Auto-Pilot: Starting generation...");
        startGeneration();
    }
  }, [autoStart, images, isGenerating]);

  useEffect(() => {
      if (cooldown > 0) { const timer = setTimeout(() => setCooldown(c => c - 1), 1000); return () => clearTimeout(timer); }
  }, [cooldown]);

  const delay = (ms: number) => new Promise(res => setTimeout(res, ms));
  const retryFailed = () => { setImages(images.map(img => img.status === 'error' ? { ...img, status: 'pending' as const } : img)); if (!isGenerating) setTimeout(() => startGeneration(), 100); };

  const startGeneration = async () => {
    setIsGenerating(true);
    let completed = 0;
    // Fast generation for AI images
    const safetyDelay = 500; 
    const queue = [...images]; 

    for (let i = 0; i < queue.length; i++) {
        if (queue[i].status === 'completed') { completed++; continue; }
        if (queue[i].status !== 'pending') continue;

        if (i > 0 && completed > 0) { setCooldown(safetyDelay / 1000); await delay(safetyDelay); }

        queue[i].status = 'loading'; setImages([...queue]); 
        
        onLog(`Generating [${i+1}/${queue.length}]: ${queue[i].id} via Gemini AI...`);

        try {
            const url = await geminiService.generateImage(queue[i].prompt, videoFormat);
            queue[i].url = url; 
            queue[i].status = 'completed'; 
            onLog(`✅ Generated AI Image: ${queue[i].id}`);
        } catch (aiErr: any) {
            console.error(aiErr);
            onLog(`❌ Failed AI Generation: ${queue[i].id}`);
            queue[i].status = 'error';
            
            // Fallback to stock Photo only if AI fails (Last resort)
            try {
                const orient = videoFormat === 'HORIZONTAL' ? 'landscape' : 'portrait';
                onLog(`⚠️ AI Failed. Trying Backup Stock Photo...`);
                // Simple keyword extraction for backup
                const cleanQuery = queue[i].prompt.split('Subject:')[1]?.split('.')[0] || "abstract background";
                const mediaUrl = await mediaService.getBackupImage(cleanQuery, orient);
                if (mediaUrl) {
                    queue[i].url = mediaUrl;
                    queue[i].status = 'completed';
                    onLog(`✅ Recovered with Stock Photo.`);
                }
            } catch (e) {}
        }
        completed++; setProgress((completed / queue.length) * 100); setImages([...queue]);
    }
    setIsGenerating(false); onLog("Visual Synthesis Finished.");
    const imageMap: Record<string, string> = {};
    queue.forEach(img => { if (img.url) imageMap[img.id] = img.url; });
    onImagesReady(imageMap);
    if (queue.every(i => i.status === 'completed') && autoStart) setTimeout(onNext, 1500);
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center space-y-4"><h2 className="text-3xl font-display font-bold text-white uppercase">Step 2: Visuals (AI Only)</h2></div>
      <div className="flex flex-col items-center justify-center space-y-6">
        {!isGenerating && (
            <div className="flex gap-4">
                {images.some(i => i.status === 'pending') && <button onClick={() => startGeneration()} className="px-8 py-4 bg-blue-600 text-white font-bold uppercase">Start Generation</button>}
                {images.some(i => i.status === 'error') && <button onClick={retryFailed} className="px-8 py-4 bg-gray-700 text-white font-bold uppercase">Retry Failed</button>}
            </div>
        )}
        {isGenerating && <div className="w-full max-w-md h-2 bg-gray-800 rounded-full"><div className="h-full bg-blue-600" style={{ width: `${progress}%`, transition: 'width 0.5s ease' }}></div></div>}
      </div>
      <div className={`grid gap-4 ${videoFormat === 'HORIZONTAL' ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-2 md:grid-cols-5'}`}>
        {images.map((img) => (
            <div key={img.id} className={`relative ${videoFormat === 'HORIZONTAL' ? 'aspect-video' : 'aspect-[9/16]'} bg-gray-900 rounded overflow-hidden border border-gray-800`}>
                {img.url ? (
                    img.url.startsWith('data:') ?
                    <img src={img.url} className="w-full h-full object-cover" /> :
                    <div className="w-full h-full bg-gray-800 flex items-center justify-center text-xs text-gray-500">External Image</div>
                ) : <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-500">{img.status}</div>}
                
                <div className="absolute bottom-0 left-0 bg-black/70 p-1 text-[10px] text-white w-full truncate">{img.id}</div>
                {img.url && img.url.startsWith('data:') && <div className="absolute top-1 right-1 bg-purple-500/80 text-white text-[8px] font-bold px-1 rounded">GEMINI AI</div>}
            </div>
        ))}
      </div>
      {images.every(i => i.status === 'completed') && !autoStart && <div className="flex justify-end pt-8"><button onClick={onNext} className="px-6 py-3 bg-white text-black font-bold uppercase">Next &rarr;</button></div>}
    </div>
  );
};

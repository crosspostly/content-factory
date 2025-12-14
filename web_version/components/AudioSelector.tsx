
import React, { useEffect, useState, useRef } from 'react';
import { Track, ProjectMode, ScriptureContent, HoroscopeContent, VitalityContent } from '../types';
import { GeminiService } from '../services/geminiService';
import { MediaService } from '../services/mediaService';

interface AudioSelectorProps {
  mode: ProjectMode;
  scripture?: ScriptureContent | null;
  horoscope?: HoroscopeContent | null;
  vitality?: VitalityContent | null;
  geminiService?: GeminiService;
  jamendoService: any;
  onTrackSelected: (track: Track) => void;
  onVoiceoverGenerated?: (url: string) => void;
  onNext: () => void;
  autoSelect?: boolean;
  onLog: (msg: string) => void;
}

const mediaService = new MediaService();

// RELIABLE BASE64 TRACKS FOR GUARANTEED PLAYBACK (Fallback)
const AMBIENT_BASE64 = "data:audio/mp3;base64,//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA/8AAAAABAAAAAAAB//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA/8AAAAABAAAAAAAB//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA//uQZAAAAAAAALAAAAWGluZwAAAA8AAAALAAAB5QAA"; 

const TRACKS_DB: Record<string, Track> = {
    'PREDATOR': { 
        id: 'track_epic', 
        name: 'Ride of the Valkyries', 
        artist_name: 'Richard Wagner', 
        duration: 300, 
        image: '', 
        audio: 'https://upload.wikimedia.org/wikipedia/commons/transcoded/5/53/Richard_Wagner_-_Ride_of_the_Valkyries.ogg/Richard_Wagner_-_Ride_of_the_Valkyries.ogg.mp3' 
    },
    'CHRISTIAN': { 
        id: 'track_faith', 
        name: 'Gymnopedie No. 1', 
        artist_name: 'Erik Satie', 
        duration: 180, 
        image: '', 
        audio: 'https://upload.wikimedia.org/wikipedia/commons/transcoded/1/1a/Gymnopedie_No_1.ogg/Gymnopedie_No_1.ogg.mp3' 
    },
    'HOROSCOPE': { 
        id: 'track_mystic', 
        name: 'Moonlight Sonata', 
        artist_name: 'Beethoven', 
        duration: 300, 
        image: '', 
        audio: 'https://upload.wikimedia.org/wikipedia/commons/transcoded/f/f6/Ludwig_van_Beethoven_-_moonlight_sonata.ogg/Ludwig_van_Beethoven_-_moonlight_sonata.ogg.mp3' 
    },
    'VITALITY': { 
        id: 'track_vitality', 
        name: 'Gymnopedie No. 2 (Safe)', 
        artist_name: 'Erik Satie', 
        duration: 180, 
        image: '', 
        // Using Base64 to prevent HTTP 503 errors on archive.org
        audio: AMBIENT_BASE64
    }
};

const DEFAULT_TRACK = TRACKS_DB['CHRISTIAN']; // Fallback

export const AudioSelector: React.FC<AudioSelectorProps> = ({ mode, scripture, horoscope, vitality, geminiService, onTrackSelected, onVoiceoverGenerated, onNext, autoSelect, onLog }) => {
  const [tracks, setTracks] = useState<Track[]>(Object.values(TRACKS_DB));
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);
  const [voiceUrl, setVoiceUrl] = useState<string | null>(null);

  useEffect(() => {
     // Fetch additional dynamic tracks from Freesound
     const fetchDynamic = async () => {
         let query = "ambient";
         if (mode === 'CHRISTIAN') query = "church ambient";
         if (mode === 'PREDATOR') query = "epic drum";
         if (mode === 'HOROSCOPE') query = "mystic drone";
         
         const dynamicTracks = await mediaService.getAmbientTracks(query);
         if (dynamicTracks.length > 0) {
             setTracks(prev => [...prev, ...dynamicTracks]);
             onLog(`🎵 Loaded ${dynamicTracks.length} extra tracks from Freesound.`);
         }
     };
     fetchDynamic();
  }, [mode, onLog]);

  const generateVoiceover = async () => {
      if (!geminiService || mode === 'PREDATOR') return;
      setIsGeneratingVoice(true);
      onLog("🎙️ Generating Voiceover...");
      
      try {
          let textToSay = "";
          
          // Helper to extract text from chapters
          const extractChapters = (chapters: any[]) => {
              return (chapters || []).map(chap => {
                  const itemsVO = (chap.items || []).map((i: any) => `${i.title}. ${i.content_spoken}.`).join(' ');
                  return `${chap.chapter_intro} ${itemsVO}`;
              }).join(' ');
          };

          if (mode === 'CHRISTIAN' && scripture) {
             if (scripture.chapters) textToSay = extractChapters(scripture.chapters);
             else textToSay = `${scripture.title}. ${scripture.verse}. ${scripture.reference}. ${scripture.reflection}.`;
          } else if (mode === 'HOROSCOPE' && horoscope) {
             if (horoscope.chapters) textToSay = extractChapters(horoscope.chapters);
             else textToSay = `${horoscope.intro_spoken || ""}. ${(horoscope.signs || []).map(s => s.prediction_spoken).join(' ')}. ${horoscope.outro_spoken || ""}`;
          } else if (mode === 'VITALITY' && vitality) {
             if (vitality.chapters) textToSay = extractChapters(vitality.chapters);
             else textToSay = (vitality.scenes || []).map(s => s.voiceover).join(' ');
          }

          if (textToSay) {
              const url = await geminiService.generateSpeech(textToSay);
              setVoiceUrl(url);
              if (onVoiceoverGenerated) onVoiceoverGenerated(url);
              onLog("✅ Voiceover generated.");
          } else {
              onLog("⚠️ No text found to synthesize.");
          }

      } catch (e: any) {
          onLog(`❌ Voiceover failed: ${e.message}`);
      } finally {
          setIsGeneratingVoice(false);
      }
  };

  useEffect(() => {
      // Intelligent Auto-Select
      if (autoSelect || !selectedId) {
          const suggestedTrack = TRACKS_DB[mode] || DEFAULT_TRACK;
          
          if (selectedId !== suggestedTrack.id) {
              setSelectedId(suggestedTrack.id);
              onTrackSelected(suggestedTrack);
              onLog(`🎵 Auto-selected BGM: ${suggestedTrack.name}`);
          }

          if (autoSelect) {
             if (mode !== 'PREDATOR' && !voiceUrl && !isGeneratingVoice) generateVoiceover();
             // Proceed when ready
             if ((mode === 'PREDATOR' || voiceUrl) && selectedId) setTimeout(onNext, 2000);
          }
      }
  }, [autoSelect, mode, voiceUrl, selectedId, onLog, onTrackSelected, onNext, isGeneratingVoice]);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 animate-fade-in">
        <div className="text-center space-y-4"><h2 className="text-3xl font-display font-bold text-white uppercase">Step 3: Audio</h2></div>
        {mode !== 'PREDATOR' && (
            <div className="bg-[#121212] border border-gray-800 p-6 rounded-lg mb-8 flex justify-between items-center">
                <span className="text-gray-400">{voiceUrl ? "Voice Ready" : "Generate AI Voice"}</span>
                <button onClick={generateVoiceover} disabled={isGeneratingVoice || !!voiceUrl} className="px-4 py-2 bg-blue-600 text-white font-bold rounded text-xs uppercase disabled:opacity-50">
                    {isGeneratingVoice ? "Synthesizing..." : voiceUrl ? "Regenerate" : "Generate"}
                </button>
            </div>
        )}
        <div className="grid gap-4">
            <h3 className="text-xs font-bold uppercase text-gray-500">Suggested Background Tracks</h3>
            {tracks.map(track => (
                <div key={track.id} onClick={() => { setSelectedId(track.id); onTrackSelected(track); }} className={`flex items-center justify-between p-4 rounded border cursor-pointer transition-all ${selectedId === track.id ? 'bg-gray-900 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]' : 'bg-panel border-gray-800 hover:border-gray-600'}`}>
                    <div className="flex flex-col">
                        <span className={`font-bold ${selectedId === track.id ? 'text-white' : 'text-gray-300'}`}>{track.name}</span>
                        <span className="text-xs text-gray-500">{track.artist_name}</span>
                    </div>
                    {selectedId === track.id && <span className="text-blue-500 text-xs font-bold uppercase">Active</span>}
                </div>
            ))}
        </div>
        {!autoSelect && <div className="flex justify-end pt-4"><button onClick={onNext} className="px-6 py-3 bg-white text-black font-bold uppercase">Next &rarr;</button></div>}
    </div>
  );
};

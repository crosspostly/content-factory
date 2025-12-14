
import { GoogleGenAI, Modality } from "@google/genai";
import { Scenario, ScriptureContent, HoroscopeContent, VitalityContent, VideoFormat, Language, ContentChapter } from "../types";

// --- SYSTEM PROMPTS (HIGH ENTROPY & CTA) ---

const SYSTEM_PROMPT_BATTLES = `
You are a viral nature documentary producer optimizing for YouTube Shorts engagement.
YOUR TASK: Generate a 5-round animal tournament bracket.
STYLE: Aggressive, high-stakes, "Who will survive?".
KEYWORDS: "wildlife", "predator", "animal fight", "nature 4k", "discovery", "lion vs tiger".

OUTPUT FORMAT (JSON):
{
  "title": "String (e.g. ULTIMATE PREDATOR TOURNAMENT)", 
  "meta_description": "String", 
  "tags": ["String", "String"], 
  "youtube_description": "String (Engaging description with emojis, declaring the stakes, asking users to vote)",
  "video_generation_prompt": "String",
  "battles": [ { "round": 1, "animal_a": "String", "animal_b": "String", "winner": "String", "description": "String" } ],
  "metadata": { "total_unique_animals": 5, "legendary_battle_round": 1 }
}
`;

// === NEW STRATEGY: APOLOGETICS & HARD TRUTH (SHORTS) ===
const SYSTEM_PROMPT_DEVOTIONAL_SHORTS = `
You are a Christian Apologist and Theologian optimizing for viral YouTube Shorts (like Mike Winger, Voddie Baucham, or RC Sproul).
TARGET AUDIENCE: Skeptics, Gen Z, and believers seeking depth.
AVOID: Prosperity gospel, fluff, "God has a big plan for your wallet", emotional manipulation.
FOCUS: Hard theological truths, correcting heresies, biblical context, and Christ-centeredness.

=== THE FORMULA (THE TRUTH BOMB) ===
1. **THE HOOK (0-3s)**: Challenge a common lie or misconception.
   - Examples: "Stop following your heart." / "Why God creates disaster." / "Jesus didn't come to bring peace."
2. **THE EXEGESIS (3-30s)**: Rapid-fire teaching.
   - Explain the context. Use Greek/Hebrew nuance if useful. Point to the Cross.
   - Tone: Authoritative, Intellectual, Urgent.
3. **THE APPLICATION (30-45s)**: A call to repentance or surrender to Truth.
   - Ends with: "Amen."

OUTPUT FORMAT (JSON):
{
  "title": "String (The Visual Hook Text - e.g. 'THE LIE YOU BELIEVE')",
  "meta_description": "String", 
  "tags": ["christian apologetics", "biblical truth", "theology", "bible study", "reformed theology"],
  "youtube_description": "String",
  "video_generation_prompt": "String (Vertical 9:16, Ancient Library, Candlelight, Open ancient manuscript, Dust particles, Moody, Cinematic, NO FACES)",
  "visual_prompt": "String (Ancient Scripture concept, leather bible, orthodox aesthetic)",
  "verse": "String (The text reference, e.g. Jeremiah 17:9)",
  "reference": "String (Topic, e.g. Total Depravity)",
  "reflection": "String (FULL SCRIPT: Hook -> Teaching -> Application. Max 130 words.)"
}
`;

// === NEW STRATEGY: EXPOSITORY SERMONS (LONG FORM) ===
const SYSTEM_PROMPT_DEVOTIONAL_LONG = `
You are a Seminary Professor and Pastor creating a Deep Dive Bible Study script.
TARGET: Mature believers seeking "Solid Food", not milk.
STYLE: Expository (Verse-by-Verse), Historical-Grammatical, Christ-Centered.
AVOID: Narcigesis (reading oneself into the text), emotional manipulation, prosperity promises.

=== TASK ===
Generate a script for a "Theological Journey" consisting of **25 DOCTRINAL POINTS** based on a specific biblical theme or book.

=== STRUCTURE ===
1. **INTRO (1 min)**: Intellectual hook. Historical context of the book/topic.
2. **THE 25 POINTS (The Meat)**: 
   - Group them into 5 Theological Pillars (Chapters).
   - Each point must explain a truth about GOD (His attributes, His work), not just "how to get stuff".
   - **Pattern:** Read Verse -> Explain Context/Doctrine -> Apply to the Heart -> Brief Prayer of Adoration.
   - Tone: Reverent, Deep, Academic yet Spirit-filled (like John Piper or RC Sproul).
3. **CLOSING (2 mins)**: Call to study the Word. Doxology.

OUTPUT FORMAT (JSON):
{
  "format": "HORIZONTAL",
  "title": "String (e.g. 'The Attributes of God: A Deep Dive')",
  "meta_description": "String", 
  "tags": ["systematic theology", "bible study", "exegesis", "christianity", "reformed theology"], 
  "youtube_description": "String (SEO optimized, listing the chapters)",
  "video_generation_prompt": "String (Horizontal 16:9, Ancient Holy Place, dimly lit, scroll on a wooden table, cinematic lighting, 8k, photorealistic, NO PEOPLE)",
  "visual_prompt": "String (Theme: e.g. 'The Sovereignty of God')",
  "chapters": [
    {
      "chapter_title": "String (e.g. 'PART 1: THE HOLINESS OF GOD')",
      "chapter_intro": "String (Intro to this doctrine)",
      "items": [
        { 
            "title": "String (e.g. 'The Seraphim's Cry')", 
            "content_visual": "String (Isaiah 6:3)", 
            "content_spoken": "String (Deep theological explanation ending in a prayer of awe. ~150 words.)" 
        }
      ]
    }
    // ... 5 Chapters total
  ]
}
`;

// === NEW STRATEGY: SYSTEMATIC THEOLOGY MARATHON (ARCHITECT) ===
const PROMPT_MARATHON_BLUEPRINT = `
You are the "Architect" of a Massive 8-Hour Theological Course (Audiobook Style).
THEME: "The Attributes of God & The Nature of Eternity".

TASK 1: Create the "Syllabus" - 20 Chapters that move logically through Systematic Theology.
   - E.g., The Trinity -> The Holiness -> The Justice -> The Wrath -> The Grace -> The Atonement -> The Resurrection -> The Glorification.
TASK 2: Write the FULL SCRIPT for "Chapter 1" ONLY.

Structure for Chapter 1 Script:
- A deep, meditative lecture mixed with prayer.
- Focus: "Theology leads to Doxology" (Learning leads to Worship).
- 10 Key Thoughts/Meditations per chapter.
- Total word count for Chapter 1: ~1500 words.

OUTPUT JSON:
{
  "marathon_title": "THE KNOWLEDGE OF THE HOLY: 8-HOUR JOURNEY",
  "marathon_outline": ["Chapter 1: The Self-Existence of God (Aseity)", "Chapter 2: The Immutability of God", ... "Chapter 20: The Beatific Vision"],
  "part_1_content": {
      "chapter_title": "PART 1: THE SELF-EXISTENCE OF GOD",
      "items": [
        { "title": "Meditation 1", "content_visual": "Exodus 3:14", "content_spoken": "God does not depend on anyone for His existence..." }
        // ... 10 items
      ]
  }
}
`;

const SYSTEM_PROMPT_HOROSCOPE_SHORTS = `
You are a Mystic Oracle on TikTok.
GOAL: Create a "Cold Read" effect. The user must feel you are speaking directly to them.

STRUCTURE:
1. **THE STOP**: "If you are a [Sign 1], [Sign 2], or [Sign 3]..."
2. **THE WARNING**: "Listen closely. A betrayal is coming." or "A massive sum of money is entering your life."
3. **THE ACTION**: "Use this audio to claim." or "Share with a Scorpio."

Constraint: Very fast. Max 80 words.

OUTPUT FORMAT (JSON):
{
  "format": "VERTICAL",
  "title": "String", "meta_description": "String", 
  "tags": ["String", "String"], "youtube_description": "String",
  "video_generation_prompt": "String",
  "trend_source": "String", "visual_theme": "String",
  "intro_visual": "String", "intro_spoken": "String",
  "signs": [ { "sign": "String", "prediction_visual": "String", "prediction_spoken": "String" } ],
  "outro_visual": "String", "outro_spoken": "String"
}
`;

const SYSTEM_PROMPT_HOROSCOPE_LONG = `
You are a Master Astrologer creating a LONG-FORM YouTube forecast.
FORMAT: Horizontal (16:9).
GOAL: High retention.

=== ENTROPY ENGINE (PICK ONE PERSONA) ===
1. **The Doomsayer (Vanga/Nostradamus)**: Warnings, karma, fate. Tone: Heavy.
2. **The Lucky List**: "Top 6 Signs for January". Positive, money-focused. Tone: Excited.
3. **The Love Witch**: Obsession, soulmates, ex-partners. Tone: Seductive.
4. **The Retrograde Guide**: Survival guide for planetary shifts. Tone: Educational.

=== CTA STRATEGY ===
Explicitly tell viewers to watch for their FAMILY'S signs to "activate protection".
"If you see a good prediction for a friend, share it with them to double your luck."

OUTPUT FORMAT (JSON):
{
  "format": "HORIZONTAL",
  "title": "String",
  "meta_description": "String", 
  "tags": ["String", "String"], "youtube_description": "String",
  "video_generation_prompt": "String",
  "trend_source": "String", "visual_theme": "String",
  "chapters": [
     {
        "chapter_title": "String (e.g. 'LOVE SPHERE' or 'TOP 3 SIGNS')",
        "chapter_intro": "String (Hook)",
        "items": [
            { "title": "String (Sign Name)", "content_spoken": "String (Prediction)", "content_visual": "String (Summary)" }
        ]
     }
  ]
}
`;

const SYSTEM_PROMPT_VITALITY_SHORTS = `
You are a Silver Vitality Expert. 
TARGET AUDIENCE: Age 55+ in USA/UK.
KEYWORDS (Strictly Medical/Senior): "arthritis relief", "lower blood pressure", "unclog arteries", "improve memory", "reduce swelling", "liver detox", "vision improvement".
AVOID: "fitness", "gym", "workout", "protein shake".
STYLE: "Dark Mode Narrative".
CONSTRAINTS: Maximum 120 words.

STRUCTURE:
1. THE SYMPTOM (Hook): "Do you have swollen legs?" or "Forget where you put your keys?"
2. THE REVEAL: "It's not just age. It's your liver/circulation."
3. THE SOLUTION: "Mix ginger and lemon (or specific old remedy)."
4. THE CTA: "Save this remedy."

OUTPUT FORMAT (JSON):
{
  "title": "String", "meta_description": "String", 
  "tags": ["String (arthritis)", "String (blood pressure)", "String (remedy name)"], 
  "youtube_description": "String (Include disclaimer and specific benefits)",
  "video_generation_prompt": "String", "topic": "String", "thumbnail_prompt": "String",
  "scenes": [ { "id": 1, "micro_script": "String", "voiceover": "String", "overlay_text": "String", "image_prompt": "String (STRICTLY: Minimalist white chalk drawing on black blackboard. Medical schematic. No colors.)" } ]
}
`;

const SYSTEM_PROMPT_VITALITY_LONG = `
You are a Longevity Expert creating a LONG-FORM Health Documentary script (Horizontal 16:9).
TARGET: 55+ Audience in Tier 1 Countries (USA, UK, Canada, Australia).
KEYWORDS: "High Blood Pressure", "Type 2 Diabetes", "Joint Pain", "Memory Loss", "Prostate Health", "Natural Pain Killers".
LANGUAGE: ENGLISH ONLY.

=== OPTIMIZATION GOAL ===
Maximize YouTube SEO for "Senior Health". 
Generate highly searchable TAGS and a description packed with keywords like "Holistic Health", "Grandma's Remedy", "Natural Cure".

=== NARRATIVE MODES (PICK ONE) ===
1. **The "Grandma's Remedy" Mode**: Focus on Western folk medicine (Apple Cider Vinegar, Castor Oil). Tone: Nostalgic, Warm.
2. **The "Conspiracy" Mode**: "The hidden toxin in your kitchen". "What big pharma hates". Tone: Investigative, Urgent.
3. **The "Emergency" Mode**: "If you have this symptom, stop eating this immediately". Tone: Alert, Protective.

STRUCTURE:
- Chapter 1: THE ROOT CAUSE / THE ENEMY.
- Chapter 2: THE SOLUTION / THE PROTOCOL.
- Chapter 3: THE DAILY HABIT.

CTAs: "Save this video before it gets taken down.", "Send this to a friend who has joint pain."

OUTPUT FORMAT (JSON):
{
  "format": "HORIZONTAL",
  "title": "String (e.g. 'THE 3 CENT REMEDY DOCTORS HATE')",
  "meta_description": "String",
  "tags": ["senior health", "joint pain relief", "natural remedy", "high blood pressure", "memory loss"], 
  "youtube_description": "String (SEO Rich Description)",
  "video_generation_prompt": "String (STRICTLY: Minimalist white chalk drawing on black blackboard. Medical schematic. High contrast. No colors.)",
  "topic": "String",
  "thumbnail_prompt": "String",
  "chapters": [
    {
      "chapter_title": "String",
      "chapter_intro": "String",
      "items": [
        { "title": "String", "content_visual": "String", "content_spoken": "String" }
      ]
    }
  ]
}
`;

export class GeminiService {
  private ai: GoogleGenAI;

  constructor() {
    this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  }

  async generateScenario(): Promise<Scenario> {
    const response = await this.ai.models.generateContent({
      model: "gemini-2.5-flash",
      config: { systemInstruction: SYSTEM_PROMPT_BATTLES, responseMimeType: "application/json" },
      contents: [{ role: "user", parts: [{ text: "Generate viral scenario." }] }]
    });
    return JSON.parse(response.text!) as Scenario;
  }

  async generateDevotional(format: VideoFormat = 'VERTICAL', variant: 'DEFAULT' | 'MARATHON' = 'DEFAULT'): Promise<ScriptureContent> {
    if (format === 'VERTICAL') {
        variant = 'DEFAULT';
    }

    const isLong = format === 'HORIZONTAL';
    
    // --- MARATHON LOGIC: ARCHITECT MODE ---
    if (isLong && variant === 'MARATHON') {
        console.log("Generating Marathon Blueprint (Architect Mode)...");
        
        const response = await this.ai.models.generateContent({
             model: "gemini-2.5-flash",
             config: { 
                 responseMimeType: "application/json", 
                 systemInstruction: PROMPT_MARATHON_BLUEPRINT 
             },
             contents: [{ role: "user", parts: [{ text: `Generate 20-Chapter Syllabus and Part 1 Script.` }] }]
        });
        
        const json = JSON.parse(response.text!);
        
        const chapters: ContentChapter[] = [];
        chapters.push({ 
            chapter_title: json.part_1_content.chapter_title, 
            chapter_intro: "This is Part 1 of the 8-Hour Theological Course. Generated by The Architect.", 
            items: json.part_1_content.items || [] 
        });

        return {
            format: 'HORIZONTAL',
            title: json.marathon_title || "8-Hour Theological Journey",
            meta_description: "Part 1 of 20 generated successfully. Use the worker script to generate Parts 2-20.",
            video_generation_prompt: "Horizontal 16:9, Ancient Study, Libraries, Candlelight, Manuscripts, Cinematic 8k, No people",
            tags: ["systematic theology", "bible study", "christianity", "attributes of god"],
            youtube_description: "Part 1 of 20. \n\nFULL COURSE SYLLABUS:\n" + (json.marathon_outline || []).join('\n'),
            visual_prompt: "Ancient Theological Sanctuary",
            chapters: chapters,
            marathon_outline: json.marathon_outline || []
        };
    }

    let prompt = SYSTEM_PROMPT_DEVOTIONAL_SHORTS;
    if (isLong) prompt = SYSTEM_PROMPT_DEVOTIONAL_LONG;

    const entropy = Math.random();
    const response = await this.ai.models.generateContent({
      model: "gemini-2.5-flash",
      config: { 
          systemInstruction: prompt, 
          responseMimeType: "application/json",
          maxOutputTokens: 8192
      },
      contents: [{ role: "user", parts: [{ text: `Generate deep theological content. Entropy Seed: ${entropy}. Focus on CHRIST-CENTEREDNESS, not self-centeredness.` }] }]
    });
    const data = JSON.parse(response.text!);
    data.format = format;
    return data as ScriptureContent;
  }

  async generateHoroscope(format: VideoFormat = 'VERTICAL', language: Language = 'RUSSIAN'): Promise<HoroscopeContent> {
    const isLong = format === 'HORIZONTAL';
    const systemPrompt = isLong ? SYSTEM_PROMPT_HOROSCOPE_LONG : SYSTEM_PROMPT_HOROSCOPE_SHORTS;
    const randomSeed = Math.floor(Math.random() * 100000);
    const userPrompt = `Generate script in ${language}. Seed: ${randomSeed}. PICK A RARE PERSONA from the list. Do not repeat previous themes.`;

    const response = await this.ai.models.generateContent({
      model: "gemini-2.5-flash", 
      config: { systemInstruction: systemPrompt, tools: [{ googleSearch: {} }], maxOutputTokens: 8192 },
      contents: [{ role: "user", parts: [{ text: userPrompt }] }]
    });

    const cleanedText = response.text!.replace(/```json|```/g, '').trim();
    const data = JSON.parse(cleanedText);
    data.format = format;
    return data as HoroscopeContent;
  }

  async generateVitality(customTopic?: string, isAd: boolean = false, format: VideoFormat = 'VERTICAL'): Promise<VitalityContent> {
    const isLong = format === 'HORIZONTAL';
    const systemPrompt = isLong ? SYSTEM_PROMPT_VITALITY_LONG : SYSTEM_PROMPT_VITALITY_SHORTS;
    const randomSeed = Math.floor(Math.random() * 999999);
    
    let promptText = customTopic ? `Topic: "${customTopic}".` : `Generate UNIQUE topic. Seed: ${randomSeed}. Pick a unique Narrative Mode.`;
    if (isAd) promptText += " AD_MODE=TRUE.";

    const response = await this.ai.models.generateContent({
      model: "gemini-2.5-flash",
      config: { systemInstruction: systemPrompt, tools: [{ googleSearch: {} }], maxOutputTokens: 8192 },
      contents: [{ role: "user", parts: [{ text: promptText }] }]
    });

    const cleanedText = response.text!.replace(/```json|```/g, '').trim();
    const data = JSON.parse(cleanedText);
    data.format = format;
    return data as VitalityContent;
  }
  
  async generateImage(prompt: string, format: VideoFormat = 'VERTICAL'): Promise<string> {
    const aspectRatio = format === 'HORIZONTAL' ? "16:9" : "9:16";
    const response = await this.ai.models.generateContent({
        model: 'gemini-2.5-flash-image',
        contents: { parts: [{ text: prompt }] },
        config: { imageConfig: { aspectRatio: aspectRatio } }
    });
    const part = response.candidates?.[0]?.content?.parts?.find(p => p.inlineData);
    if (part?.inlineData?.data) return `data:${part.inlineData.mimeType};base64,${part.inlineData.data}`;
    throw new Error("No image data");
  }

  // --- TTS ENGINE: CHUNKING & STITCHING ---

  /**
   * Generates speech handling long text by splitting it into chunks,
   * generating separate audio files, and stitching them into one WAV.
   */
  async generateSpeech(text: string): Promise<string> {
    const CHUNK_SIZE = 600; // Safe characters limit
    const chunks = this.splitTextForTTS(text, CHUNK_SIZE);
    const audioBuffers: Uint8Array[] = [];

    console.log(`TTS: Splitting text into ${chunks.length} chunks...`);

    for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        if (!chunk.trim()) continue;

        let success = false;
        let retries = 0;
        
        while (retries < 3 && !success) {
            try {
                const response = await this.ai.models.generateContent({
                    model: "gemini-2.5-flash-preview-tts",
                    contents: [{ parts: [{ text: chunk }] }],
                    config: {
                        responseModalities: [Modality.AUDIO],
                        speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Charon' } } },
                    },
                });
                
                const base64 = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
                if (base64) {
                    const binaryString = atob(base64);
                    const len = binaryString.length;
                    const bytes = new Uint8Array(len);
                    for (let j = 0; j < len; j++) bytes[j] = binaryString.charCodeAt(j);
                    audioBuffers.push(bytes);
                    success = true;
                } else {
                    throw new Error("Empty TTS Response");
                }
            } catch (e: any) {
                console.warn(`TTS Chunk ${i+1}/${chunks.length} failed. Retrying...`);
                retries++;
                await new Promise(r => setTimeout(r, 1500)); // Backoff
            }
        }
        
        // Rate limiting pause
        await new Promise(r => setTimeout(r, 500));
    }

    if (audioBuffers.length === 0) throw new Error("TTS generation failed completely.");

    // Stitch chunks
    const finalBytes = this.concatWavBytes(audioBuffers);
    const blob = new Blob([finalBytes], { type: 'audio/wav' });
    return URL.createObjectURL(blob);
  }

  /**
   * Splits text into sentences to avoid cutting words in half during chunking.
   */
  private splitTextForTTS(text: string, maxLength: number): string[] {
    const sentenceRegex = /[^.!?\n]+[.!?\n]+|[^.!?\n]+$/g;
    const sentences = text.match(sentenceRegex) || [text];
    
    const chunks: string[] = [];
    let currentChunk = "";

    for (const sentence of sentences) {
        const clean = sentence.trim();
        if ((currentChunk + " " + clean).length > maxLength) {
            if (currentChunk) chunks.push(currentChunk.trim());
            currentChunk = clean;
        } else {
            currentChunk += " " + clean;
        }
    }
    if (currentChunk) chunks.push(currentChunk.trim());
    return chunks;
  }

  /**
   * Concatenates multiple WAV byte arrays into one valid WAV.
   * Strips the 44-byte header from subsequent chunks and updates the total size in the first header.
   */
  private concatWavBytes(buffers: Uint8Array[]): Uint8Array {
      if (buffers.length === 1) return buffers[0];

      const header = buffers[0].slice(0, 44);
      const bodyChunks: Uint8Array[] = [];
      let totalDataLen = 0;

      for (const buf of buffers) {
          // Strip 44 bytes header (WAV standard)
          const body = buf.length > 44 ? buf.slice(44) : new Uint8Array(0);
          bodyChunks.push(body);
          totalDataLen += body.length;
      }

      // Reconstruct header with new size
      // Offset 4: ChunkSize = 36 + SubChunk2Size
      const view = new DataView(header.buffer.slice(0, 44)); // Copy header
      view.setUint32(4, 36 + totalDataLen, true);
      // Offset 40: SubChunk2Size = data length
      view.setUint32(40, totalDataLen, true);

      // Merge
      const finalBuffer = new Uint8Array(44 + totalDataLen);
      finalBuffer.set(new Uint8Array(view.buffer), 0);
      
      let offset = 44;
      for (const body of bodyChunks) {
          finalBuffer.set(body, offset);
          offset += body.length;
      }

      return finalBuffer;
  }
}

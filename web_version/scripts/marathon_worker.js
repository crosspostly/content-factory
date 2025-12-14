
/**
 * ♾️ INFINITE THEOLOGY ENGINE - V3.5 (EXPOSITORY & DOCTRINAL)
 * -----------------------------------------------------
 * ARCHITECTURE:
 * 1. THE ARCHITECT: Generates a 20-chapter SYSTEMATIC THEOLOGY Syllabus.
 * 2. THE PROFESSOR: Writes deep, educational scripts that transition into worship.
 * 3. THE SLICER: Splits huge scripts into small sentence-based chunks for safe TTS.
 * 4. THE SYNTH: Generates audio for chunks and stitches them binary-style into one WAV.
 */

const { GoogleGenAI, Modality } = require("@google/genai");
const fs = require('fs');
const path = require('path');

// === 🎛️ CONTROL PANEL ===
const CONFIG = {
    // ТЕМА МАРАФОНА: Переключено с "Успеха" на "Атрибуты Бога"
    THEME: "The Attributes of God & The Mystery of the Trinity", 
    
    // Количество глав (20 глав * 15 мин = ~5 часов)
    TOTAL_CHAPTERS: 20,                          
    
    // Голос: 'Charon' (Deep Male) - идеален для серьезного обучения
    VOICE_MODEL: 'Charon',                    
    
    // Папка вывода
    OUTPUT_DIR: './output_marathon',
    
    // Безопасный размер куска текста для TTS
    TTS_SAFE_CHUNK_SIZE: 600 
};

// === INIT ===
const apiKey = process.env.API_KEY;
if (!apiKey) { console.error("❌ ERROR: Set API_KEY env variable."); process.exit(1); }
const ai = new GoogleGenAI({ apiKey: apiKey });

// === UTILS ===
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

function splitTextForTTS(text, maxLength) {
    const sentenceRegex = /[^.!?\n]+[.!?\n]+|[^.!?\n]+$/g;
    const sentences = text.match(sentenceRegex) || [text];
    
    const chunks = [];
    let currentChunk = "";

    for (const sentence of sentences) {
        const cleanSentence = sentence.trim();
        if (!cleanSentence) continue;

        if ((currentChunk + " " + cleanSentence).length > maxLength) {
            if (currentChunk) chunks.push(currentChunk.trim());
            currentChunk = cleanSentence;
        } else {
            currentChunk += " " + cleanSentence;
        }
    }
    if (currentChunk) chunks.push(currentChunk.trim());
    return chunks;
}

function concatWavBuffers(buffers) {
    if (buffers.length === 0) return null;
    if (buffers.length === 1) return buffers[0];
    const header = buffers[0].slice(0, 44);
    const bodyChunks = [];
    let totalDataLen = 0;
    for (const buf of buffers) {
        const body = buf.length > 44 ? buf.slice(44) : Buffer.alloc(0);
        bodyChunks.push(body);
        totalDataLen += body.length;
    }
    const newHeader = Buffer.from(header);
    newHeader.writeUInt32LE(36 + totalDataLen, 4);
    newHeader.writeUInt32LE(totalDataLen, 40);
    return Buffer.concat([newHeader, ...bodyChunks]);
}

// === STEP 1: THE ARCHITECT (SYLLABUS) ===
async function generateOutline() {
    console.log(`\n🏛️  ARCHITECT: Designing Theological Syllabus for: "${CONFIG.THEME}"...`);
    
    const prompt = `
    ROLE: You are the Dean of a Theological Seminary.
    TASK: Create a 20-chapter Syllabus for a course on: "${CONFIG.THEME}".
    
    GUIDELINES:
    - NO FLUFF. NO PROSPERITY GOSPEL.
    - Focus on SYSTEMATIC THEOLOGY (Theology Proper, Christology, Pneumatology).
    - Titles must be academic yet reverent.
    - Example Progression: The Aseity of God -> The Holiness -> The Justice -> The Love -> The Trinity -> The Incarnation.
    
    OUTPUT JSON ONLY:
    { "chapters": [ "Chapter 1 Title", "Chapter 2 Title", ... ] }
    `;

    const resp = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        config: { responseMimeType: "application/json" },
        contents: [{ role: "user", parts: [{ text: prompt }] }]
    });

    return JSON.parse(resp.text).chapters;
}

// === MAIN LOOP ===
async function main() {
    if (!fs.existsSync(CONFIG.OUTPUT_DIR)) fs.mkdirSync(CONFIG.OUTPUT_DIR);

    // 1. Generate Plan
    let chapters;
    try {
        chapters = await generateOutline();
        fs.writeFileSync(path.join(CONFIG.OUTPUT_DIR, 'outline.json'), JSON.stringify(chapters, null, 2));
        console.log(`✅ Syllabus generated: ${chapters.length} chapters.`);
    } catch (e) {
        console.error("❌ Architect Failed:", e.message);
        return;
    }

    // 2. Process Each Chapter
    console.log("\n🏭 STARTING SEMINARY PRODUCTION LINE...");

    for (let i = 0; i < chapters.length; i++) {
        const title = chapters[i];
        const label = `PART_${(i+1).toString().padStart(2, '0')}`;
        console.log(`\n🎬 PROCESSING ${label}: "${title}"`);

        // --- PHASE A: THE PROFESSOR (Scripting) ---
        let script = "";
        let visualPrompt = "";
        
        try {
            // === THE SYSTEMATIC THEOLOGY PROMPT ===
            const writerPrompt = `
            ROLE: You are a Reformed Theologian and Pastor (like RC Sproul or John Piper).
            CONTEXT: Writing Chapter ${i+1} of a deep audio course.
            THEME: "${CONFIG.THEME}".
            CHAPTER TITLE: "${title}".
            
            OBJECTIVE: Write a 1500-word Expository Teaching that leads into Worship (Doxology).
            
            === STRATEGY: THEOLOGY LEADS TO DOXOLOGY ===
            1. **The Exegesis (500 words):** 
               - Define the doctrine clearly.
               - Quote a key scripture (KJV/NKJV) and explain the context.
               - Explain WHY this matters. (e.g. "If God is not Holy, our sin is not serious.")
            2. **The Meditation (500 words):** 
               - Apply this truth to the heart.
               - Not "how to get rich", but "how to find joy in God".
               - Confront idols. Call to repentance.
            3. **The Prayer of Adoration (500 words):**
               - A vertical prayer speaking BACK to God about His attributes.
               - "Lord, we adore You because You are [Attribute]..."
            
            CONSTRAINTS:
            - **NO META TEXT:** Do not write [Pause].
            - **TONE:** Reverent, Awe-filled, Serious, Intellectual.
            - **AVOID:** "I declare success", "My destiny", "My breakthrough". Focus on GOD, not SELF.
            
            OUTPUT JSON:
            { 
              "script": "The full spoken text...", 
              "visual_prompt": "A prompt for an AI image generator. Describe a motionless, holy, cinematic abstract scene representing '${title}'. Ancient library, scrolls, candle, divine light. NO PEOPLE. NO TEXT." 
            }
            `;

            const scriptReq = await ai.models.generateContent({
                model: "gemini-2.5-flash",
                config: { responseMimeType: "application/json" },
                contents: [{ role: "user", parts: [{ text: writerPrompt }] }]
            });
            const json = JSON.parse(scriptReq.text);
            script = json.script;
            visualPrompt = json.visual_prompt;
            
            fs.writeFileSync(path.join(CONFIG.OUTPUT_DIR, `${label}_script.txt`), script);
            console.log(`   📝 Teaching written (~${script.split(' ').length} words).`);

        } catch (e) {
            console.error(`   ⚠️ Script Error: ${e.message}. Skipping.`);
            continue;
        }

        // --- PHASE B: THE VISUALIZER (Image) ---
        try {
            const imgResp = await ai.models.generateContent({
                model: 'gemini-2.5-flash-image',
                contents: { parts: [{ text: `Cinematic 8k, photorealistic, ancient theological aesthetic. ${visualPrompt}. No text, no people.` }] },
                config: { imageConfig: { aspectRatio: "16:9" } }
            });
            const imgData = imgResp.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
            if (imgData) {
                fs.writeFileSync(path.join(CONFIG.OUTPUT_DIR, `${label}.png`), Buffer.from(imgData, 'base64'));
                console.log(`   🎨 Visual generated.`);
            }
        } catch (e) { console.error(`   ⚠️ Image Error: ${e.message}`); }

        // --- PHASE C: THE SLICER & SYNTH (Audio) ---
        console.log(`   🎙️ Audio Production (Chunking Strategy)...`);
        const textChunks = splitTextForTTS(script, CONFIG.TTS_SAFE_CHUNK_SIZE);
        const wavSegments = [];
        
        process.stdout.write(`      Progress: [`);

        for (const chunk of textChunks) {
            let retries = 0;
            let success = false;

            while (retries < 3 && !success) {
                try {
                    const ttsResp = await ai.models.generateContent({
                        model: "gemini-2.5-flash-preview-tts",
                        contents: [{ parts: [{ text: chunk }] }],
                        config: {
                            responseModalities: [Modality.AUDIO],
                            speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: CONFIG.VOICE_MODEL } } },
                        },
                    });
                    const audioB64 = ttsResp.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
                    if (audioB64) {
                        wavSegments.push(Buffer.from(audioB64, 'base64'));
                        success = true;
                        process.stdout.write("#"); 
                    } else { throw new Error("No audio data"); }
                } catch (e) {
                    if (e.status === 403 || (e.message && e.message.includes("Region"))) {
                        console.error("\n❌ FATAL: Region Not Supported. Use VPN.");
                        process.exit(1);
                    }
                    retries++;
                    await sleep(1000 * retries); 
                }
            }
            if (!success) process.stdout.write("x"); 
            await sleep(200); 
        }
        process.stdout.write(`] Done.\n`);

        // --- PHASE D: STITCHING ---
        if (wavSegments.length > 0) {
            const finalWav = concatWavBuffers(wavSegments);
            if (finalWav) {
                fs.writeFileSync(path.join(CONFIG.OUTPUT_DIR, `${label}.wav`), finalWav);
                console.log(`   ✅ Audio Stitched & Saved (${(finalWav.length / 1024 / 1024).toFixed(2)} MB).`);
            }
        }
    }

    console.log("\n🎉 THEOLOGICAL COURSE GENERATION COMPLETE.");
}

main();

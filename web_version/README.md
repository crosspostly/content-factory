
# Predator Shorts Studio (AI Automation Dashboard)

An advanced AI dashboard designed to automate the creation of viral YouTube Shorts and Long-Form content for niche channels ("Predator Battles", "Daily Prayers", "Horoscopes", "Vitality Health").

## 🚀 Key Features

*   **One-Click Auto Pilot:** Generates Script -> Visuals -> Voiceover -> Video Render in one flow.
*   **Gemini 2.0 Integration:** Uses Google's latest models for Scripting, Image Generation (Imagen 3), and TTS (Text-to-Speech).
*   **No Black Screens:** Uses Base64-encoded AI images to bypass browser CORS security restrictions during video rendering.
*   **Smart Duration Logic:** Intelligently scales vertical Shorts to fit under 60 seconds using proportional scaling for videos 60-120s and safe capping for longer videos.

## 🛠️ Components Structure

### 1. `App.tsx` (The Brain)
*   Manages the global state (Current Step, Selected Mode, Data).
*   Contains the "One-Click Auto Pilot" logic `generateContent(true)`.
*   Handles the top navigation bar and project switching.

### 2. `GeminiService.ts` (The Engine)
*   Contains all **System Prompts** (The "instruction manual" for the AI).
*   **Modify prompts here** if you want to change the style of the scripts (e.g., make prayers more aggressive or horoscopes more mystical).
*   Handles API calls for Text, Images, and Audio.

### 3. `ImageryGenerator.tsx` (Visuals)
*   **Default Behavior:** Generates AI Images using Gemini.
*   **Why?** To prevent "Black Screen" errors caused by stock videos (Pexels/Pixabay) being blocked by browser security when saving the video file.
*   **Smart Cleaning:** It automatically strips technical words ("4k", "Vertical") from the prompt before sending it to the image generator to get better artistic results.

### 4. `VideoRenderer.tsx` (The Studio)
*   **Canvas Rendering:** Draws images and text frame-by-frame onto a hidden HTML5 Canvas.
*   **Audio Mixing:** Mixes Background Music + AI Voiceover using WebAudio API.
*   **Recorder:** Captures the canvas stream and downloads a `.webm` file.
*   **Fixes:** Now calculates duration *once* at start-up to prevent "double rendering" loops.

## ⚠️ Troubleshooting

**"Rendering Error" / Black Screen:**
*   This happens if an image fails to load.
*   We now use **Gemini AI Images** by default because they are generated securely within the app and never fail due to CORS.

**"Duration capped/scaled" messages:**
*   YouTube Shorts **must** be under 60 seconds.
*   The system now intelligently scales content: videos 60-120s are proportionally scaled, longer videos are capped at 59.9s for safe upload.

**"API Error":**
*   Check your internet connection.
*   Ensure the API Key environment variable is active.

## 🎨 Customizing Styles

*   **Colors:** Defined in `index.html` (Tailwind config).
*   **Fonts:** Uses 'Cinzel' (Headers) and 'Inter' (Body).
*   **Prompts:** Edit `services/geminiService.ts` constants.

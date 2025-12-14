
// NEW SERVICE FOR EXTERNAL MEDIA API
import { Track, GeneratedImage } from "../types";

const KEYS = {
    PIXABAY: "53682602-8d0a89ba50ebfe88428528c8d",
    PEXELS: "MSK8N1uYAzU1yTNpicrZeWvKnQ1t99vTpy4YDKPHjSlHwaKbKqlFrokZ",
    // Primary Freesound token
    FREESOUND: "4E54XDGL5Pc3V72TQfSo83WZMb600FE2k9gPf6Gk" 
};

export class MediaService {
  
  // --- ROBUST DOWNLOADER (THE CORS KILLER) ---
  /**
   * Attempts to fetch a resource using a chain of fallbacks.
   * 1. Direct (in case it works)
   * 2. CorsProxy.io (Fastest)
   * 3. AllOrigins (Reliable for raw bytes)
   * 4. ThingProxy (Backup)
   */
  async downloadAsset(url: string): Promise<Blob> {
      // Helper to try a fetch and throw if not ok
      const tryFetch = async (targetUrl: string) => {
          const res = await fetch(targetUrl);
          if (!res.ok) throw new Error(`Status ${res.status}`);
          return await res.blob();
      };

      // 1. Try Direct (Best case)
      try {
          return await tryFetch(url);
      } catch (e) {
          console.warn(`[Download] Direct fetch failed for ${url}. Trying Proxy 1...`);
      }

      // 2. Proxy 1: corsproxy.io
      try {
          const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(url)}`;
          return await tryFetch(proxyUrl);
      } catch (e) {
          console.warn(`[Download] Proxy 1 failed. Trying Proxy 2...`);
      }

      // 3. Proxy 2: allorigins.win (Request raw)
      try {
          const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
          return await tryFetch(proxyUrl);
      } catch (e) {
          console.warn(`[Download] Proxy 2 failed. Trying Proxy 3...`);
      }

      // 4. Proxy 3: thingproxy (Last resort)
      try {
          const proxyUrl = `https://thingproxy.freeboard.io/fetch/${url}`;
          return await tryFetch(proxyUrl);
      } catch (e) {
          console.error(`[Download] All proxies died. Cannot download asset.`);
          throw new Error("CORS_BLOCK: Unable to download asset via any proxy.");
      }
  }

  // --- VIDEO SEARCH (PRIMARY) ---
  async getStockVideo(query: string, orientation: 'landscape' | 'portrait'): Promise<string> {
      try {
        // 1. PEXELS VIDEO (Best Quality)
        const pexelsUrl = `https://api.pexels.com/videos/search?query=${encodeURIComponent(query)}&orientation=${orientation}&per_page=8&size=medium`;
        const pexelsRes = await fetch(pexelsUrl, { headers: { Authorization: KEYS.PEXELS } });
        
        if (pexelsRes.ok) {
            const data = await pexelsRes.json();
            if (data.videos && data.videos.length > 0) {
                const randomIndex = Math.floor(Math.random() * data.videos.length);
                const chosenVideo = data.videos[randomIndex];
                const videoFiles = chosenVideo.video_files;
                const bestFile = videoFiles.find((f: any) => f.height >= 720 && f.height <= 1080) || videoFiles[0];
                return bestFile.link;
            }
        }

        // 2. PIXABAY VIDEO (Fallback)
        const pixabayUrl = `https://pixabay.com/api/videos/?key=${KEYS.PIXABAY}&q=${encodeURIComponent(query)}&video_type=film&per_page=8`;
        const pixabayRes = await fetch(pixabayUrl);
        
        if (pixabayRes.ok) {
            const data = await pixabayRes.json();
            if (data.hits && data.hits.length > 0) {
                 const randomIndex = Math.floor(Math.random() * data.hits.length);
                 return data.hits[randomIndex].videos.medium.url || data.hits[randomIndex].videos.large.url;
            }
        }

      } catch (e) {
          console.warn("Stock Video Fetch Error:", e);
      }
      return "";
  }

  // --- IMAGE SEARCH (BACKUP) ---
  async getBackupImage(query: string, orientation: 'landscape' | 'portrait'): Promise<string> {
    try {
        const pexelsUrl = `https://api.pexels.com/v1/search?query=${encodeURIComponent(query)}&orientation=${orientation}&per_page=5`;
        const pexelsRes = await fetch(pexelsUrl, { headers: { Authorization: KEYS.PEXELS } });
        
        if (pexelsRes.ok) {
            const data = await pexelsRes.json();
            if (data.photos && data.photos.length > 0) {
                return data.photos[Math.floor(Math.random() * data.photos.length)].src.large2x; 
            }
        }
    } catch (e) { console.warn("Media Fallback Error:", e); }
    return "";
  }

  // --- AUDIO (FREESOUND) ---
  async getAmbientTracks(theme: string): Promise<Track[]> {
    const tracks: Track[] = [];
    try {
        const fsUrl = `https://freesound.org/apiv2/search/text/?query=${encodeURIComponent(theme)}&fields=id,name,previews,username,duration,images&token=${KEYS.FREESOUND}&filter=duration:[60 TO 600]`;
        const fsRes = await fetch(fsUrl);
        
        if (fsRes.ok) {
            const data = await fsRes.json();
            if (data.results) {
                data.results.slice(0, 4).forEach((item: any) => {
                    if (item.previews && item.previews['preview-hq-mp3']) {
                        tracks.push({
                            id: `fs_${item.id}`,
                            name: item.name.replace(/_/g, ' ').replace(/.mp3|.wav/gi, '').substring(0, 25),
                            artist_name: `Freesound: ${item.username}`,
                            duration: item.duration,
                            image: item.images?.waveform_m || '',
                            audio: item.previews['preview-hq-mp3']
                        });
                    }
                });
            }
        }
    } catch (e) { console.warn("Audio Fetch Error:", e); }
    return tracks;
  }
}

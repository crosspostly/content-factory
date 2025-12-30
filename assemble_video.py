
import os
import json
import subprocess
import sys
import shutil
import datetime
import glob
import requests
from urllib.parse import urlparse

# CONFIGURATION
MUSIC_VOLUME = 0.12  # Consistent with app mix
SPEECH_FILTER = "equalizer=f=3000:width_type=h:width=2000:g=3,acompressor=threshold=-18dB:ratio=3:attack=200:release=1000"

# --- ORIENTATION CONFIG ---
IS_PORTRAIT = True
TARGET_WIDTH = 1080 if IS_PORTRAIT else 1920
TARGET_HEIGHT = 1920 if IS_PORTRAIT else 1080

# Subtitle Styling
SUB_STYLE = "FontName=Arial,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,MarginV=70,Alignment=2,MarginL=10,MarginR=10,Bold=1" if IS_PORTRAIT else "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,MarginV=35,Alignment=2,Bold=1"

# ZOOM CONFIG (Ken Burns)
ZOOM_SPEED = 0.002 if IS_PORTRAIT else 0.001
MAX_ZOOM = 1.2 if IS_PORTRAIT else 1.1

# METADATA SCRUBBING FLAGS
METADATA_FLAGS = [
    "-map_metadata", "-1",
    "-metadata", "creation_time=now",
    "-metadata", "major_brand=mp42",
    "-metadata", "handler_name=Core Media Data Handler",
    "-metadata", "encoder=Adobe Premiere Pro 2024 (24.1.0)"
]

def run_command(cmd):
    try:
        subprocess.run(cmd, check=True, encoding='utf-8', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}. Error: {e}")
        sys.exit(1)

def download_file(url, folder, filename):
    if not url:
        return None
    
    safe_filename = "".join([c for c in filename if c.isalnum() or c in "._-"]).strip()
    filepath = os.path.join(folder, safe_filename)
    
    os.makedirs(folder, exist_ok=True)
    
    try:
        print(f"  Downloading: {url} -> {filepath}")
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return filepath
    except Exception as e:
        print(f"  [WARN] Failed to download {url}: {e}")
        return None

def main():
    print("===================================================")
    print(f"   Mystic Narratives Assembler v3.0 ({'VERTICAL' if IS_PORTRAIT else 'HORIZONTAL'})")
    print("===================================================")

    chapter_count = 1
    base_path = os.getcwd()
    
    video_title = "final_video"
    if os.path.exists("project_metadata.json"):
        try:
            with open("project_metadata.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                video_title = data.get("selectedTitle", "final_video")
        except: pass
            
    safe_title = "".join([c for c in video_title if c.isalnum() or c in " ._-"]).strip()
    output_file = f"{safe_title.replace(' ', '_')}.mp4"
    
    final_inputs = []
    
    for i in range(1, chapter_count + 1):
        chapter_num = f"{i:02d}"
        chapter_dir = os.path.join("chapters", f"chapter_{chapter_num}")
        
        if not os.path.exists(chapter_dir):
            continue
            
        print(f"\nProcessing Chapter {chapter_num}...")
        
        images_dir = os.path.join(chapter_dir, "images")
        images = sorted(glob.glob(os.path.join(images_dir, "*.[jJ][pP][gG]")) + 
                        glob.glob(os.path.join(images_dir, "*.[jJ][pP][eE][gG]")) +
                        glob.glob(os.path.join(images_dir, "*.[pP][nN][gG]")))
        
        if not images:
            print(f"  [WARN] No images in chapter {chapter_num}, skipping...")
            continue
            
        audio_path_mp3 = os.path.join(chapter_dir, "audio.mp3")
        audio_path_wav = os.path.join(chapter_dir, "audio.wav")
        audio_path = audio_path_mp3 if os.path.exists(audio_path_mp3) else audio_path_wav if os.path.exists(audio_path_wav) else None

        if not audio_path:
            print(f"  [WARN] No audio found for chapter {chapter_num}, skipping...")
            continue
        
        try:
            duration_str = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]).decode().strip()
            duration = float(duration_str)
        except:
            duration = 10.0
            
        img_duration = duration / len(images)
        total_frames = int(img_duration * 30)
        
        music_path = None
        sfx_inputs = []
        meta_path = os.path.join(chapter_dir, "metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                    if metadata.get('musicUrl'):
                        music_ext = os.path.splitext(urlparse(metadata['musicUrl']).path)[1] or '.mp3'
                        music_path = download_file(metadata['musicUrl'], chapter_dir, f"music{music_ext}")
                    
                    sfx_dir = os.path.join(chapter_dir, "sfx")
                    for sfx_meta in metadata.get('sfxTimings', []):
                        if sfx_meta.get('url'):
                            sfx_path = download_file(sfx_meta['url'], sfx_dir, os.path.basename(sfx_meta['filePath']))
                            if sfx_path:
                                sfx_inputs.append({
                                    'path': sfx_path,
                                    'startTime': sfx_meta.get('startTime', 0),
                                    'volume': sfx_meta.get('volume', 0.5)
                                })
            except Exception as e:
                 print(f"  [WARN] Could not process metadata.json for chapter {chapter_num}: {e}")

        chapter_out = os.path.join(chapter_dir, "chapter_out.mp4")
        
        cmd = ["ffmpeg", "-y"]
        
        for img in images:
            cmd += ["-loop", "1", "-t", str(img_duration), "-i", img]
            
        cmd += ["-i", audio_path]
        audio_idx = len(images)
        
        music_idx = -1
        if music_path:
            cmd += ["-stream_loop", "-1", "-i", music_path]
            music_idx = audio_idx + 1
        
        sfx_start_idx = audio_idx + 2 if music_path else audio_idx + 1
        for sfx in sfx_inputs:
            cmd += ["-i", sfx['path']]

        fc = []
        for j in range(len(images)):
            zoom = f"min(zoom+{ZOOM_SPEED},{MAX_ZOOM})"
            fc.append(f"[{j}:v]scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={TARGET_WIDTH}:{TARGET_HEIGHT},zoompan=z='{zoom}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={TARGET_WIDTH}x{TARGET_HEIGHT},setsar=1[v{j}]")
        
        concat_v = "".join([f"[v{j}]" for j in range(len(images))])
        fc.append(f"{concat_v}concat=n={len(images)}:v=1:a=0[bg]")
        
        sub_path = os.path.abspath(os.path.join(chapter_dir, "subtitles.srt")).replace('\\', '/').replace(':', '\\:')
        fc.append(f"[bg]subtitles='{sub_path}':force_style='{SUB_STYLE}'[v_final]")
        
        fc.append(f"[{audio_idx}:a]{SPEECH_FILTER}[speech]")
        audio_sources = ["[speech]"]
        
        if music_path:
            fc.append(f"[{music_idx}:a]volume={MUSIC_VOLUME}[mus]")
            audio_sources.append("[mus]")
            
        for idx, sfx in enumerate(sfx_inputs):
            curr_sfx_idx = sfx_start_idx + idx
            delay_ms = int(sfx['startTime'] * 1000)
            fc.append(f"[{curr_sfx_idx}:a]adelay={delay_ms}|{delay_ms},volume={sfx['volume']}[sfx{idx}]")
            audio_sources.append(f"[sfx{idx}]")
            
        fc.append(f"{''.join(audio_sources)}amix=inputs={len(audio_sources)}:duration=first:dropout_transition=2[a_final]")
        
        cmd += ["-filter_complex", ";".join(fc)]
        cmd += ["-map", "[v_final]", "-map", "[a_final]"]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
        cmd += METADATA_FLAGS + ["-shortest", chapter_out]
        
        run_command(cmd)
        final_inputs.append(f"file 'chapters/chapter_{chapter_num}/chapter_out.mp4'")

    with open("concat_list.txt", "w") as f:
        f.write("\n".join(final_inputs))
        
    print(f"\nMerging all chapters to {output_file}...")
    merge_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_list.txt", "-c", "copy"] + METADATA_FLAGS + [output_file]
    run_command(merge_cmd)
    
    if os.path.exists("concat_list.txt"): os.remove("concat_list.txt")
    print("\nSUCCESS! Video generated.")

if __name__ == "__main__":
    main()

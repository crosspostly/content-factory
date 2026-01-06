import sqlite3

# ... (imports)

# Config from config.py
LOGIN = config.RUTUBE_LOGIN
PASSWORD = config.RUTUBE_PASSWORD
BASE_URL = "https://rutube.ru"
YOUTUBE_CHANNEL_URL = config.YOUTUBE_CHANNEL_URL
PUBLIC_IP = config.PUBLIC_IP
SERVER_PORT = config.SERVER_PORT
UPLOAD_FOLDER = config.UPLOADS_DIR
COOKIES_FILE = config.YOUTUBE_COOKIES_FILE
DB_FILE = config.DB_FILE

def log(msg):
    print(f"[TEST] {msg}")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('CREATE TABLE IF NOT EXISTS synced (y_id TEXT PRIMARY KEY, title TEXT)')
    conn.commit()
    conn.close()

def is_video_synced(y_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute('SELECT 1 FROM synced WHERE y_id=?', (y_id,)).fetchone()
    conn.close()
    return res is not None

def save_to_db(y_id, title):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('INSERT OR REPLACE INTO synced VALUES (?, ?)', (y_id, title))
    conn.commit()
    conn.close()
    log(f"💾 Saved to DB: {y_id} - {title}")

# ... (ensure_server_running, get_token same as before)

def run_test():
    init_db()
    ensure_server_running()
    log("Authenticating...")
    token = get_token()
    if not token:
        log("❌ Auth failed")
        return
    log(f"✅ Auth Token: {token[:10]}...******")

    # 1. Get List
    log("Fetching video list from YouTube...")
    cmd = [config.YT_DLP_PATH, "--cookies", COOKIES_FILE, "--get-id", "--get-title", "--flat-playlist", "--playlist-end", "5", YOUTUBE_CHANNEL_URL] # Check top 5
    log(f"🔍 Executing CMD: {' '.join(cmd)}")
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log(f"❌ yt-dlp list error: {res.stderr}")
        return

    lines = res.stdout.strip().split("\n")
    if len(lines) < 2:
        log("❌ No videos found in output")
        log(f"Stdout: {res.stdout}")
        return

    # Find first unsynced video
    target_video = None
    for i in range(0, len(lines), 2):
        if i+1 >= len(lines): break
        t_title = lines[i]
        t_id = lines[i+1]
        
        if not is_video_synced(t_id):
            target_video = (t_title, t_id)
            break
        else:
            log(f"⏭️ Skipping already synced: {t_title}")

    if not target_video:
        log("✅ All recent videos are already synced.")
        return

    title, y_id = target_video
    
    # Добавляем идентификатор среды к названию
    env_tag = "[GHA]" if os.environ.get("FORCE_CATBOX") == "true" else "[Local]"
    title = f"{env_tag} {title}"
    
    log(f"🎬 Processing Video: {title} (ID: {y_id})")

    youtube_url = f"https://youtube.com/watch?v={y_id}"
    upload_url = None

    # ... (Direct Link and Fallback logic same as before, ensuring local_filename uses y_id)
    
    # 3. Fallback: Download & Serve -> Upload to Catbox
    if not upload_url:
        log("⚠️ Direct link failed/blocked. Switching to Download + Catbox Upload...")
        if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
        
        local_filename = f"{y_id}.mp4"
        local_path = os.path.join(UPLOAD_FOLDER, local_filename)
        
        # Check if exists
        if not os.path.exists(local_path):
            cmd_dl = [config.YT_DLP_PATH, "--cookies", COOKIES_FILE, "-f", "best[ext=mp4]/best", "-o", local_path, youtube_url]
            log(f"⬇️ Downloading CMD: {' '.join(cmd_dl)}")
            
            res_dl = subprocess.run(cmd_dl, capture_output=True, text=True)
            if res_dl.returncode != 0:
                log(f"❌ Download failed: {res_dl.stderr}")
                return
            log("✅ Download complete.")
        else:
            log("✅ File already exists locally.")
        
        # USE Catbox if FORCE_CATBOX env var is set (for GitHub Actions)
        if os.environ.get("FORCE_CATBOX") == "true":
            log("📦 Uploading to Catbox (GitHub Actions mode)...")
            uploader = RutubeUploader(LOGIN, PASSWORD)
            upload_url = uploader.upload_to_catbox(local_path)
            if not upload_url:
                log("❌ Catbox upload failed.")
                return
            log(f"✅ Catbox URL: {upload_url}")
        else:
            # USE DOMAIN with WEBHOOK HACK (to bypass Caddy path restrictions)
            upload_url = f"https://crosspostly.hopto.org/rutube-webhook/webhook?file={local_filename}"
            log(f"✅ Local Server URL (Webhook Hack): {upload_url}")

    # 4. Upload
    log("🚀 Preparing Upload to Rutube API...")
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    payload = {
        "url": upload_url,
        "title": title,
        "category_id": 13,
        "is_hidden": False, # PUBLIC ACCESS
        "description": f"Original: {youtube_url}"
    }
    
    log("📤 SENDING REQUEST:")
    # ... (Request sending)

    r = requests.post(f"{BASE_URL}/api/video/", json=payload, headers=headers)
    
    log("📥 RECEIVED RESPONSE:")
    log(f"Status Code: {r.status_code}")
    log(f"Body: {r.text}")

    if r.status_code in [200, 201]:
        vid_id = r.json().get('video_id') or r.json().get('id')
        log(f"🎉 Request accepted. Rutube ID: {vid_id}")
        
        # Optimistic Save to DB (or wait for confirmation)
        # We save immediately to avoid loop if processing takes long
        save_to_db(y_id, title)
        
        log("⏳ Waiting for processing results (polling status)...")
        
        # Polling loop ... (keep existing polling logic)

        
        # Polling loop
        max_retries = 30 # 30 * 5 sec = 150 sec timeout
        for i in range(max_retries):
            time.sleep(5)
            try:
                r_status = requests.get(f"{BASE_URL}/api/video/{vid_id}/", headers=headers)
                if r_status.status_code == 200:
                    data = r_status.json()
                    
                    # Check for errors/deletion
                    if data.get('is_deleted') is True:
                        reason = data.get('action_reason', {}).get('name', 'Unknown')
                        log(f"❌ UPLOAD FAILED! Status: Deleted. Reason: {reason}")
                        # Log detailed info if reason is error
                        log(f"Full Status dump: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        return

                    # Check for success (ready to watch?)
                    # Usually 'is_on_air' or just existence implies success, but let's look for specific states if available.
                    # For now, if it's NOT deleted and exists for a while, it's progress.
                    log(f"🔄 Status check {i+1}/{max_retries}: processing... (Deleted: {data.get('is_deleted')})")
                    
                    # If we want to wait until it's 'ready', we might wait forever if processing is slow. 
                    # But if we see 'error_upload_video' it happens fast.
                    
                else:
                    log(f"⚠️ Status check failed: {r_status.status_code}")
            except Exception as e:
                log(f"⚠️ Polling error: {e}")
                
        log("⚠️ Timeout waiting for final status.")
        
    else:
        log(f"❌ API Error. See response above.")

if __name__ == "__main__":
    run_test()

# -*- coding: utf-8 -*-
import os
import requests
import subprocess
import sys
import time
import json
import config
from rutube_uploader import RutubeUploader

# Config from config.py
LOGIN = config.RUTUBE_LOGIN
PASSWORD = config.RUTUBE_PASSWORD
BASE_URL = "https://rutube.ru"
YOUTUBE_CHANNEL_URL = config.YOUTUBE_CHANNEL_URL
PUBLIC_IP = config.PUBLIC_IP
SERVER_PORT = config.SERVER_PORT
UPLOAD_FOLDER = config.UPLOADS_DIR
COOKIES_FILE = config.YOUTUBE_COOKIES_FILE

def log(msg):
    print(f"[TEST] {msg}")

def ensure_server_running():
    try:
        requests.get(f"http://localhost:{SERVER_PORT}/health", timeout=1)
        return
    except:
        log("Starting local server...")
        server_script = os.path.join(os.path.dirname(__file__), "server_simple.py")
        subprocess.Popen([sys.executable, server_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(2)

def get_token():
    try:
        r = requests.post(f"{BASE_URL}/api/accounts/token_auth/", data={'username': LOGIN, 'password': PASSWORD})
        return r.json().get('token')
    except: return None

def run_test():
    ensure_server_running()
    log("Authenticating...")
    token = get_token()
    if not token:
        log("❌ Auth failed")
        return
    log(f"✅ Auth Token: {token[:10]}...******")

    # 1. Get List
    log("Fetching video list from YouTube...")
    cmd = [config.YT_DLP_PATH, "--cookies", COOKIES_FILE, "--get-id", "--get-title", "--flat-playlist", "--playlist-end", "1", YOUTUBE_CHANNEL_URL]
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

    title = lines[0]
    y_id = lines[1]
    log(f"🎬 Found Video: {title} (ID: {y_id})")

    youtube_url = f"https://youtube.com/watch?v={y_id}"
    upload_url = None

    # 2. Try Direct Link
    # FORCE SKIP DIRECT LINK to ensure stability
    log("⚠️ Skipping Direct Link check (forced local download mode)...")
    # try:
    #     cmd_url = [config.YT_DLP_PATH, "--cookies", COOKIES_FILE, "-g", "-f", "best[ext=mp4]/best", youtube_url]
    #     log(f"🔍 Executing CMD: {' '.join(cmd_url)}")
        
    #     res_url = subprocess.run(cmd_url, capture_output=True, text=True)
    #     if res_url.returncode == 0 and res_url.stdout.strip():
    #         upload_url = res_url.stdout.strip()
    #         log(f"✅ Direct link obtained: {upload_url[:60]}...")
    #     else:
    #          log(f"⚠️ Direct link fetch stderr: {res_url.stderr}")
    # except Exception as e:
    #     log(f"⚠️ Direct link exception: {e}")

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
        "is_hidden": True,
        "description": f"Test upload of {youtube_url}"
    }
    
    log("📤 SENDING REQUEST:")
    log(f"URL: {BASE_URL}/api/video/")
    log(f"Headers: Authorization: Token {token[:10]}...")
    log(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    r = requests.post(f"{BASE_URL}/api/video/", json=payload, headers=headers)
    
    log("📥 RECEIVED RESPONSE:")
    log(f"Status Code: {r.status_code}")
    log(f"Body: {r.text}")

    if r.status_code in [200, 201]:
        vid_id = r.json().get('video_id') or r.json().get('id')
        log(f"🎉 Request accepted. Rutube ID: {vid_id}")
        log("⏳ Waiting for processing results (polling status)...")
        
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

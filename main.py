# main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
from typing import Dict, Optional

app = FastAPI(title="YouTube Audio Stream API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_audio_info(video_url: str) -> Dict:
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if not audio_formats:
                raise HTTPException(status_code=404, detail="No audio streams found")
            
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
            
            return {
                'title': info.get('title'),
                'url': best_audio.get('url'),
                'format': best_audio.get('format'),
                'filesize': best_audio.get('filesize'),
                'abr': best_audio.get('abr'),
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "YouTube Audio Stream API"}

@app.get("/audio/{video_id}")
def get_audio_stream(video_id: str):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return get_audio_info(video_url)

# Add this at the end of main.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

from flask import Flask, jsonify
import yt_dlp

app = Flask(__name__)

def get_audio_url(video_url):
    """Extract audio stream URL from YouTube video."""
    ydl_opts = {
        'format': 'bestaudio',
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video information
            info = ydl.extract_info(video_url, download=False)
            
            # Get the best audio format
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if audio_formats:
                # Return the highest quality audio stream URL
                best_audio = max(audio_formats, key=lambda f: f.get('abr', 0))
                return {
                    'success': True,
                    'url': best_audio.get('url'),
                    'format': best_audio.get('format'),
                    'bitrate': best_audio.get('abr')
                }
            else:
                return {'success': False, 'error': 'No audio stream found'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/audio/<video_id>')
def get_youtube_audio(video_id):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    result = get_audio_url(video_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

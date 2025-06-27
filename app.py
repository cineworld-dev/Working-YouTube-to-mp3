from flask import Flask, request, jsonify, send_file, after_this_request
import yt_dlp
import os
import uuid

app = Flask(__name__)

DEFAULT_YOUTUBE_URL = "https://youtu.be/LrM62pv56o0"

@app.route('/')
def home():
    return jsonify({
        "message": "YouTube to MP3 API is working!",
        "usage": "/convert?url=YOUTUBE_URL",
        "note": "Using default video if 'url' param is missing",
        "default": DEFAULT_YOUTUBE_URL,
        "created_by": "Zero Creations"
    })

@app.route('/convert', methods=['GET'])
def convert():
    url = request.args.get("url") or DEFAULT_YOUTUBE_URL

    # Clean URL
    if "?si=" in url:
        url = url.split("?si=")[0]
    if "&" in url:
        url = url.split("&")[0]

    # filename WITHOUT extension
    base_filename = f"{uuid.uuid4().hex}"
    expected_file = f"{base_filename}.mp3"

    options = {
        'format': 'bestaudio/best',
        'outtmpl': base_filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': True,
    }

    try:
        print(f"🎬 Downloading: {url}")
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        # Sometimes yt-dlp might add .mp3 again, check both
        final_file = expected_file
        if not os.path.exists(final_file):
            double_ext_file = expected_file + ".mp3"
            if os.path.exists(double_ext_file):
                final_file = double_ext_file
            else:
                print("❌ File not found after download.")
                return jsonify({"error": "Failed to download MP3."}), 500

        @after_this_request
        def cleanup(response):
            try:
                os.remove(final_file)
                print(f"🗑️ Deleted: {final_file}")
            except Exception as e:
                print(f"⚠️ Error deleting file: {e}")
            return response

        print(f"✅ Sending: {final_file}")
        return send_file(final_file, as_attachment=True, mimetype='audio/mpeg')

    except Exception as e:
        print(f"🔥 Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

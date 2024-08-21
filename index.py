from flask import Flask, request, jsonify, make_response
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, world!'

@app.route('/data', methods=['POST'])
def get_subtitles():
    video_url = request.json.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query).get('v', [None])[0]

    if not video_id:
        path_segments = parsed_url.path.split('/')
        video_id = path_segments[-1] if path_segments[-1] else path_segments[-2]

    if not video_id:
        return jsonify({'error': 'Video ID could not be extracted'}), 400

    print("Extracted Video ID:", video_id)

    lang = request.json.get('lang', 'en')
    
    subtitles = None
    try:
        subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return jsonify({'error': 'Error fetching subtitles: ' + str(e)}), 500

    if not subtitles:
        return jsonify({'error': 'No subtitles found for this video'}), 404

    subtitles_text = "\n".join([sub['text'] for sub in subtitles])

    response = make_response(subtitles_text)
    response.headers['Content-Disposition'] = f'attachment; filename={video_id}_subtitles.txt'
    response.headers['Content-Type'] = 'text/plain'

    return response

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    app.run(host='0.0.0.0', port=port)

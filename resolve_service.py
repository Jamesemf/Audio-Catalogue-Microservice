import requests
import os
from flask import Flask, request

KEY = os.environ["AUDD_KEY"]
URI = "https://api.audd.io/"
catalogue = "http://localhost:3000/catalogue"

app = Flask(__name__)

@app.route("/resolver", methods=["POST"])
def Resolve():
    """
    Identifies a song from an audio fragment and returns the track details.
    
    Request JSON:
    {
        "file": "<base64_encoded_audio>"
    }

    Returns:
        200 OK - Track found and returned.
        404 Not Found - Track not in the catalogue.
        500 Internal Server Error - Recognition failed.
        400 Bad Request - Invalid request.
    """
    js = request.get_json()
    fragment = js.get("file")
    if fragment != None:
        song_name = Solve_song(fragment)
        if song_name != None:
            catalogue_song = requests.get(f'{catalogue}/{song_name}')
            return catalogue_song.json(), catalogue_song.status_code
        else:
            return "",500 # Internal Server Error
    else:
        return "",400 # Bad Request

def Solve_song(fragment):
    """
    Sends an audio fragment to audd API for song recognition.
    
    Args:
        fragment (str): Base64 encoded audio fragment.

    Returns:
        str: Recognized song title or None if recognition fails.
    """

    data = {
        'api_token': KEY,
        'audio': fragment,
        'return': 'timecode'
    }

    response = requests.post(URI, data=data).json()
    title = response.get('result', {}).get('title')
    return title  # Prevents crashes

def Launcher():
    app.run(host="localhost", port=3001)

if __name__ == "__main__":
    Launcher()
    


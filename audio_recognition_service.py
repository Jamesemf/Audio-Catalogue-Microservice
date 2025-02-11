import requests
import os
from flask import Flask, jsonify, request

KEY = os.environ["AUDD_KEY"]
URI = "https://api.audd.io/"
CATALOGUE = "http://localhost:3001/catalogue"

app = Flask(__name__)

@app.route("/audio_recognition", methods=["POST"])
def recognise():
    """
    Identifies a song from an audio fragment and returns the track details.
    
    Request JSON:
    {
        "file": "<base64_encoded_audio>"
    }

    Returns:
        200 OK - Track found and returned.  (returned by get)
        404 Not Found - Track not in the catalogue. (returned by get)
        500 Internal Server Error - Recognition failed.
        400 Bad Request - Invalid request.
    """
    data = request.get_json()
    fragment = data.get("file")

    if not fragment:
        return jsonify({'message': 'No audio fragment provided'}), 400

    song_name, status_code = Solve_song(fragment)

    if status_code != 200 or not song_name:
        return song_name, status_code  # song_name will contain an error message JSON

    # If song recognized, look it up in the catalogue
    catalogue_song = requests.get(f'{CATALOGUE}/{song_name}')

    if catalogue_song.status_code == 200:
        return jsonify(catalogue_song.json()), 200
    elif catalogue_song.status_code == 404:
        return jsonify({'message': 'Track not found in catalogue'}), 404
    else:
        return jsonify({'message': 'Error retrieving track from catalogue'}), 500

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
    print(response['result'])
    
    return handle_api_response(response)
    
def handle_api_response(response):
    """
    Wrapper function to handle API responses consistently.

    Args:
        response (requests.Response): The response object from the API.

    Returns:
        ( ,int): Tuple containing the Flask JSON response and status code.
    """

    if response == None:
        return jsonify({'message': 'No response from API'}), 500
    
    if response['status'] == "error":
        error_code = response["error"].get("error_code", "N/A")
        error_message = response["error"].get("error_message", "N/A")
        return {'message': f'API Error: {error_message}'}, error_code

    if response['status'] == "success":
            if response['result'] == None:
                return jsonify({'message': f'API found no result'}), 404
            return response.get('result', {}).get('title'), 200


def Launcher():
    app.run(host="localhost", port=3002)

if __name__ == "__main__":
    Launcher()
    


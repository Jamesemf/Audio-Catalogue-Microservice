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
    Identifies a song from an audio fragment and returns the track name

    Request JSON:
    {
        "file": "<base64_encoded_audio>"
    }

    Returns:
        200 OK - Track found and returned.
        404 Not Found - Track not found.
        500 Internal Server Error - Recognition failed.
        400 Bad Request - Invalid request.
    """
    js = request.get_json()

    # Prepare data for the Audd api
    data = {
        'api_token': KEY,
        'audio': js.get("file"),
        'return': 'timecode'
    }

    # Send the audio data to Audd
    response = requests.post(URI, data=data).json()
    
    return handle_api_response(response)

def handle_api_response(response):
    """
    Handles the response from the audio recognition API and formats it for the client.

    Args:
        response (dict): The response object from the API.

    Returns:
        (JSON, int): Tuple containing the Flask JSON response and status code.
    """

    if response == None:
        return jsonify({'message': 'No response from API'}), 500 # No response received
    
    if response['status'] == "error":
        error_code = response["error"].get("error_code", "N/A")
        error_message = response["error"].get("error_message", "N/A")
        return jsonify({'message': f'API Error: {error_message}'}), error_code # API return an error

    if response['status'] == "success":
            if response['result'] == None:
                return jsonify({'message': f'API found no result'}), 404 # No result found
            return jsonify({'name':response.get('result', {}).get('title')}), 200 # Return the track title


def Launcher():
    app.run(host="localhost", port=3002)

if __name__ == "__main__":
    Launcher()
    


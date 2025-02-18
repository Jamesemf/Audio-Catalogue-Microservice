from flask import Flask, request, jsonify
import requests

CATALOGUE_SERVICE_URL = 'http://localhost:3000/catalogue'
AUDIO_RECOGNITION_SERVICE_URL = 'http://localhost:3002/audio_recognition'

app = Flask(__name__)
@app.route("/shamzam/add_track", methods=["PUT"])
def AddTrack():
    """
    Adds a new track to the catalogue.
    
    Request JSON:
    {
        "file": "<base64_encoded_audio>"
    }
    
    Returns:
        201 Created - Track successfully added.
        403 Forbidden - Track already exists.
        400 Bad Request - Invalid request data.
        500 Internal Server Error - Database error.
    """

    file = request.get_json().get('file')   # Retrieve the audio file from the request JSON

    if file == None:
        return jsonify({'message': 'No track provided'}), 400
    
    # Send the file to the audio recognition service to identify the track
    response = requests.post(AUDIO_RECOGNITION_SERVICE_URL, json=request.get_json())

    if response.status_code != 200:
        return jsonify(response.json()), response.status_code
    
    # Extract the recognized track name
    track_name = response.json().get('name')
    combined = {'name': track_name, 'file':file} # response.text is the name of the song if 

    # Add the recognized track to the catalogue
    response = requests.post(f'{CATALOGUE_SERVICE_URL}/add_track', json=combined)

    if response.status_code == 201:
        return jsonify({'name':track_name}), 201

    if response != None:
        return '', response.status_code
    
    return jsonify({'message': 'Internal server error'}), 500
    
        
@app.route("/shamzam/remove_track/<string:name>", methods=["DELETE"])
def RemoveTrack(name):
    """
    Deletes a track from the catalogue.
    
    Returns:
        204 No Content - Successfully deleted.
        404 Not Found - Track does not exist.
        500 Internal Server Error - Database error.
    """

    response = requests.delete(f'{CATALOGUE_SERVICE_URL}/delete_track', json={'name': name})
    if response != None:
        return '', response.status_code

    return jsonify({'message': 'Internal server error'}), 500
    
@app.route("/shamzam/list_tracks", methods=["GET"])
def ListTracks():
    """
    Lists all tracks in the catalogue.
    
    Returns:
        200 OK - List of track names in JSON format.
        500 Internal Server Error - If the catalogue cannot be accessed.
    """
    response = requests.get(f'{CATALOGUE_SERVICE_URL}/list_tracks')
    if response != None:
        return jsonify(response.json()), response.status_code

    return jsonify({'message': 'Internal server error'}), 500
    
@app.route("/shamzam/retrieve_track/<string:name>", methods=["GET"])
def RetrieveTrack(name):
    """
    Retrieves a track by name.
    
    Returns:
        200 OK - Track found.
        404 Not Found - Track does not exist.
        500 Internal Server Error - Database error.
    """
    response = requests.get(f'{CATALOGUE_SERVICE_URL}/retrieve_track', json={'name':name})
    if response != None:
        return jsonify(response.json()), response.status_code
    
    return jsonify({'message': 'Internal server error'}), 500

@app.route("/shamzam/recognise_fragment", methods=["POST"])
def recognise():
    """
    Recognizes a song from an audio fragment and checks if it's in the catalogue.

    Request JSON:
    {
        "file": "<base64_encoded_audio>"
    }

    Returns:
        200 OK - Track found in the catalogue.
        404 Not Found - Track not found in the catalogue.
        400 Bad Request - No audio fragment provided.
        500 Internal Server Error - Audio recognition or database error.
    """

    # Retrieve the audio fragment from the request
    file = request.get_json().get('file')
    if file == None:
        return jsonify({'message': 'No audio fragment provided'}), 400
    
    # Send the audio fragment to Audd
    response = requests.post(AUDIO_RECOGNITION_SERVICE_URL, json=request.get_json())
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    # Extract the recognized track name
    track_name = response.json().get('name')

    # Check if the recognized track is in the catalogue
    catalogue_song = requests.get(f'{CATALOGUE_SERVICE_URL}/retrieve_track', json={'name':track_name})
    
    if catalogue_song.status_code == 200:
        return catalogue_song.json(), 200
    elif catalogue_song.status_code == 404:
        return jsonify({'message': 'Track not found in catalogue'}), 404
    else:
        return jsonify({'message': 'Error retrieving track from catalogue'}), 500

def Launcher():
    app.run(host="localhost", port=3001)

if __name__ == "__main__":
    Launcher()
    



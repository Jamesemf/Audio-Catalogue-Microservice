from flask import Flask, request, jsonify
import requests

DATABASE_SERVICE_URL = 'http://localhost:3000/database'

app = Flask(__name__)
@app.route("/catalogue/<string:name>", methods=["PUT"])
def AddTrack(name):
    """
    Adds a new track to the catalogue.
    
    Request JSON:
    {
        "name": "Track Name",
        "file": "<base64_encoded_audio>"
    }
    
    Returns:
        201 Created - Track successfully added.
        403 Forbidden - Track already exists.
        400 Bad Request - Invalid request data.
        500 Internal Server Error - Database error.
    """
    data = request.get_json()

    if data.get('name') != name or not data.get('file'):
        return '', 400 # Bad Request
    
    response = requests.post(f'{DATABASE_SERVICE_URL}/add_track', json=data)
    if response != None:
        return '', response.status_code
    
    return "", 500 # Internal server error
    
        
@app.route("/catalogue/<string:name>", methods=["DELETE"])
def RemoveTrack(name):
    """
    Deletes a track from the catalogue.
    
    Returns:
        204 No Content - Successfully deleted.
        404 Not Found - Track does not exist.
        500 Internal Server Error - Database error.
    """

    response = requests.delete(f'{DATABASE_SERVICE_URL}/delete_track', json={'name': name})
    if response != None:
        return '', response.status_code

    return "",500 # Internal server error
    
@app.route("/catalogue", methods=["GET"])
def ListTracks():
    """
    Lists all tracks in the catalogue.
    
    Returns:
        200 OK - List of track names in JSON format.
    """
    response = requests.get(f'{DATABASE_SERVICE_URL}/list_tracks')
    print(response)
    if response != None:
        return jsonify(response.json()), response.status_code

    return "", 500 # Internal server error
    
@app.route("/catalogue/<string:name>", methods=["GET"])
def RetrieveTrack(name):
    """
    Retrieves a track by name.
    
    Returns:
        200 OK - Track found.
        404 Not Found - Track does not exist.
    """
    response = requests.get(f'{DATABASE_SERVICE_URL}/retrieve_track', json={'name':name})
    if response != None:
        return jsonify(response.json()), response.status_code
    
    return "", 500 # Not Found


def Launcher():
    app.run(host="localhost", port=3001)

if __name__ == "__main__":
    Launcher()
    



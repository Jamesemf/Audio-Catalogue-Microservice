from flask import Flask, request, jsonify
from catalogue import catalogue_db

app = Flask(__name__)

@app.route('/catalogue/add_track', methods=['POST'])
def add_track():
    """
    Adds a new track to the catalogue.

    Request JSON:
    {
        "name": "<track_name>",
        "file": "<base64_encoded_audio>"
    }

    Returns:
        201 Created - Track successfully added.
        403 Forbidden - Track already exists in the catalogue.
        500 Internal Server Error - An unexpected error occurred.
    """
    data = request.get_json()
    try:
        # Attempt to add the track to the catalogue
        if catalogue_db.add_track(data['name'], data['file']):
            return "", 201 # Track added successfully
        else:
            return jsonify({'message': 'Track already exists'}), 403 # Track already exists
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/catalogue/delete_track', methods=['DELETE'])
def delete_track():
    """
    Deletes a track from the catalogue.

    Request JSON:
    {
        "name": "<track_name>"
    }

    Returns:
        204 No Content - Track successfully deleted.
        404 Not Found - Track does not exist in the catalogue.
    """
    data = request.get_json()
    if catalogue_db.delete_track(data['name']):
        return "", 204 # Track deleted successfully
    else:
        return jsonify({'message': 'Track not found'}), 404 # Track not found

@app.route('/catalogue/list_tracks', methods=['GET'])
def list_tracks():
    """
    Lists all tracks in the catalogue.

    Returns:
        200 OK - List of all tracks in JSON format.
    """
    tracks = catalogue_db.list_tracks()
    return jsonify(tracks), 200 # Return list of tracks

@app.route('/catalogue/retrieve_track', methods=['GET'])
def retrieve_track():
    """
    Retrieves a specific track by name from the catalogue.

    Request JSON:
    {
        "name": "<track_name>"
    }

    Returns:
        200 OK - Track details found and returned.
        404 Not Found - Track does not exist in the catalogue.
    """
    data = request.get_json()
    track = catalogue_db.retrieve_track(data['name'])
    if track:
      return jsonify(track), 200 # Track found

    return jsonify({'message': 'Track not found'}), 404 # Track not found

def Launcher():
    app.run(host="localhost", port=3000)

if __name__ == "__main__":
    Launcher()
    
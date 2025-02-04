import requests
import base64
import model
import os
import sqlite
import json
from flask import Flask, request


KEY = os.environ["AUDD_KEY"]
URI = "https://api.audd.io/"

app = Flask(__name__)

@app.route("/catalogue/<string:name>", methods=["PUT"])
def Add(name):
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
    js = request.get_json()
    name2 = js.get("name")
    file = js.get("file")

    if name2 != None and file != None and name == name2:
        track = model.Track(name,file)
        if repo.lookup(name) != None:
                return "" ,403 # Already exists
        else:
            if repo.insert(track):
                return "" ,201 # Created
            else:
                return "" ,500 # Internal Server Error
    else:
        return "" ,400 # Bad Request
    
@app.route("/catalogue/<string:name>", methods=["GET"])
def get(name):
    """
    Retrieves a track by name.
    
    Returns:
        200 OK - Track found.
        404 Not Found - Track does not exist.
    """
    track = repo.lookup(name)
    if track != None:
            return {"name":track.name, "file":track.file}, 200 # OK
    else:
        return "", 404 # Not Found

    
@app.route("/catalogue/<string:name>", methods=["DELETE"])
def remove(name):
    """
    Deletes a track from the catalogue.
    
    Returns:
        204 No Content - Successfully deleted.
        404 Not Found - Track does not exist.
        500 Internal Server Error - Database error.
    """
    if not repo.lookup(name):
        return "", 404 # Not Found
    
    if repo.delete(name):
        return "",204 # No Content
    
    return "",500 # Internal server error
    
@app.route("/catalogue", methods=["GET"])
def list():
    """
    Lists all tracks in the catalogue.
    
    Returns:
        200 OK - List of track names in JSON format.
    """
    names = repo.list()
    size = len(names)
    js = "["
    for n, name in enumerate(names):
        js += "\"" + name + "\""
        if n < size - 1 : js += ","
    js += "]"
    return js, 200 # ok

@app.route("/catalogue/convert", methods=["POST"])
def endpoint():
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
        song_name = solve_song(fragment)
        if song_name != None:
            catalogue_song = repo.lookup(song_name)
            if catalogue_song != None:
                return {"name":catalogue_song.name, "file":catalogue_song.file}, 200
            else:
                return "", 404 # Not Found
        else:
            return "",500 # Internal Server Error
    else:
        return "",400 # Bad Request

def solve_song(fragment):
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
    return response.get('result', {}).get('title')  # Prevents crashes

def launcher():
    global repo
    repo = sqlite.Catalogue("catalogue")
    app.run(host="localhost", port=3000)

if __name__ == "__main__":
    launcher()
    


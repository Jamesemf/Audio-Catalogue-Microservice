import model
import sqlite
from flask import Flask, request

app = Flask(__name__)
repo = sqlite.Catalogue("catalogue")

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
def FindTrack(name):
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
def Remove(name):
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
def List():
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

@app.route("/catalogue/cleardatabase", methods=["DELETE"])
def Clear():
    if repo.clear():
        return "", 204
    
    return "",500


def Launcher():
    app.run(host="localhost", port=3000)

if __name__ == "__main__":
    Launcher()
    



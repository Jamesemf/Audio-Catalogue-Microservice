import database
from flask import Flask, request


app = Flask(__name__)
@app.route("/catalogue/<string:name>", methods=["GET"])
def RetrieveTrack(name):
    """
    Retrieves a track by name.
    
    Returns:
        200 OK - Track found.
        404 Not Found - Track does not exist.
    """
    track = database.db.lookup(name)
    if track != None:
            return {"name":track.name, "file":track.file}, 200 # OK
    else:
        return "", 404 # Not Found

def Launcher():
    app.run(host="localhost", port=3002)

if __name__ == "__main__":
    Launcher()
    



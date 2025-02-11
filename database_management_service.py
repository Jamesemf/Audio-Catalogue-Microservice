from flask import Flask, request, jsonify
from catalogue import catalogue

app = Flask(__name__)

@app.route('/database/add_track', methods=['POST'])
def add_track():
    data = request.get_json()
    try:
        if catalogue.add_track(data['name'], data['file']):
            return "", 201
        else:
            return jsonify({'message': 'Track already exists'}), 403
    except Exception as e:
        return jsonify({'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/database/delete_track', methods=['DELETE'])
def delete_track():
    data = request.get_json()
    if catalogue.delete_track(data['name']):
        return "", 204
    else:
        return jsonify({'message': 'Track not found'}), 404

@app.route('/database/list_tracks', methods=['GET'])
def list_tracks():
    tracks = catalogue.list_tracks()
    return jsonify(tracks), 200

@app.route('/database/retrieve_track', methods=['GET'])
def retrieve_track():
    data = request.get_json()
    track = catalogue.retrieve_track(data['name'])
    if track:
      return jsonify(track), 200

    return jsonify({'message': 'Track not found'}), 404

def Launcher():
    app.run(host="localhost", port=3000)

if __name__ == "__main__":
    Launcher()
    

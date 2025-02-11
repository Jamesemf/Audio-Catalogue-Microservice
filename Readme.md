# Shamzam Microservices

Shamzam is a microservice-based application designed for audio recognition and catalog management. It integrates with an external API (Audd.io) to identify audio fragments and manages a catalogue of recognized tracks. The application consists of three microservices:

1. **Audio Recognition Service** - Identifies songs from audio fragments using Audd.io API.
2. **Catalogue Service** - Manages the track catalogue including adding, deleting, and listing tracks.
3. **Shamzam Service** - Provides a unified interface for interacting with the other two services.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` for package management
- Audd.io API key (set as an environment variable `AUDD_KEY`)

### Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up environment variables:
    ```bash
    export AUDD_KEY=your_audd_api_key
    ```

### Running the Services

Each microservice runs on a different port locally. Use the following commands to start them:

1. **Catalogue Service** (Port 3000):
    ```bash
    python catalogue_service.py
    ```

2. **Shamzam Service** (Port 3001):
    ```bash
    python shamzam_service.py
    ```

3. **Audio Recognition Service** (Port 3002):
    ```bash
    python audio_recognition_service.py
    ```

### Running Tests

Unit tests are provided to validate the functionality of the microservices:

```bash
python -m unittest test_microservices.py
```

## API Endpoints

### Audio Recognition Service
- `POST /audio_recognition`: Recognizes a song from an audio fragment.

### Catalogue Service
- `POST /catalogue/add_track`: Adds a new track.
- `DELETE /catalogue/delete_track`: Deletes a track.
- `GET /catalogue/list_tracks`: Lists all tracks.
- `GET /catalogue/retrieve_track`: Retrieves a specific track.

### Shamzam Service
- `PUT /shamzam/add_track`: Adds a new track.
- `DELETE /shamzam/<name>`: Deletes a track by name.
- `GET /shamzam`: Lists all tracks.
- `GET /shamzam/<name>`: Retrieves a specific track by name.
- `POST /shamzam/recognise_fragment`: Recognise a track in the catalogue by audio fragment.


## Acknowledgments

- [Audd.io](https://audd.io/) for the audio recognition API.


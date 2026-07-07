# Track Trace — Music Recognition Microservices

A small "Shazam-style" system built as three cooperating Flask microservices. Administrators maintain a catalogue of music tracks; users can submit a short audio fragment and get back the full track it came from, identified via the [AudD](https://audd.io/) music recognition API.

## Architecture

| Service | File | Port | Role |
|---|---|---|---|
| Admin service | `admin_service.py` | 3000 | Add, remove, and list tracks in the catalogue |
| Recognition service | `audd_service.py` | 3001 | Identify a song from an audio fragment and fetch it from the catalogue |
| User service | `user_service.py` | 3002 | Retrieve a track by name |

Supporting modules:

- `model.py` — the `Track` data class (name + audio file).
- `catalogue.py` — SQLite-backed catalogue with insert / lookup / update / delete / list operations.
- `database.py` — shared database instance used by all services (creates `catalogue.db`).
- `test_microservices.py` — end-to-end integration tests covering all three services.

The recognition service calls the user service internally to return the full track once AudD has identified the fragment, so the services communicate over HTTP just as they would when deployed independently.

```
client ──► admin service (3000) ──► SQLite catalogue
client ──► user service (3002)  ──► SQLite catalogue
client ──► audd service (3001)  ──► AudD API
                     └──────────► user service (3002)
```

## API

### Admin service (port 3000)

| Method | Endpoint | Description | Responses |
|---|---|---|---|
| `PUT` | `/catalogue/<name>` | Add a track. Body: `{"name": "...", "file": "<base64 audio>"}` (name must match the URL) | `201` created, `403` already exists, `400` bad request, `500` error |
| `DELETE` | `/catalogue/<name>` | Remove a track | `204` deleted, `404` not found, `500` error |
| `GET` | `/catalogue` | List all track names | `200` JSON array of names |

### User service (port 3002)

| Method | Endpoint | Description | Responses |
|---|---|---|---|
| `GET` | `/catalogue/<name>` | Retrieve a track by name | `200` `{"name": ..., "file": ...}`, `404` not found |

### Recognition service (port 3001)

| Method | Endpoint | Description | Responses |
|---|---|---|---|
| `POST` | `/audd` | Identify a fragment. Body: `{"file": "<base64 audio>"}` | `200` full track returned, `404` identified but not in catalogue, `500` recognition failed, `400` bad request |

Audio is exchanged as base64-encoded data inside JSON bodies.

## Getting started

### Prerequisites

- Python 3.8+
- An [AudD API key](https://dashboard.audd.io/) (free tier available)

### Setup

```bash
pip install flask requests
```

Set your AudD API key (required by the recognition service):

```bash
# Windows (PowerShell)
$env:AUDD_KEY = "your-api-token"

# Linux / macOS
export AUDD_KEY="your-api-token"
```

### Run

Start each service in its own terminal:

```bash
python admin_service.py   # port 3000
python audd_service.py    # port 3001
python user_service.py    # port 3002
```

The SQLite database (`catalogue.db`) is created automatically on first run.

### Example usage

```bash
# Add a track (base64-encode the audio first)
curl -X PUT http://localhost:3000/catalogue/MySong \
     -H "Content-Type: application/json" \
     -d '{"name": "MySong", "file": "<base64 audio>"}'

# List the catalogue
curl http://localhost:3000/catalogue

# Identify a fragment and retrieve the full track
curl -X POST http://localhost:3001/audd \
     -H "Content-Type: application/json" \
     -d '{"file": "<base64 audio fragment>"}'
```

## Testing

`test_microservices.py` contains 14 integration tests that exercise the full system: adding, listing, retrieving, and deleting tracks, plus fragment recognition (including unknown songs and non-music audio).

The tests expect all three services to be running, plus a set of `.wav` files in the repository root — full tracks (e.g. `Blinding Lights.wav`) and matching fragments prefixed with an underscore (e.g. `_Blinding Lights.wav`). Audio files are not committed (see `.gitignore`), so supply your own.

```bash
python -m unittest test_microservices.py -v
```

## Notes

- This project was built for a university Enterprise Computing module to demonstrate a microservice architecture with REST APIs and inter-service communication.
- Tracks are stored as BLOBs in SQLite; this is fine for a demo but not intended for production-scale audio storage.

import base64
import requests
import unittest

catalogue = "http://localhost:3000/catalogue"
resolver = "http://localhost:3001/resolver"
hdrs = {"Content-Type":"application/json"}

 # List of tracks to upload
tracks = [
    {"filename": "Blinding Lights.wav", "name": "Blinding Lights"},
    {"filename": "Dont Look Back In Anger.wav", "name": "Blinding Lights"},  # Note: same name as above
    {"filename": "good 4 u.wav", "name": "good 4 u"},
    {"filename": "Everybody (Backstreets Back) (Radio Edit).wav", "name": "Everybody (Backstreet's Back) (Radio Edit)"}
]

class Testing(unittest.TestCase):

    def clear_database(self):
        """Helper function to clear the database."""
        requests.delete(f'{catalogue}/cleardatabase')

    def test_01_add_track(self):
        """Tests adding a new track to the catalogue."""

        self.clear_database()

        with open("Blinding Lights.wav", "rb") as track:
            name = "Blinding Lights"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 201)

        track.close()

    # Unhappy path
    def test_02_add_existing_track(self):
        """Tests attempting to add a duplicate track."""

        self.clear_database()

        with open("good 4 u.wav", "rb") as track:
            name = "good 4 u"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 403)

        track.close()
        
    def test_03_list_tracks(self):
        """Tests listing all tracks."""

        self.clear_database()

        for track in tracks:
            with open(track["filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                payload = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue}/{track["name"]}', headers=hdrs, json=payload)

        response = requests.get(f'{catalogue}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Blinding Lights" in response.text)


    def test_04_get_track(self):
        """Tests retrieving an existing track by name."""
        
        self.clear_database()

        for track in tracks:
            with open(track["filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                payload = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue}/{track["name"]}', headers=hdrs, json=payload)

                # Retrieve track
                response = requests.get(f'{catalogue}/{track["name"]}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))

    #Unhappy path
    def test_05_get_non_existent_track(self):
        """Tests retrieving a non-existent track."""

        self.clear_database()

        rsp = requests.get(f'{catalogue}/Scooby-doo')
        self.assertEqual(rsp.status_code, 404)        
    
    def test_06_delete_track(self):
        """Tests deleting a track."""
    
        self.clear_database()

        for track in tracks:
            with open(track["filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                payload = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue}/{track["name"]}', headers=hdrs, json=payload)

                delete_response = requests.delete(f'{catalogue}/{track["name"]}')
                self.assertEqual(delete_response.status_code, 204)

    def test_07_resolve_fragment(self):
        """Tests locating a song in the catalogue based on a fragment."""

        self.clear_database()

        # List of tracks and their corresponding fragments
        tracks_and_fragments = [
            {
                "track_filename": "Everybody (Backstreets Back) (Radio Edit).wav",
                "fragment_filename": "_Everybody (Backstreets Back) (Radio Edit).wav",
                "name": "Everybody (Backstreet's Back) (Radio Edit)"
            },
            {
                "track_filename": "Blinding Lights.wav",
                "fragment_filename": "_Blinding Lights.wav",
                "name": "Blinding Lights"
            }
        ]

        for item in tracks_and_fragments:
            with open(item["track_filename"], "rb") as track_file:
                encoded_track = base64.b64encode(track_file.read()).decode("utf-8")
                payload = {"name": item["name"], "file": encoded_track}
                requests.put(f'{catalogue}/{item["name"]}', headers=hdrs, json=payload)

            with open(item["fragment_filename"], "rb") as fragment_file:
                encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
                fragment_payload = {"file": encoded_fragment}
                response = requests.post(f'{resolver}', headers=hdrs, json=fragment_payload)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))
            
    # Unhappy Path
    def test_08_non_music_fragment(self):
        """Tests locating a song that is not in the catalogue based on a fragment."""

        self.clear_database() # Clear the database

        with open("_Davos.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            js = {"name":None,"file": encoded_fragment}
            rsp = requests.post(f'{resolver}', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 500)



            


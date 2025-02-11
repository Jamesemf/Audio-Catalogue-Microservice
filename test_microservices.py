import base64
import requests
import unittest
import Catalogue

CATALOGUE = "http://localhost:3001/catalogue"
AUDIO_RECOGNITION = "http://localhost:3002/audio_recognition"
hdrs = {"Content-Type":"application/json"}


# List of tracks and their corresponding fragments
tracks = [
            {
                "track_filename": "Everybody (Backstreets Back) (Radio Edit).wav",
                "fragment_filename": "_Everybody (Backstreets Back) (Radio Edit).wav",
                "name": "Everybody (Backstreet's Back) (Radio Edit)"
            },
            {
                "track_filename": "Blinding Lights.wav",
                "fragment_filename": "_Blinding Lights.wav",
                "name": "Blinding Lights"
            },
            {
                "track_filename": "Dont Look Back In Anger.wav",
                "fragment_filename": "_Dont Look Back In Anger.wav",
                "name": "Don't Look Back In Anger"
            },
            {
                "track_filename": "good 4 u.wav",
                "fragment_filename": "_good 4 u.wav",
                "name": "good 4 u"
            }
        ]

class TestUserStoryOne(unittest.TestCase):

    # ----------------Happy case---------------
    def test_add_track(self):
        """Tests adding a new track to the catalogue."""

        Catalogue.catalogue.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                rsp = requests.put(f'{CATALOGUE}/{track["name"]}', headers=hdrs, json=js)
                self.assertEqual(rsp.status_code, 201)

    # ----------------Unhappy case---------------
    def test_add_duplicate_track(self):   
        """Tests attempting to add a duplicate track."""

        Catalogue.catalogue.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{CATALOGUE}/{track["name"]}', headers=hdrs, json=js)
            
                rsp = requests.put(f'{CATALOGUE}/{track["name"]}', headers=hdrs, json=js)
                self.assertEqual(rsp.status_code, 403)

    def test_add_invalid_format(self):
        """Tests adding a track with an invalid file format."""

        Catalogue.catalogue.clear()

        with open(tracks[0]["track_filename"], "rb") as file:
            encoded_track = base64.b64encode(file.read()).decode("utf-8")
            js = {"name": tracks[0]["name"], "file": encoded_track}

            rsp = requests.put(f'{CATALOGUE}/empty', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 400)

    def test_add_missing_data(self):
        """Tests adding a track with no data provided."""

        Catalogue.catalogue.clear()

        js = {"name": tracks[0]["name"], "file": None}
        rsp = requests.put(f'{CATALOGUE}/{tracks[0]["name"]}', headers=hdrs, json=js)
        
        self.assertEqual(rsp.status_code, 400)

class TestUserStoryTwo(unittest.TestCase):
    
    # ----------------Happy case---------------
    def test_delete_track(self):
        """Tests deleting a track."""
    
        Catalogue.catalogue.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{CATALOGUE}/{track["name"]}', headers=hdrs, json=js)

                delete_response = requests.delete(f'{CATALOGUE}/{track["name"]}')
                self.assertEqual(delete_response.status_code, 204)
                
    # ----------------Unhappy case---------------
    def test_delete_non_existent_track(self):
        """Tests deleting a track that doesnt exist."""
    
        Catalogue.catalogue.clear()

        delete_response = requests.delete(f'{CATALOGUE}/whistle')
        self.assertEqual(delete_response.status_code, 404)


    def test_delete_track_bad_format(self):
        """Tests deleting a track that doesnt exist."""
    
        Catalogue.catalogue.clear()

        delete_response = requests.delete(f'{CATALOGUE}/')
        self.assertEqual(delete_response.status_code, 404)

class TestUserStoryThree(unittest.TestCase):

    # ----------------Happy case---------------
    def test_list_tracks(self):
        """Tests listing all tracks."""

        Catalogue.catalogue.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{CATALOGUE}/{track["name"]}', headers=hdrs, json=js)

        response = requests.get(f'{CATALOGUE}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(x['name'] in response.text for x in tracks)
    
    # ----------------Unhappy case---------------
    def test_list_empty(self):
        """Tests retrieving an set of tracks"""

        Catalogue.catalogue.clear()

        response = requests.get(f'{CATALOGUE}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

class TestUserStoryFour(unittest.TestCase):

    # ----------------Happy case---------------
    def test_solve_fragment(self):
        """Tests locating a song in the catalogue based on a fragment."""

        Catalogue.catalogue.clear()

        for item in tracks:
            with open(item["track_filename"], "rb") as track_file:
                encoded_track = base64.b64encode(track_file.read()).decode("utf-8")
                js = {"name": item["name"], "file": encoded_track}
                requests.put(f'{CATALOGUE}/{item["name"]}', headers=hdrs, json=js)

            with open(item["fragment_filename"], "rb") as fragment_file:
                encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
                fragment_js = {"file": encoded_fragment}
                response = requests.post(f'{AUDIO_RECOGNITION}', headers=hdrs, json=fragment_js)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))
    
    #----------------Unhappy case---------------
    def test_solve_unknown_fragment(self):
        """Tests locating a song that is not in the catalogue based on a fragment."""

        Catalogue.catalogue.clear()

        with open(tracks[0]["fragment_filename"], "rb") as fragment_file:
            encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
            fragment_js = {"file": encoded_fragment}
            response = requests.post(f'{AUDIO_RECOGNITION}', headers=hdrs, json=fragment_js)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json().get('message'),"Track not found in catalogue")        

    def test_solve_non_music_fragment(self):
        """Tests locating a fragment that is not a song."""

        Catalogue.catalogue.clear() # Clear the database

        with open("_Davos.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            js = {"name":None,"file": encoded_fragment}
            response = requests.post(f'{AUDIO_RECOGNITION}', headers=hdrs, json=js)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json().get('message'),"API found no result")        

    def test_solve_no_fragment(self):
        """Tests locating a song without passing in a fragment."""

        Catalogue.catalogue.clear() # Clear the database

        js = {"name":None,"file": None}
        rsp = requests.post(f'{AUDIO_RECOGNITION}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 400)

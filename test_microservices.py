import base64
import requests
import unittest
import catalogue

SHAMZAM = "http://localhost:3001/shamzam"
AUDIO_RECOGNITION = "http://localhost:3002/audio_recognition"
hdrs = {"Content-Type":"application/json"}


# List of tracks and their corresponding fragments
tracks = [
            {
                "track_filename": "Everybody (Backstreets Back) (Radio Edit).wav",
                "fragment_filename": "_Everybody (Backstreets Back) (Radio Edit).wav",
            },
            {
                "track_filename": "Blinding Lights.wav",
                "fragment_filename": "_Blinding Lights.wav",
            },
            # {
            #     "track_filename": "Dont Look Back In Anger.wav",
            #     "fragment_filename": "_Dont Look Back In Anger.wav",
            # },
            # {
            #     "track_filename": "good 4 u.wav",
            #     "fragment_filename": "_good 4 u.wav",
            # }
        ]

class TestUserStoryOne(unittest.TestCase):

    # ----------------Happy case---------------
    def test_add_track(self):
        """Tests adding a new track to the catalogue."""

        catalogue.catalogue_db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"file": encoded_track}
                response = requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)
                self.assertEqual(response.status_code, 201)

    #----------------Unhappy case---------------
    def test_add_duplicate_track(self):   
        """Tests attempting to add a duplicate track."""

        catalogue.catalogue_db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"file": encoded_track}
                requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)
            
                rsp = requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)
                self.assertEqual(rsp.status_code, 403)

    def test_add_missing_data(self):
        """Tests adding a track with no data provided."""

        catalogue.catalogue_db.clear()

        js = {"file": None}
        rsp = requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)
        
        self.assertEqual(rsp.status_code, 400)

class TestUserStoryTwo(unittest.TestCase):
    
    # ----------------Happy case---------------
    def test_delete_track(self):
        """Tests deleting a track."""
    
        catalogue.catalogue_db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"file": encoded_track}
                requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)

                list_response = requests.get(f'{SHAMZAM}')

                delete_response = requests.delete(f'{SHAMZAM}/{list_response.json()[0]}')
                self.assertEqual(delete_response.status_code, 204)
                
    # ----------------Unhappy case---------------
    def test_delete_non_existent_track(self):
        """Tests deleting a track that doesnt exist."""
    
        catalogue.catalogue_db.clear()

        delete_response = requests.delete(f'{SHAMZAM}/whistle')
        self.assertEqual(delete_response.status_code, 404)


    def test_delete_track_bad_format(self):
        """Tests deleting a track that doesnt exist."""
    
        catalogue.catalogue_db.clear()

        delete_response = requests.delete(f'{SHAMZAM}/')
        self.assertEqual(delete_response.status_code, 404)

class TestUserStoryThree(unittest.TestCase):

    # ----------------Happy case---------------
    def test_list_tracks(self):
        """Tests listing all tracks."""

        catalogue.catalogue_db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"file": encoded_track}
                requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)

        response = requests.get(f'{SHAMZAM}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(x['name'] in response.text for x in tracks)

    # ----------------Unhappy case---------------
    def test_list_empty(self):
        """Tests retrieving an set of tracks"""

        catalogue.catalogue_db.clear()

        response = requests.get(f'{SHAMZAM}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

class TestUserStoryFour(unittest.TestCase):

    # ----------------Happy case---------------
    def test_solve_fragment(self):
        """Tests locating a song in the catalogue based on a fragment."""

        catalogue.catalogue_db.clear()

        for item in tracks:
            with open(item["track_filename"], "rb") as track_file:
                encoded_track = base64.b64encode(track_file.read()).decode("utf-8")
                js = {"file": encoded_track}
                requests.put(f'{SHAMZAM}/add_track', headers=hdrs, json=js)

            with open(item["fragment_filename"], "rb") as fragment_file:
                encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
                fragment_js = {"file": encoded_fragment}
                response = requests.post(f'{SHAMZAM}/recognise_fragment', headers=hdrs, json=fragment_js)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))
    
    #----------------Unhappy case---------------
    def test_solve_unknown_fragment(self):
        """Tests locating a song that is not in the catalogue based on a fragment."""

        catalogue.catalogue_db.clear()
    
        with open(tracks[0]["fragment_filename"], "rb") as fragment_file:
            encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
            fragment_js = {"file": encoded_fragment}
            response = requests.post(f'{SHAMZAM}/recognise_fragment', headers=hdrs, json=fragment_js)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json().get('message'),"Track not found in catalogue")        

    def test_solve_non_music_fragment(self):
        """Tests locating a fragment that is not a song."""

        catalogue.catalogue_db.clear()

        with open("_Davos.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            js = {"name":None,"file": encoded_fragment}
            response = requests.post(f'{SHAMZAM}/recognise_fragment', headers=hdrs, json=js)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json().get('message'),"API found no result")        

    def test_solve_no_fragment(self):
        """Tests locating a song without passing in a fragment."""

        catalogue.catalogue_db.clear() # Clear the database

        js = {"file": None}
        rsp = requests.post(f'{SHAMZAM}/recognise_fragment', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 400)

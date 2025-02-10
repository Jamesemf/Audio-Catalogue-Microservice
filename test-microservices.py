import base64
import requests
import unittest
import database

catalogue_user = "http://localhost:3002/catalogue"
catalogue_admin = "http://localhost:3000/catalogue"
audd_service = "http://localhost:3001/audd"
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

class Testing(unittest.TestCase):

    def test_01_add_track(self):
        """Tests adding a new track to the catalogue."""

        database.db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                rsp = requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)
                self.assertEqual(rsp.status_code, 201)

    def test_02_add_existing_track(self):
        """Tests attempting to add a duplicate track."""

        database.db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)
            
                rsp = requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)
                self.assertEqual(rsp.status_code, 403)

    def test_03_add_poor_format(self):
        """Tests adding a track with an invalid file format."""

        database.db.clear()

        with open(tracks[0]["track_filename"], "rb") as file:
            encoded_track = base64.b64encode(file.read()).decode("utf-8")
            js = {"name": tracks[0]["name"], "file": encoded_track}

            rsp = requests.put(f'{catalogue_admin}/empty', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 400)

    def test_04_add_nothing(self):
        """Tests adding a track with no data provided."""

        database.db.clear()

        js = {}
        rsp = requests.put(f'{catalogue_admin}/empty_track', headers=hdrs, json=js)
        
        self.assertEqual(rsp.status_code, 400)


    def test_05_list_tracks(self):
        """Tests listing all tracks."""

        database.db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)

        response = requests.get(f'{catalogue_admin}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(x['name'] in response.text for x in tracks)

    def test_06_list_empty(self):
        """Tests retrieving an set of tracks"""

        database.db.clear()

        response = requests.get(f'{catalogue_admin}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text == '[]')


    def test_07_retrieve_track(self):
        """Tests retrieving an existing track by name."""
        
        database.db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)

                response = requests.get(f'{catalogue_user}/{track["name"]}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))

    def test_08_retrieve_no_track(self):
        """Tests retrieving a non-existent track."""

        database.db.clear()

        rsp = requests.get(f'{catalogue_user}/blank')
        self.assertEqual(rsp.status_code, 404)        
    
    def test_09_remove_track(self):
        """Tests deleting a track."""
    
        database.db.clear()

        for track in tracks:
            with open(track["track_filename"], "rb") as file:
                encoded_track = base64.b64encode(file.read()).decode("utf-8")
                js = {"name": track["name"], "file": encoded_track}
                requests.put(f'{catalogue_admin}/{track["name"]}', headers=hdrs, json=js)

                delete_response = requests.delete(f'{catalogue_admin}/{track["name"]}')
                self.assertEqual(delete_response.status_code, 204)
    
    def test_10_remove_no_track(self):
        """Tests deleting a track that doesnt exist."""
    
        database.db.clear()

        with open(tracks[0]["track_filename"], "rb") as file:
            encoded_track = base64.b64encode(file.read()).decode("utf-8")
            js = {"name": tracks[0]["name"], "file": encoded_track}
            requests.put(f'{catalogue_admin}/{tracks[0]["name"]}', headers=hdrs, json=js)

            delete_response = requests.delete(f'{catalogue_admin}/random')
            self.assertEqual(delete_response.status_code, 404)

    def test_11_solve_fragment(self):
        """Tests locating a song in the catalogue based on a fragment."""

        database.db.clear()

        for item in tracks:
            with open(item["track_filename"], "rb") as track_file:
                encoded_track = base64.b64encode(track_file.read()).decode("utf-8")
                js = {"name": item["name"], "file": encoded_track}
                requests.put(f'{catalogue_admin}/{item["name"]}', headers=hdrs, json=js)

            with open(item["fragment_filename"], "rb") as fragment_file:
                encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
                fragment_js = {"file": encoded_fragment}
                response = requests.post(f'{audd_service}', headers=hdrs, json=fragment_js)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(encoded_track, response.json().get('file'))
            
    def test_12_solve_unknown_fragment(self):
        """Tests locating a song that is not in the catalogue based on a fragment."""

        database.db.clear()

        with open(tracks[0]["fragment_filename"], "rb") as fragment_file:
            encoded_fragment = base64.b64encode(fragment_file.read()).decode("utf-8")
            fragment_js = {"file": encoded_fragment}
            response = requests.post(f'{audd_service}', headers=hdrs, json=fragment_js)

            self.assertEqual(response.status_code, 404)           

    def test_13_solve_non_music_fragment(self):
        """Tests locating a fragment that is not a song."""

        database.db.clear() # Clear the database

        with open("_Davos.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            js = {"name":None,"file": encoded_fragment}
            rsp = requests.post(f'{audd_service}', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 500)

    def test_14_solve_no_fragment(self):
        """Tests locating a song without passing in a fragment."""

        database.db.clear() # Clear the database

        with open("_Davos.wav", "rb") as fragment:
            encoded_fragment = None
            js = {"name":None,"file": encoded_fragment}
            rsp = requests.post(f'{audd_service}', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 400)



            


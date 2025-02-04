import base64
import requests
import unittest

catalogue = "http://localhost:3000/catalogue"

class Testing(unittest.TestCase):

    # Run on a fresh catalogue for correct testing

    def test_01_add_track(self):
        """Tests adding a new track to the catalogue."""

        with open("Long/Blinding Lights.wav", "rb") as track:
            name = "Blinding Lights"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 201)
        
        with open("Long/Dont Look Back In Anger.wav", "rb") as track:
            name = "Dont Look Back In Anger"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 201)

        with open("Long/Everybody (Backstreets Back) (Radio Edit).wav", "rb") as track:
            name = "Everybody"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 201)

        with open("Long/good 4 u.wav", "rb") as track:
            name = "good 4 u"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 201)

    # Unhappy path
    def test_02_add_existing_track(self):
        """Tests attempting to add a duplicate track."""

        with open("Long/good 4 u.wav", "rb") as track:
            name = "good 4 u"
            encoded_track = base64.b64encode(track.read()).decode("utf-8")
            hdrs = {"Content-type":"application/json"}
            js = {"name":name,"file":encoded_track}
            rsp = requests.put(f'{catalogue}/{name}', headers=hdrs, json=js)
        self.assertEqual(rsp.status_code, 403)
        
    def test_03_list_tracks(self):
        """Tests listing all tracks."""

        rsp = requests.get(f'{catalogue}')
        self.assertEqual(rsp.status_code, 200)
        self.assertTrue("Blinding Lights" in rsp.text)

    def test_04_get_track(self):
        """Tests retrieving an existing track by name."""

        name = 'Blinding Lights'
        rsp = requests.get(f'{catalogue}/{name}')
        self.assertEqual(rsp.status_code,200)

    #Unhappy path
    def test_05_get_non_existent_track(self):
        """Tests retrieving a non-existent track."""

        name = "Scooby-doo"
        rsp = requests.get(f'{catalogue}/{name}')
        self.assertEqual(rsp.status_code, 404)        
    
    def test_06_delete_track(self):
        """Tests deleting a track."""

        name = "Blinding Lights"
        rsp = requests.delete(f'{catalogue}/{name}')
        self.assertEqual(rsp.status_code, 204)

    def test_07_convert_fragment(self):
        """Tests locating a song in the catalogue based on a fragment."""

        with open("Short/_good 4 u.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            hdrs = {"Content-Type":"application/json"}
            js = {"file": encoded_fragment}
            rsp = requests.post(f'{catalogue}/convert', headers=hdrs, json=js)
            
            self.assertEqual(rsp.status_code, 200)
            self.assertTrue('good 4 u' in rsp.json()['name'])

    # Unhappy Path
    def test_08_non_music_fragment(self):
         """Tests locating a song that is not in the catalogue based on a fragment."""

         with open("Short/_Davos.wav", "rb") as fragment:
            encoded_fragment = base64.b64encode(fragment.read()).decode("utf-8")
            hdrs = {"Content-Type":"application/json"}
            js = {"name":None,"file": encoded_fragment}
            rsp = requests.post(f'{catalogue}/convert', headers=hdrs, json=js)
            self.assertEqual(rsp.status_code, 500)



            


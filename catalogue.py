import sqlite3

class Track:
    """
    Represents a track in the catalogue.
    
    Attributes:
        name (str): The name of the track.
        file (bytes): The audio file in binary format.
    """
    def __init__(self,name,file):
        self.name = name
        self.file = file

class Catalogue:
  def __init__(self,name):
    self.database = name + ".db" 
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "CREATE TABLE IF NOT EXISTS tracks " +
        "(name TEXT PRIMARY KEY, file BLOB)"
      )
      connection.commit()

  def add_track(self, name, file):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      try:
        cursor.execute(
          "INSERT INTO tracks (name,file) VALUES (?,?)",
          (name, file)
        )
        connection.commit()
        return True
      except sqlite3.IntegrityError:
        return False

  def retrieve_track(self, name):
    with sqlite3.connect(self.database) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name, file FROM tracks WHERE name LIKE ?",
            (f"%{name}%",)
        )
        row = cursor.fetchone()
        return {'name': row[0], 'file': row[1]} if row else None

  def delete_track(self,name):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "DELETE FROM tracks WHERE name=?",
        (name,)
      )
      connection.commit()
      return cursor.rowcount > 0        
    
  def clear(self):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        f" DELETE FROM tracks"
    )
    connection.commit()
  
  def list_tracks(self):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute("SELECT * FROM tracks")
      tracks = cursor.fetchall()
      return [row[0] for row in tracks] if tracks else []


catalogue_db = Catalogue("Shamzam")
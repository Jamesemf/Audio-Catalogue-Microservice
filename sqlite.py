import model
import sqlite3

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
  
  
  def update(self, track):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "UPDATE tracks SET file=? WHERE name=?",
        (track.file,track.name)
      )
      connection.commit()
      return cursor.rowcount


  def insert(self, track):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "INSERT INTO tracks (name,file) VALUES (?,?)",
        (track.name,track.file)
      )
      connection.commit()
      return cursor.rowcount

  def lookup(self,name):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "SELECT name, file FROM tracks WHERE name=?",
        (name,)
      )
      row = cursor.fetchone()
      if row: return model.Track(row[0],row[1])
      else: return None


  def delete(self,name):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute(
        "DELETE FROM tracks WHERE name=?",
        (name,)
      )
      connection.commit()
      return cursor.rowcount > 0        


  def list(self):
    with sqlite3.connect(self.database) as connection:
      cursor = connection.cursor()
      cursor.execute("SELECT * FROM tracks")
      return [row[0] for row in cursor.fetchall()]
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
    
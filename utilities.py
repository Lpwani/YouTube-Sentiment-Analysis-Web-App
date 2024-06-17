import os

class CleanCache:
    '''
    this class is responsible to clear any residual csv and image files
    present due to the past searches made.
    '''
    def __init__(self, directory=None):
        self.clean_path = directory
        if os.listdir(self.clean_path) != list():
            files = os.listdir(self.clean_path)
            for fileName in files:
                os.remove(os.path.join(self.clean_path, fileName))
        print("cleaned!")

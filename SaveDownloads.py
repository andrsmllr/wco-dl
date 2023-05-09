try:
    import cPickle as pickle
except ImportError:
    import pickle
from Settings import Settings
import os

class SaveDownloadToFile: 
    def __init__(self, settings: Settings):
        self.shows = {}
        self.database_path = settings.get_setting('downloadsDatabaseLocation')
        self.total_number_of_shows_downloaded = 0

        if (os.path.exists(self.database_path)):
            with open(self.database_path, 'rb') as file: 
                self.shows = pickle.load(file)
                self.total_number_of_shows_downloaded = len(self.shows)
                print('Database loaded.', end='\n\n')
            
    def add_show_to_database(self, show_url): 
        isIn = False
        self.total_number_of_shows_downloaded = len(self.shows)
        for x in self.iterate_urls():
            if show_url == x:
                isIn = True
        if isIn:
            pass
        else:
            self.shows['anime{0}'.format(str(self.total_number_of_shows_downloaded+1))] = show_url
            self.save_to_file()
        
    def save_to_file(self):
        with open(self.database_path, 'wb') as file:
            pickle.dump(self.shows, file, protocol=pickle.HIGHEST_PROTOCOL)
            
    def print_shows(self):
        for x in range(self.total_number_of_shows_downloaded):
            if ('/anime/' in str(self.shows['anime{0}'.format(str(x+1))])):
                print('Show url: {0}'.format(str(self.shows['anime{0}'.format(str(x+1))])),
                      'Show name: {0}'.format(str(self.shows['anime{0}'.format(str(x+1))]).rsplit('/', 1)[-1].replace('-', ' ').title()))
            else:
                print('Episode url: {0}'.format(str(self.shows['anime{0}'.format(str(x+1))])),
                      'Episode name: {0}'.format(str(self.shows['anime{0}'.format(str(x+1))]).rsplit('/', 1)[-1].replace('-', ' ').title()))
    
    def iterate_urls(self):
        for x in range(self.total_number_of_shows_downloaded):
            if ("/anime/" in str(self.shows['anime{0}'.format(str(x+1))])):
                yield str(self.shows['anime{0}'.format(str(x+1))])

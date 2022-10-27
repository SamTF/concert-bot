### IMPORTS
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from typing import List
import re
import itertools

### CLASS
class Concert:
    id = None
    date = None
    band = None
    time = None
    venue = None
    region = None

    id_counter = itertools.count()

    def __init__(self, date:str, concert:str) -> None:
        self.date = self._date_from_string(date)
        self.band, self.time, self.venue, self.region = self._parse_concert_title(concert)
        self.id = next(self.id_counter)

    def __repr__(self) -> str:
        date_str = datetime.strftime(self.date, '%d/%m/%y')
        s = f'{date_str}\n'
        for b in self.band:
            s += f'- {b})\n'
        s += f'{self.time} @ {self.venue}\n'
        s += f'{self.region}'

        return s
    
    def _date_from_string(self, string) -> datetime.date:
        date_string = string[-10:]  # extracting only the date as dd.mm.yyyy
        date = datetime.strptime(date_string, '%d.%m.%Y')
        return date

    def _parse_concert_title(self, concert_title:str):
        # HEMELBESTORMER (Post-Rock, Sludge, Black Metal aus Belgien),
        # NOORVIK (Rock, Metal)
        # ab 21 Uhr im Sonic Ballroom (Oskar-Jäger-Str. 190)
        # / Köln-Ehrenfeld

        # 1. split string by commas and abs
        split_str = re.split('ab\s', concert_title)

        # 2. getting the bands
        band = split_str[0] if not '),' in split_str[0] else split_str[0].split('),')
        band = [b.strip() for b in band]

        # 3. getting the time, venue, region
        venue_data = re.split('\sim\s|in der|auf dem|/', split_str[-1])
        venue_data = [x.strip() for x in venue_data]
        time, venue, region, *rest = venue_data

        # 3.1 fixing the stupid umlauts
        venue = venue.replace('Ã¶', 'ö')
        region = region.replace('Ã¶', 'ö')
        region = region.replace('Ã¼', 'ü')

        # 3.2 removing address in brackets
        venue = re.sub("[\(\[].*?[\)\]]", "", venue)

        # returning the data
        return band, time, venue, region
    
    @property
    def shorthand(self) -> str:
        '''
        Succinct version of the concert info displaying only date and headliner.
        '''
        date_str = datetime.strftime(self.date, '%d/%m/%y')

        s = f'[{self.id}] **{date_str}** - {self.band[0]})'

        if len(self.band) > 1:
            other_bands = len(self.band) - 1
            s += f' [+{other_bands}]'
        
        return s
        
    


### SCRAPING WEB DATA
def fetch_concerts() -> List[Concert]:
    # getting the website source code
    source = requests.get('http://www.punkstelle.de/').text

    # creating html parser object
    soup = BeautifulSoup(source, 'lxml')

    events = soup.find('div', { 'id' : 'calendar'})
    all_events = events.find_all('div', class_='event')
    filtered_events = []

    # finding all event elements without "full" or "month" CSS classes
    for event in all_events:
        if event.find(class_='month') or event.find(class_='full'):
            continue
        filtered_events.append(event)


    # parsing the data into Concert objects
    concerts = []
    for concert in filtered_events:
        date = concert.find('div', class_='date').text
        concert_title = concert.find('div', class_='concert-title').text

        x = Concert(date, concert_title)
        concerts.append(x)
    
    # filtering out past concerts
    concerts = [c for c in concerts if c.date > datetime.today()]
    
    return concerts


# When running the script directly
if __name__ == "__main__":
    concerts = fetch_concerts()
    print(concerts[0].shorthand)
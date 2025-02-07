import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscogsCollectionScraper:
    def __init__(self, base_url, save_dir='static/images'):
        self.base_url = base_url
        self.save_dir = save_dir
        self.albums = []
        os.makedirs(save_dir, exist_ok=True)
        
    def get_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def parse_album(self, item):
        try:
            img_elem = item.find('img', class_='thumbnail_center')
            if not img_elem:
                return None
                
            img_url = img_elem.get('src')
            if not img_url:
                return None
                
            # Get high-quality image URL
            img_url = img_url.replace('_small', '_600')
            
            # Extract title and artist
            title_elem = item.find('a', class_='release')
            artist_elem = item.find('a', class_='artist')
            
            if not title_elem or not artist_elem:
                return None
                
            return {
                'img_url': img_url,
                'title': title_elem.text.strip(),
                'artist': artist_elem.text.strip()
            }
        except Exception as e:
            logger.error(f"Error parsing album: {str(e)}")
            return None

    def download_image(self, img_url, filename):
        try:
            response = requests.get(img_url)
            response.raise_for_status()
            
            file_path = os.path.join(self.save_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return filename
        except Exception as e:
            logger.error(f"Error downloading image {img_url}: {str(e)}")
            return None

    def scrape_collection(self):
        page = 1
        while True:
            url = f"{self.base_url}?page={page}"
            logger.info(f"Scraping page {page}")
            
            try:
                html = self.get_page(url)
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.find_all('tr', class_='collection-row')
                
                if not items:
                    break
                    
                for item in items:
                    album_data = self.parse_album(item)
                    if album_data:
                        # Generate filename from artist and title
                        filename = f"{album_data['artist']}_{album_data['title']}.jpg"
                        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"{len(self.albums):03d}_{filename[:50]}.jpg"
                        
                        # Download image
                        if self.download_image(album_data['img_url'], filename):
                            album_data['filename'] = filename
                            self.albums.append(album_data)
                            logger.info(f"Added album: {album_data['artist']} - {album_data['title']}")
                
                time.sleep(1)  # Be nice to Discogs servers
                page += 1
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                break
        
        # Save album metadata
        with open(os.path.join(self.save_dir, 'albums.json'), 'w') as f:
            json.dump(self.albums, f, indent=2)
        
        return self.albums

if __name__ == '__main__':
    collection_url = "https://www.discogs.com/user/ingridvp/collection"
    scraper = DiscogsCollectionScraper(collection_url)
    albums = scraper.scrape_collection()
    logger.info(f"Successfully scraped {len(albums)} albums")

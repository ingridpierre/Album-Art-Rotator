import os
import requests
import logging
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscogsCollectionScraper:
    def __init__(self, username, token, save_dir='static/images'):
        self.username = username
        self.token = token
        self.save_dir = save_dir
        self.albums = []
        self.base_url = f'https://api.discogs.com/users/{username}/collection/folders/0/releases'
        os.makedirs(self.save_dir, exist_ok=True)

    def cleanup_old_files(self):
        """Remove old image files that are no longer referenced."""
        current_files = set(os.listdir(self.save_dir))
        current_files.discard('albums.json')

        json_path = os.path.join(self.save_dir, 'albums.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    old_data = json.load(f)
                    keep_files = {album['filename'] for album in old_data}
                    for file in current_files:
                        if file not in keep_files and file != 'albums.json':
                            try:
                                os.remove(os.path.join(self.save_dir, file))
                                logger.info(f"Removed old file: {file}")
                            except OSError as e:
                                logger.error(f"Error removing file {file}: {e}")
            except Exception as e:
                logger.error(f"Error cleaning up old files: {e}")

    def get_collection_page(self, page=1):
        headers = {
            'Authorization': f'Discogs token={self.token}',
            'User-Agent': 'AlbumArtDisplayApp/1.0'
        }
        params = {
            'page': page,
            'per_page': 100
        }
        logger.info(f"Requesting page {page} from Discogs API")
        response = requests.get(self.base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received {len(data.get('releases', []))} releases from page {page}")
        return data

    def download_image(self, img_url, filename):
        try:
            headers = {
                'User-Agent': 'AlbumArtDisplayApp/1.0'
            }
            logger.info(f"Downloading image from {img_url}")
            response = requests.get(img_url, headers=headers)
            response.raise_for_status()

            file_path = os.path.join(self.save_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Successfully saved new image to {filename}")
            else:
                logger.info(f"Image {filename} already exists, skipping download")
            return filename
        except Exception as e:
            logger.error(f"Error downloading image {img_url}: {str(e)}")
            return None

    def generate_filename(self, artist, title):
        clean_name = "".join(c for c in f"{artist}_{title}" if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{clean_name[:100]}.jpg"

    def scrape_collection(self):
        self.cleanup_old_files()
        page = 1
        total_pages = 1
        self.albums = []

        while page <= total_pages:
            logger.info(f"Processing page {page} of {total_pages}")
            try:
                data = self.get_collection_page(page)
                pagination = data.get('pagination', {})
                total_pages = pagination.get('pages', 1)

                releases = data.get('releases', [])
                if not releases:
                    logger.warning(f"No releases found on page {page}")
                    break

                for release in releases:
                    basic_information = release.get('basic_information', {})
                    if not basic_information:
                        continue

                    cover_image = basic_information.get('cover_image')
                    if not cover_image:
                        logger.warning(f"No cover image found for release {basic_information.get('title', 'Unknown')}")
                        continue

                    artists = basic_information.get('artists', [{}])
                    artist = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'
                    title = basic_information.get('title', 'Unknown Title')

                    logger.info(f"Processing album: {artist} - {title}")

                    filename = self.generate_filename(artist, title)
                    if self.download_image(cover_image, filename):
                        self.albums.append({
                            'filename': filename,
                            'title': title,
                            'artist': artist
                        })
                        logger.info(f"Successfully added album: {artist} - {title}")

                time.sleep(1)
                page += 1

            except Exception as e:
                logger.error(f"Error processing page {page}: {str(e)}")
                break

        if self.albums:
            metadata_path = os.path.join(self.save_dir, 'albums.json')
            with open(metadata_path, 'w') as f:
                json.dump(self.albums, f, indent=2)
            logger.info(f"Saved metadata for {len(self.albums)} albums to {metadata_path}")
        else:
            logger.warning("No albums were processed successfully")

        return self.albums

if __name__ == '__main__':
    token = os.environ.get('DISCOGS_TOKEN')
    if not token:
        logger.error("No Discogs token found in environment variables")
        exit(1)

    username = os.environ.get('DISCOGS_USERNAME', 'ingridvp')
    scraper = DiscogsCollectionScraper(username, token)
    albums = scraper.scrape_collection()
    logger.info(f"Successfully scraped {len(albums)} albums")
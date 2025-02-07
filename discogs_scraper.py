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
        os.makedirs(save_dir, exist_ok=True)

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
            with open(file_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Successfully saved image to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error downloading image {img_url}: {str(e)}")
            return None

    def scrape_collection(self):
        page = 1
        total_pages = 1  # Will be updated from API response

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

                    # Get the cover image URL directly
                    cover_image = basic_information.get('cover_image')
                    if not cover_image:
                        logger.warning(f"No cover image found for release {basic_information.get('title', 'Unknown')}")
                        continue

                    # Generate filename from artist and title
                    artists = basic_information.get('artists', [{}])
                    artist = artists[0].get('name', 'Unknown Artist') if artists else 'Unknown Artist'
                    title = basic_information.get('title', 'Unknown Title')

                    logger.info(f"Processing album: {artist} - {title}")

                    filename = f"{artist}_{title}.jpg"
                    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{len(self.albums):03d}_{filename[:50]}.jpg"

                    # Download image
                    if self.download_image(cover_image, filename):
                        album_data = {
                            'filename': filename,
                            'title': title,
                            'artist': artist
                        }
                        self.albums.append(album_data)
                        logger.info(f"Successfully added album: {artist} - {title}")

                time.sleep(1)  # Be nice to Discogs servers
                page += 1

            except Exception as e:
                logger.error(f"Error processing page {page}: {str(e)}")
                break

        # Save album metadata
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

    username = "ingridvp"
    scraper = DiscogsCollectionScraper(username, token)
    albums = scraper.scrape_collection()
    logger.info(f"Successfully scraped {len(albums)} albums")
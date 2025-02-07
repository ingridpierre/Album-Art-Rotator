import os
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_discogs_api():
    token = os.environ.get('DISCOGS_TOKEN')
    if not token:
        logger.error("No Discogs token found")
        return
        
    username = "ingridvp"
    url = f'https://api.discogs.com/users/{username}/collection/folders/0/releases'
    
    headers = {
        'Authorization': f'Discogs token={token}',
        'User-Agent': 'AlbumArtDisplayApp/1.0'
    }
    
    params = {
        'page': 1,
        'per_page': 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Pretty print the first release data
        logger.info("API Response Structure:")
        print(json.dumps(data, indent=2))
        
        if 'releases' in data:
            release = data['releases'][0]
            logger.info(f"First release basic info: {json.dumps(release['basic_information'], indent=2)}")
    except Exception as e:
        logger.error(f"Error testing API: {str(e)}")

if __name__ == '__main__':
    test_discogs_api()

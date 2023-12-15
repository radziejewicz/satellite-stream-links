import os
import json
import requests
from googleapiclient.discovery import build


YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
NASA_CHANNEL_ID = 'UCLA_DiR1FfKNvjuUpBHmylQ'
JSON_FILE_NAME = 'live_streams.json' # For tests

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_live_streams():
    request = youtube.search().list(
        part='snippet',
        eventType='live',
        type='video',
        maxResults=50,
        channelId=NASA_CHANNEL_ID
    )
    response = request.execute()

    return response['items']


def update_json(file_name, new_urls):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Requires change if there are other satellites
            existing_urls = data['links']['25544']['youtube']
            urls_exist = True

            for url in new_urls:
                if url not in existing_urls:
                    print(url)
                    urls_exist = False
                    break

            if not urls_exist:
                data['links']['25544']['youtube'] = new_urls
                data['version'] = str(int(data['version']) + 1)

                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        return None


def find_live_streams(json_data) -> list:
    if json_data:
        urls = []

        target_titles = [
            "Live High-Definition Views from the International Space Station (Official NASA Stream)",
            "Live Video from the International Space Station (Official NASA Stream)"
        ]

        for item in json_data:
            if 'snippet' in item and 'title' in item['snippet']:
                title = item['snippet']['title']
                if title in target_titles:
                    video_id = item['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    urls.append(video_url)

        return urls


live_streams = get_live_streams()
streams = find_live_streams(live_streams)
update_json(JSON_FILE_NAME, streams)

import requests
import json
from datetime import datetime

def test_youtube_api():
    api_key = "AIzaSyBK4-JY-2wCX73vOv0_zJsuhRsA5e-GnVU"
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'key': api_key,
        'q': 'python programming',
        'part': 'snippet',
        'type': 'video',
        'maxResults': 5,
        'order': 'date',
        'publishedAfter': '2025-01-01T00:00:00Z'
    }

    print("Testing YouTube API...")
    response = requests.get(search_url, params=search_params)

    if response.status_code == 200:
        data = response.json()
        videos = data.get('items', [])
        if not videos:
            print("No videos found")
            return
        print("YouTube API working successfully!")
        print(f"Retrieved {len(videos)} videos")

        video_ids = [video['id']['videoId'] for video in videos]
        video_details = get_video_statistics(api_key, video_ids)

        for i, video in enumerate(videos):
            video_id = video['id']['videoId']
            snippet = video['snippet']
            stats = video_details.get(video_id, {})
            print(f"Video {i+1}:")
            print(f"Title: {snippet['title'][:80]}...")
            print(f"Channel: {snippet['channelTitle']}")
            print(f"Published: {snippet['publishedAt']}")
            if stats:
                print(f"Views: {stats.get('viewCount', 'N/A')}")
                print(f"Likes: {stats.get('likeCount', 'N/A')}")
                print(f"Comments: {stats.get('commentCount', 'N/A')}")
            print(f"URL: https://youtube.com/watch?v={video_id}")

    elif response.status_code == 403:
        print("API Key error or daily quota exceeded")
    else:
        print(f"Error: {response.status_code}")
        print(f"Message: {response.text}")

def get_video_statistics(api_key, video_ids):
    if not video_ids:
        return {}
    stats_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'key': api_key,
        'id': ','.join(video_ids),
        'part': 'statistics'
    }
    response = requests.get(stats_url, params=params)
    if response.status_code == 200:
        data = response.json()
        stats_dict = {}
        for item in data.get('items', []):
            video_id = item['id']
            stats = item.get('statistics', {})
            stats_dict[video_id] = stats
        return stats_dict
    return {}


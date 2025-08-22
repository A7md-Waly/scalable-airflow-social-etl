import requests
import json

def test_x_api():
    bearer_token = "AAAAAAAAAAAAAAAAAAAAALqS3gEAAAAAG%2BczfRrirqTNfnu%2FOFVAnZ500Hs%3DsFvWK7ry8CJ4EFjhaYWxA4cZ114TW2EcZ1e1j7QeulJROnQoIg"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "User-Agent": "SocialMediaAnalytics/1.0"
    }
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": "python -is:retweet lang:en",
        "max_results": 10,
        "tweet.fields": "created_at,author_id,public_metrics,lang"
    }

    print("Testing X API...")
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        print("X API is working successfully!")
        data = response.json()
        tweets = data.get("data", [])
        print(f"Retrieved {len(tweets)} tweets")
        if tweets:
            for i, tweet in enumerate(tweets[:2], 1):
                print(f"Tweet {i}:")
                print(f"Text: {tweet['text'][:100]}...")
                metrics = tweet['public_metrics']
                print(f"Likes: {metrics['like_count']}")
                print(f"Retweets: {metrics['retweet_count']}")
                print(f"Replies: {metrics['reply_count']}")
                print(f"Date: {tweet['created_at']}")
    elif response.status_code == 401:
        print("Authentication error - check your Bearer Token")
    elif response.status_code == 429:
        print("Rate limit exceeded - please wait a while")
    else:
        print(f"Error: {response.status_code}")
        print(f"Message: {response.text}")


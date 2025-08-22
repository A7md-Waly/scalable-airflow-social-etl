from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import logging
from typing import List, Dict

# DAG Configuration
default_args = {
    'owner': 'Ahmed Waly',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

dag = DAG(
    'social_media_analytics',
    default_args=default_args,
    description='Collect and analyze social media data',
    schedule_interval=timedelta(minutes=15),
    max_active_runs=1
)

# API Keys
X_BEARER_TOKEN = Variable.get("X_BEARER_TOKEN")
YT_API_KEY = Variable.get("YT_API_KEY")

def get_postgres_hook():
    return PostgresHook(postgres_conn_id='postgres_default')

def fetch_x_tweets(**context) -> List[Dict]:
    logging.info("Fetching tweets from X")
    
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    params = {
        "query": "-is:retweet lang:en",
        "max_results": 10,
        "tweet.fields": "created_at,author_id,public_metrics"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        tweets = response.json().get("data", [])
        results = []
        
        for t in tweets:
            metrics = t.get('public_metrics', {})
            results.append({
                "platform": "X",
                "platform_post_id": t["id"],
                "platform_author_id": t["author_id"],
                "content": t.get("text", "")[:1000],
                "likes_count": metrics.get("like_count", 0),
                "comments_count": metrics.get("reply_count", 0),
                "shares_count": metrics.get("retweet_count", 0),
                "published_at": t["created_at"]
            })
        
        logging.info(f"Collected {len(results)} tweets")
        return results
        
    except Exception as e:
        logging.error(f"Error fetching X data: {e}")
        return []

def fetch_youtube_videos(**context) -> List[Dict]:
    logging.info("Fetching YouTube videos")
    
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': YT_API_KEY,
        'q': 'latest videos',
        'part': 'snippet',
        'type': 'video',
        'maxResults': 10,
        'order': 'date'
    }

    try:
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        
        videos = response.json().get("items", [])
        video_ids = [v['id']['videoId'] for v in videos if 'videoId' in v.get('id', {})]
        
        if not video_ids:
            return []
        
        # Get statistics
        stats_url = "https://www.googleapis.com/youtube/v3/videos"
        stats_params = {
            'key': YT_API_KEY,
            'id': ','.join(video_ids),
            'part': 'statistics'
        }
        
        stats_resp = requests.get(stats_url, params=stats_params, timeout=30)
        stats_resp.raise_for_status()
        stats_data = stats_resp.json().get("items", [])
        stats_dict = {item["id"]: item.get("statistics", {}) for item in stats_data}

        results = []
        for v in videos:
            if 'videoId' not in v.get('id', {}):
                continue
                
            vid = v['id']['videoId']
            snippet = v['snippet']
            stats = stats_dict.get(vid, {})
            
            results.append({
                "platform": "YouTube",
                "platform_post_id": vid,
                "platform_author_id": snippet.get("channelId", ""),
                "author_username": snippet.get("channelTitle", ""),
                "content": snippet.get("title", "")[:1000],
                "likes_count": int(stats.get("likeCount", 0)),
                "comments_count": int(stats.get("commentCount", 0)),
                "shares_count": 0,
                "published_at": snippet.get("publishedAt", "")
            })
        
        logging.info(f"Collected {len(results)} videos")
        return results
        
    except Exception as e:
        logging.error(f"Error fetching YouTube data: {e}")
        return []

def store_data(**context):
    logging.info("Storing data to PostgreSQL")
    
    ti = context['ti']
    x_data = ti.xcom_pull(task_ids='fetch_x_data') or []
    yt_data = ti.xcom_pull(task_ids='fetch_youtube_data') or []
    
    all_data = x_data + yt_data
    
    if not all_data:
        logging.warning("No data to store")
        return
    
    postgres_hook = get_postgres_hook()
    new_posts = 0
    
    for post in all_data:
        try:
            insert_query = """
                INSERT INTO social_media_schema.social_posts (
                    platform, platform_post_id, platform_author_id, 
                    author_username, content, likes_count, comments_count, 
                    shares_count, published_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (platform, platform_post_id) DO NOTHING
            """
            
            postgres_hook.run(insert_query, parameters=(
                post['platform'], post['platform_post_id'], post['platform_author_id'],
                post.get('author_username', ''), post['content'], post['likes_count'], 
                post['comments_count'], post['shares_count'], post['published_at']
            ))
            
            new_posts += 1
            
        except Exception as e:
            logging.error(f"Error inserting post: {e}")
            continue
    
    logging.info(f"Processing complete. Attempted to store {new_posts} posts")

# Define tasks
fetch_x_task = PythonOperator(
    task_id='fetch_x_data',
    python_callable=fetch_x_tweets,
    dag=dag
)

fetch_youtube_task = PythonOperator(
    task_id='fetch_youtube_data',
    python_callable=fetch_youtube_videos,
    dag=dag
)

store_data_task = PythonOperator(
    task_id='store_data',
    python_callable=store_data,
    dag=dag
)

# Task dependencies
[fetch_x_task, fetch_youtube_task] >> store_data_task
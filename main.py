import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import requests
from bs4 import BeautifulSoup
import time

def authenticate_youtube(client_secrets_file):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    scopes = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.readonly"]

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    return youtube

def get_video_urls_from_playlist(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    video_urls = []
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_urls.append(video_url)

    return video_urls

def scrape_video_metadata(video_url):
    response = requests.get(video_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('meta', {'name': 'title'})['content']
    description = soup.find('meta', {'name': 'description'})['content']
    keywords = soup.find('meta', {'name': 'keywords'})['content']
    tags = keywords.split(',')

    return title, description, tags

def download_video(video_url, output_path, retries=5, delay=10):
    for attempt in range(retries):
        try:
            yt = YouTube(video_url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=os.path.dirname(output_path), filename=os.path.basename(output_path))
            print(f"Downloaded video: {video_url} to {output_path}")
            return
        except (VideoUnavailable, TimeoutError) as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to download video: {video_url} after {retries} attempts.")
                raise

def upload_video(youtube, file_path, title, description, category_id, tags):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=file_path
    )
    response = request.execute()
    return response

def upload_subtitle(youtube, video_id, subtitle_file, language, name):
    body = {
        'snippet': {
            'videoId': video_id,
            'language': language,
            'name': name,
            'isDraft': False
        }
    }
    insert_request = youtube.captions().insert(
        part="snippet",
        body=body,
        media_body=subtitle_file
    )
    response = insert_request.execute()
    return response

def get_caption_tracks(youtube, video_id):
    request = youtube.captions().list(
        part="snippet",
        videoId=video_id
    )
    response = request.execute()
    return response['items']

def download_srt(youtube, caption_id, output_file):
    request = youtube.captions().download(
        id=caption_id,
        tfmt="srt"
    )
    with open(output_file, 'wb') as file:
        download = request.execute()
        file.write(download)

def read_uploaded_videos(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return set(file.read().splitlines())
    return set()

def write_uploaded_video(file_path, video_id):
    with open(file_path, 'a') as file:
        file.write(f"{video_id}\n")

def main():
    # Authenticate YouTube API for the original channel to download videos
    original_channel_client_secrets_file = "credentials.json"
    original_youtube = authenticate_youtube(original_channel_client_secrets_file)

    # Authenticate YouTube API for the target channel to upload videos
    target_channel_client_secrets_file = "credentials.json"
    target_youtube = authenticate_youtube(target_channel_client_secrets_file)

    # Define playlist ID and subtitle details
    playlist_id = "PLbpC3u41peksrSXFqMpTexRIQcS_syzsL"
    download_dir = "download_dir"
    uploaded_videos_file = "uploaded_videos.txt"
    category_id = "28"  # Technology category

    # Language and subtitle details
    subtitles_info = [
        {"path": "path_to_english_subtitle.srt", "language": "en", "name": "English Subtitles"},
        {"path": "path_to_japanese_subtitle.srt", "language": "ja", "name": "Japanese Subtitles"}
        # Add more subtitle details here if needed
    ]

    # Ensure download directory exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Retrieve video URLs from playlist
    video_urls = get_video_urls_from_playlist(original_youtube, playlist_id)

    # Read uploaded videos record
    uploaded_videos = read_uploaded_videos(uploaded_videos_file)

    for video_url in video_urls:
        # Scrape metadata
        title, description, tags = scrape_video_metadata(video_url)

        # Create a unique output path for the video
        video_id = video_url.split("v=")[1]
        output_path = os.path.join(download_dir, f"{video_id}.mp4")

        # Skip download if the file already exists
        if os.path.exists(output_path):
            print(f"File {output_path} already exists. Skipping download.")
        else:
            # Download video with retry logic
            print(f"Downloading video from {video_url} to {output_path}")
            download_video(video_url, output_path)

        # Check if the video is already uploaded
        if video_id in uploaded_videos:
            print(f"Video {video_id} already uploaded. Skipping upload.")
            continue

        # Upload video to target channel
        video_response = upload_video(target_youtube, output_path, title, description, category_id, tags)
        uploaded_video_id = video_response['id']
        print(f"Video uploaded with ID: {uploaded_video_id}")

        # Record uploaded video ID
        write_uploaded_video(uploaded_videos_file, video_id)

        # Upload multiple subtitles
        for subtitle_info in subtitles_info:
            subtitle_file = subtitle_info["path"]
            language = subtitle_info["language"]
            subtitle_name = subtitle_info["name"]
            
            # Check if the subtitle file exists
            if os.path.exists(subtitle_file):
                subtitle_response = upload_subtitle(target_youtube, uploaded_video_id, subtitle_file, language, subtitle_name)
                print(f"Subtitles uploaded with ID: {subtitle_response['id']}")
            else:
                print(f"Subtitle file {subtitle_file} not found. Skipping upload for {subtitle_name}.")

if __name__ == "__main__":
    main()

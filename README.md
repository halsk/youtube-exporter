# YouTube Video Downloader and Uploader

This Python script is designed to automate the process of downloading videos from a YouTube playlist, scraping their metadata, and then uploading them to another YouTube channel with the option to include multiple subtitle tracks.

## Features

- Authenticate with YouTube API
- Download videos from a specified YouTube playlist
- Scrape video metadata (title, description, tags)
- Upload videos to a target YouTube channel
- Upload multiple subtitle tracks for each video

## Prerequisites

Before you can run this script, you will need to:

1. Install Python 3.x on your system.
2. Install the required Python libraries with `pip install -r requirements.txt`.
3. Enable the YouTube Data API by following these steps:
   - Go to the [Google API Console](https://console.developers.google.com/).
   - Create a new project or select an existing one.
   - In the dashboard, click on "ENABLE APIS AND SERVICES".
   - Search for "YouTube Data API v3" and enable it.
   - In the credentials section, click on "Create credentials" and choose "OAuth client ID".
   - If prompted, configure the consent screen.
   - Set the application type to "Desktop app" and give it a name.
   - Once the credentials are created, download the JSON file and save it as `credentials.json` in the project directory.
4. Obtain OAuth 2.0 client credentials from the Google API Console and save the file as `credentials.json` in the project directory.

## Usage

Before running the script, you need to install the necessary Python libraries. You can do this by running the following command in your terminal:

```
pip install -r requirements.txt
```


To use this script, follow these steps:

1. Set the `playlist_id` variable to the ID of the YouTube playlist you want to download videos from.
2. Set the `category_id` variable to the YouTube category ID for the uploaded videos.
3. Define the subtitle information in the `subtitles_info` list if you want to upload subtitles.
4. Run the script with `python main.py`.

## Important Notes

- The `download_dir` directory is used to store the downloaded videos. Make sure you have enough space on your disk.
- The `.gitignore` file is configured to ignore the `credentials.json` and `download_dir` to prevent uploading sensitive information to version control.

## License

This project is open-sourced under the MIT License. See the LICENSE file for more information.

## Disclaimer

This tool is for educational purposes only. Please ensure you have the right to download and upload the content from and to YouTube.

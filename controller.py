from utils import VK, YouTube
def process_video_data(title, description, category, platforms):

    YouTube.VideoUploader.upload_video(
        video_file=video_path,
        title=video_title,
        description=video_description,
        category_id="27",  # Education
        privacy_status="private",  # "public", "private", "unlisted"
        tags=["api", "python", "youtube", "программирование"]
    )
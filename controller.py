from utils import VK, YouTube
def process_video_data(title, description, category, file, image, tags):

    YouTube.VideoUploader.upload_video(
        file,
        title,
        description,
        category, # TODO id категории
        tags, 
        privacy_status="private",  # TODO приватность
        
    )
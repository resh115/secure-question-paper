from b2sdk.v2 import InMemoryAccountInfo, B2Api
from config import B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME

def get_bucket():
    if not B2_KEY_ID or not B2_APPLICATION_KEY or not B2_BUCKET_NAME:
        raise RuntimeError("Backblaze configuration is incomplete.")

    info = InMemoryAccountInfo()
    api = B2Api(info)
    api.authorize_account("production", B2_KEY_ID, B2_APPLICATION_KEY)
    return api.get_bucket_by_name(B2_BUCKET_NAME)

def upload_bytes(file_name: str, data: bytes, content_type="application/octet-stream"):
    bucket = get_bucket()
    return bucket.upload_bytes(data, file_name, content_type=content_type)

def download_bytes(file_name: str) -> bytes:
    bucket = get_bucket()
    downloaded = bucket.download_file_by_name(file_name)
    return downloaded.response.content

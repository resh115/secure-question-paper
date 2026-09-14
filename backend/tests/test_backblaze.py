from services.backblaze import get_bucket

bucket = get_bucket()
print("Backblaze connection successful!")
print("Bucket:", bucket.name)

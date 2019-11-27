from tqdm import tqdm

from boto.s3.connection import S3Connection

def get_file_names(access_key, secret_access_key):
    """ Gets the names of all train, validation, and test files in the open-images AWS bucket """
    conn = S3Connection(access_key, secret_access_key)
    bucket = conn.get_bucket('open-images-dataset', validate=False)
    files = {}
    for subset in ["train", "validation", "test"]:
        files[subset] = []
        print("Getting {} images".format(subset))
        for file in tqdm(bucket.list("{}/".format(subset))):
            files[subset].append(file)
    return files

import urllib.request
import urllib.error
import hashlib
import base64
import time
import warnings
import os
from PIL import Image
from io import BytesIO


def download_image(root_dir, image_id, md5_image_hash, image_url, rotation=None, download_folder=None,
                   attempts=None, timeout=None, wait=None):
    """ Attempts to download the image, if it fails None is returned, otherwise the image_id

    Parameters
    ----------
    root_dir : str
        Root directory to download to
    image_id : str
        Id of the image being downloaded
    md5_image_hash : str
        Expected base64-encoded MD5 hash of downloaded image
    image_url : str
        Url to download image from
    rotation : int
        How much to rotate image by (must be one of 0, 90, 180, 270, or None), default None meaning no rotation
    download_folder : str
        Folder to download images into
    attempts : int
        Maximum number of attempts to try downloading image
    timeout : float
        Timeout in seconds for request
    wait : float
        Time to wait after a failed download

    Returns
    -------
    str
        The image id if the download is successful, otherwise None
    """

    download_folder = download_folder or 'images'
    attempts = attempts or 3
    timeout = timeout or 2
    wait = wait or 2
    warn_msg = None
    data = None
    while attempts > 0:
        try:
            resp = urllib.request.urlopen(image_url, timeout=timeout)
        except urllib.error.HTTPError as e:
            warn_msg = str(e)
            attempts -= 1
            if attempts != 0:
                time.sleep(wait)
            continue
        warn_msg = None
        data = resp.read()
        hash_md5 = hashlib.md5()
        hash_md5.update(data)
        md5_download_hash = base64.b64encode(hash_md5.digest()).strip().decode('utf-8')
        if md5_download_hash != md5_image_hash:
            warn_msg = "MD5 did not match"
            attempts -= 1
            if attempts != 0:
                time.sleep(wait)
            continue
        break
    if warn_msg is not None:
        warnings.warn("Downloading {} failed with {}".format(image_id, warn_msg))
        return None
    img = Image.open(BytesIO(data))
    if rotation in [90, 180, 270]:
        img = img.rotate(rotation, expand=True)
    image_ext = image_url.split(".")[-1]
    image_path = os.path.join(root_dir, download_folder, "{}.{}".format(image_id, image_ext))
    img.save(image_path)
    return image_id

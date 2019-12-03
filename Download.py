import urllib.request
import urllib.error
import hashlib
import base64
import time
import warnings


def download_image(image_path, image_id, md5_image_hash, url, attempts=None, timeout=None, wait=None):
    """ Attempts to download the image, if it fails None is returned, otherwise the image_id

    Parameters
    ----------
    image_path : str
        Path to save the image at if the download succeeds
    image_id : str
        Id of the image being downloaded
    md5_image_hash : str
        Expected base64-encoded MD5 hash of downloaded image
    url : str
        Url to download image from
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

    attempts = attempts or 3
    timeout = timeout or 5
    wait = wait or 5
    warn_msg = None
    data = None
    while attempts > 0:
        try:
            resp = urllib.request.urlopen(url, timeout=timeout)
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
    f = open(image_path, 'wb')
    f.write(data)
    f.close()
    return image_id

import urllib.request
import urllib.error
import hashlib
import base64
import time
import warnings
import os
from PIL import Image
from io import BytesIO

Image.MAX_IMAGE_PIXELS = None


def resize_one_dim(img, longest, new_length):
    """ Resizes image such that longest/shortest side of the image is of new_length

    Parameters
    ----------
    img : PIL.Image.Image
        Image to be resized
    longest : bool
        Which side to make new_length long, if True pick longest side, otherwise pick shortest
    new_length : int
        Required length for new side

    Returns
    -------
    PIL.Image.Image
        Resized image
    """

    w, h = img.size
    if longest:
        resize_width = w > h
    else:
        resize_width = w < h
    if resize_width:
        h = int(h * (new_length / w))
        w = new_length
    else:
        w = int(w * (new_length / h))
        h = new_length
    return img.resize((w, h), Image.BILINEAR)


def keep_aspect_ratio_resizer(img):
    """ Resizes image using method discussed in Faster RCNN paper. First resizes image such that shortest side becomes
    600 pixels long, and if the longer side exceeds 1024 pixels, resizes such that the longer size is 1024 pixels
    instead.

    Parameters
    ----------
    img : PIL.Image.Image
        Image to be resized

    Returns
    -------
    PIL.Image.Image
        Resized image
    """
    new_img = resize_one_dim(img, False, 600)
    w, h = new_img.size
    if max(w, h) > 1024:
        new_img = resize_one_dim(img, True, 1024)
    return new_img


def download_image(root_dir, image_id, md5_image_hash, image_url, rotation=None, resize=None,
                   download_folder=None, attempts=None, timeout=None, wait=None, common_download_errors=None):
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
    resize : bool
        Whether to resize images as described in the Faster RCNN paper, and discussed here
        https://github.com/tensorflow/models/issues/1794#issuecomment-311569473 . Benefit is reduces storage space
        without effecting training if using the FasterRCNN Inception ResNet V2 architecture. Default is False.
    download_folder : str
        Folder to download images into
    attempts : int
        Maximum number of attempts to try downloading image
    timeout : float
        Timeout in seconds for request
    wait : float
        Time to wait after a failed download
    common_download_errors : bool
            Whether to show common expected download error (HTTP 404 and 410) messages, default False

    Returns
    -------
    str
        The image id if the download is successful, otherwise None
    """

    resize = resize if resize is not None else False
    download_folder = download_folder or 'images'
    attempts = attempts or 3
    timeout = timeout or 2
    wait = wait or 2
    common_download_errors = common_download_errors if common_download_errors is not None else False
    code = None
    warn_msg = None
    data = None
    image_ext = image_url.split(".")[-1]
    image_path = os.path.join(root_dir, download_folder, "{}.{}".format(image_id, image_ext))
    if not os.path.isfile(image_path):
        while attempts > 0:
            try:
                resp = urllib.request.urlopen(image_url, timeout=timeout)
                code = None
                warn_msg = None
                data = resp.read()
            except urllib.error.HTTPError as e:
                code = e.code
                warn_msg = str(e)
                attempts -= 1
                if attempts != 0:
                    time.sleep(wait)
                continue
            except Exception as e:
                warn_msg = str(e)
                attempts -= 1
                if attempts != 0:
                    time.sleep(wait)
                continue
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
            if common_download_errors or code not in [404, 410]:
                warnings.warn("Downloading {} failed with {}".format(image_id, warn_msg))
            return None
        img = Image.open(BytesIO(data))
        if rotation in [90, 180, 270]:
            img = img.rotate(rotation, expand=True)
        if resize:
            img = keep_aspect_ratio_resizer(img)
        img.save(image_path)
    return image_id

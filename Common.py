import csv
import re
import os

import sys
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def load_csv_as_dict(csv_path, fieldnames=None, delimiter=None):
    """ Loads the csv DictReader

    Parameters
    ----------
    csv_path : str
        Path to csv
    fieldnames : list of str
        List of fieldnames, if None then fieldnames are take from the first row
    delimiter : str
        String to split on 

    Returns
    -------
    csv.DictReader
        DictReader object of path
    """

    delimiter = delimiter or ","
    f = open(csv_path, encoding='latin1')
    c = csv.DictReader(f, fieldnames=fieldnames, delimiter=delimiter)
    return c


def new_csv_as_dict(csv_path, fieldnames):
    """ Loads the csv DictWriter

    Parameters
    ----------
    csv_path : str
        Path to csv
    fieldnames : list of str
        List of fieldnames for csv

    Returns
    -------
    csv.DictWriter
        DictWriter object of path
    """

    f = open(csv_path, 'w', encoding='latin1', newline='')
    c = csv.DictWriter(f, fieldnames=fieldnames)
    return c


def copy_rows_on_image_id(root_dir, new_folder, csv_file, image_ids):
    """ For the csv file specified, creates a copy in new_folder, where rows that are not in image_ids are omitted

    Parameters
    ----------
    new_folder : str
        New folder to place new CSV
    root_dir : str
        Root directory contianing csv files and new folder
    csv_file : str
        Location of CSV file
    image_ids : set of str
        Set of image_ids who's rows should be copied over
    """

    path = os.path.join(root_dir, csv_file)
    new_path = os.path.join(root_dir, new_folder, csv_file)
    c = load_csv_as_dict(path)
    w = new_csv_as_dict(new_path, c.fieldnames)
    rows = [row for row in c if row["ImageID"] in image_ids]
    w.writeheader()
    w.writerows(rows)


def new_text_file(txt_path, lines):
    """ Writes the lines to the specified text file

    Parameters
    ----------
    txt_path : str
        Path to text file
    lines : list of str
        List of lines to be written
    """

    f = open(txt_path, 'w', encoding='latin1')
    f.writelines(lines)


def extract_image_id_from_flickr_static(static_url):
    """ Given a static url extract the image id

    Parameters
    ----------
    static_url : str
        Static url to photo, one of kind:
            https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
                or
            https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}_[mstzb].jpg
                or
            https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{o-secret}_o.(jpg|gif|png)

    Returns
    -------
    str
        Image id of url
    """

    pattern = r"(?:.*?\/\/?)+([^_]*)"
    image_id = re.findall(pattern, static_url)[0]
    return image_id

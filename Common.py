import csv
import re
import os
from tqdm import tqdm

import sys

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)


class Common:
    def __init__(self, image_level=None):
        """ Builds the object

        Parameters
        ----------
        image_level : bool
            Whether using image-level dataset, set to False if using bounding boxes, by default is True
        """

        self.image_level = True if image_level is None else image_level

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

        print("Creating new {}".format(csv_file))
        path = os.path.join(root_dir, csv_file)
        new_path = os.path.join(root_dir, new_folder, csv_file)
        c = Common.load_csv_as_dict(path)
        w = Common.new_csv_as_dict(new_path, c.fieldnames)
        rows = [row for row in tqdm(c) if row["ImageID"] in image_ids]
        w.writeheader()
        w.writerows(rows)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def pass_args_to_f(f, args):
        """ Given a function f pass it the list of args

        Parameters
        ----------
        f : function
            Function to pass the args to
        args : list
            List of args

        Returns
        -------
        Return type of function f
            Value returned by f for arguments args
        """

        return f(*args)

    def get_image_labels_file(self, subset):
        """ Get the name of the image labels file for the specified subset

        Parameters
        ----------
        subset : str
            Subset want filename for, one of train, validation, test

        Returns
        -------
        str
            Name of image labels file for the subset
        """

        return "{}-annotations-human-imagelabels{}.csv".format(subset, "-boxable" if not self.image_level else "")

    def get_image_ids_file(self, subset):
        """ Get the name of the image ids file for the specified subset

        Parameters
        ----------
        subset : str
            Subset want filename for, one of train, validation, test

        Returns
        -------
        str
            Name of image ids file for the subset
        """

        return "{}-images-{}with-rotation.csv".format(subset, (
            "with-labels-" if self.image_level else "boxable-") if subset == "train" else "")

    @staticmethod
    def get_boxes_file(subset):
        """ Get the name of the boxes file for the specified subset

        Parameters
        ----------
        subset : str
            Subset want filename for, one of train, validation, test

        Returns
        -------
        str
            Name of boxes file for the subset
        """

        return "{}-annotations-bbox.csv".format(subset)

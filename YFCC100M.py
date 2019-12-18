from Common import Common
import os
from tqdm import tqdm

dataset_rows = ["LineNumber", "ID", "Hash", "UserNSID", "UserNickname", "DateTaken", "DateUploaded",
                "CaptureDevice", "Title", "Description", "UserTags", "MachineTags", "Longitude", "Latitude",
                "LongLatAcc", "PageURL", "DownloadURL", "LicenseName", "LicenseURL", "ServerIdentifier",
                "FarmIdentifier", "Secret", "OriginalSecret", "OriginalExtension", "Video"]
places_row = ["ID", "PlacesInfo"]


class YFCC100M:
    def __init__(self, image_level=None):
        """ Builds the object
        
        Parameters
        ----------
        image_level : bool
            Whether using image-level dataset, set to False if using bounding boxes, by default is True
        """

        self.image_level = True if image_level is None else image_level
        self.common = Common(self.image_level)

    def join_labels_to_yfcc(self, labels_dir, yfcc_dir, new_folder="Extended", dataset=None, places=None):
        """ Joins the Open Images labels to the YFCC100M datasets specified, outputting the result in the same directory
            with the file ending "-extended.csv" instead of ".csv". The output file maintains the same order, but where
            no matches to YFCC100M was found the rows are omitted from the output file

        Parameters
        ----------
        labels_dir : str
            Path to the directory of CSV labels files
        yfcc_dir : str
            Directory where the YFCC files are stored
        new_folder : str
            Folder to put the joined dataset in
        dataset : bool
            Whether to extend with the dataset file, by default true
        places : bool
            Whether to extend with the places file, by default true
        """

        dataset = True if dataset is None else dataset
        places = True if places is None else places

        os.mkdir(os.path.join(labels_dir, new_folder))

        print("Building dictionary mapping Flickr ID to OpenImages ID")
        rows_by_flickr_id = {}
        order = {}
        matches = set()
        for subset in ["train", "validation", "test"]:
            print("Loading {}".format(subset))
            labels_file = self.common.get_labels_file(subset)
            labels_path = os.path.join(labels_dir, labels_file)
            open_images = Common.load_csv_as_dict(labels_path)
            rows_by_flickr_id[subset] = {}
            order[subset] = []
            for row in tqdm(open_images):
                static_url = row["OriginalURL"]
                flickr_id = Common.extract_image_id_from_flickr_static(static_url)
                order[subset].append(flickr_id)
                rows_by_flickr_id[subset][flickr_id] = row
                if dataset:
                    for col_name in dataset_rows:
                        if col_name != "ID":
                            rows_by_flickr_id[subset][flickr_id][col_name] = ''
                if places:
                    for col_name in places_row:
                        if col_name != "ID":
                            rows_by_flickr_id[subset][flickr_id][col_name] = ''

        if dataset:
            print("Matching Open Images to YFCC100M Dataset")
            yfcc100m_dataset = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_dataset"),
                                                       fieldnames=dataset_rows,
                                                       delimiter="\t")
            YFCC100M._join_matches(rows_by_flickr_id, matches, yfcc100m_dataset)

        if places:
            print("Matching Open Images to YFCC100M Places")
            yfcc100m_places = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_places"), fieldnames=places_row,
                                                      delimiter="\t")
            YFCC100M._join_matches(rows_by_flickr_id, matches, yfcc100m_places)

        print("Writing results to file")
        fieldnames = list(rows_by_flickr_id["train"][order["train"][0]].keys())
        for subset in ["train", "validation", "test"]:
            image_ids = set()
            labels_file = self.common.get_labels_file(subset)
            new_labels_path = os.path.join(labels_dir, new_folder, labels_file)
            w = Common.new_csv_as_dict(new_labels_path, fieldnames)
            rows = [rows_by_flickr_id[subset][flickr_id] for flickr_id in order[subset] if flickr_id in matches]
            for row in rows:
                image_ids.add(row["ImageID"])
            w.writeheader()
            w.writerows(rows)

            anno_file = self.common.get_anno_file(subset)
            Common.copy_rows_on_image_id(labels_dir, new_folder, anno_file, image_ids)

    @staticmethod
    def _join_matches(rows_by_flickr_id, matches, yfcc100m):
        """ Given the dataset from yfcc100m, iterate over it, for every match with OpenImages, add the flickr image id to
            matches, and update the column values with those given in the YFCC100M dataset

        Parameters
        ----------
        rows_by_flickr_id : dict of str -> dict of str -> OrderedDict of str -> str
            First level of dictionary is train, validation, and test, second level is flickr image id's that are part of
            that subset, third level is OrderedDict mapping column names to values
        matches : set of str
            Set of image id's from the training, validation, and test set found in the YFCC100M dataset
        yfcc100m : csv.DictReader
            Dict reader for a YFCC100M dataset
        """
        for row in tqdm(yfcc100m):
            flickr_id = row["ID"]
            for subset in ["train", "validation", "test"]:
                if rows_by_flickr_id[subset].get(flickr_id):
                    for col_name in row.keys():
                        if col_name != "ID":
                            rows_by_flickr_id[subset][flickr_id][col_name] = row[col_name]
                    matches.add(flickr_id)

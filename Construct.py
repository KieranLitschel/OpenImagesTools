import os
from Select import Select
from Common import Common
from tqdm import tqdm
import random
import multiprocessing
import Download
from functools import partial


class Construct:
    def __init__(self, image_level=None):
        """ Builds the object

        Parameters
        ----------
        image_level : bool
            Whether using image-level dataset, set to False if using bounding boxes, by default is True
        """

        self.image_level = image_level
        self.common = Common(self.image_level)

    def build_images_csv(self, anno_file, labels_file, new_folder, root_dir, classes):
        """ Given an annotations file and labels file, builds a new one containing only the specified classes in the new
            specified folder

        Parameters
        ----------
        anno_file : str
            Name of csv files with labels, typically "XXX-annotations-human-imagelabels.csv"
        labels_file : str
            Name of csv files with annotations, typically "XXX-images-with-labels-with-rotation.csv"
        new_folder : str
            New folder to place new CSV's
        root_dir : str
            Root directory contianing csv files and new folder
        classes : set of str
            Set of classes to be kept
        """

        anno_path = os.path.join(root_dir, anno_file)
        print("Selecting images to keep")
        images_to_keep = Select.select_images_with_class(anno_path, classes)
        for csv_file_name in [anno_file, labels_file]:
            print("Saving rows for {}".format(csv_file_name))
            old_path = os.path.join(root_dir, csv_file_name)
            new_path = os.path.join(root_dir, new_folder, csv_file_name)
            old_c = self.common.load_csv_as_dict(old_path)
            new_c = self.common.new_csv_as_dict(new_path, old_c.fieldnames)
            rows = []
            for row in tqdm(old_c):
                if row['ImageID'] in images_to_keep and (
                        row.get('LabelName') is None or row.get('LabelName') in classes):
                    rows.append(row)
            new_c.writeheader()
            new_c.writerows(rows)

    def build_classes_sub_files(self, classes, new_folder, root_dir):
        """ Given a set of classes to keep and the locations of CSV's, builds a new directory where only the specified
            classes are kept

        Parameters
        ----------
        classes : iterable of str
            Set of classes to be kept
        new_folder : str
            New folder to place new CSV's
        root_dir : str
            Root directory contianing csv files and new folder
        """

        os.mkdir(os.path.join(root_dir, new_folder))
        if not isinstance(classes, type):
            classes = set(classes)
        for subset in ["train", "validation", "test"]:
            print("Building new CSVs for {}".format(subset))
            anno_file = self.common.get_anno_file(subset)
            labels_file = self.common.get_labels_file(subset)
            self.build_images_csv(anno_file, labels_file, new_folder, root_dir, classes)

    def build_classes_sample(self, new_folder, root_dir, n, seed=None):
        """ Samples n random classes and builds a new dataset in new_folder where only the specified classes are present

        Parameters
        ----------
        new_folder : str
            New folder to place new CSV's
        root_dir : str
            Root directory contianing csv files and new folder
        n : int
            Number of classes to select
        seed : int
            Seed for random number generator
        """

        classes_file = 'classes-trainable.txt'
        classes_path = os.path.join(root_dir, classes_file)
        print("Selecting random sample of {} classes".format(n))
        classes = Select.select_random_classes(classes_path, n, seed=seed)
        self.build_classes_sub_files(classes, new_folder, root_dir)
        new_classes_path = os.path.join(root_dir, new_folder, classes_file)
        Common.new_text_file(new_classes_path, classes)

    def build_images_sample(self, new_folder, root_dir, ns, n_jobs=None, required_columns=None, seed=None,
                            attempts=None,
                            timeout=None, wait=None):
        """ Samples n random images and builds a new dataset in new_folder where only the specified classes are present

        Parameters
        ----------
        new_folder : str
            New folder to place new CSV's
        root_dir : str
            Root directory containing csv files and new folder
        ns : tuple of int
            Number of images to select for (training, validation, test) respectively, if any are None all are sampled
        n_jobs : int
            Number of images to download in parallel at once. Default of 9, as there are around 9 farms, so this means
            on average we'll only be making 1 request to a farm at a time
        required_columns : list of str
            Set of columns required to not be the empty string for the row to be included in the sample, if None
        seed : int
            Seed for random number generator
        attempts : int
            Maximum number of attempts to try downloading an image
        timeout : float
            Timeout in seconds for a request
        wait : float
            Time to wait after a failed download attempt
        """

        seed = seed or 0
        n_jobs = n_jobs or 9

        new_root = os.path.join(root_dir, new_folder)
        images_folder = os.path.join(new_root, "images")

        os.mkdir(new_root)
        os.mkdir(images_folder)

        subsets = ["train", "validation", "test"]
        for i in range(len(subsets)):
            subset = subsets[i]
            n = ns[i]

            print("Building subset for {}".format(subset))

            labels_file = self.common.get_labels_file(subset)
            labels_path = os.path.join(root_dir, labels_file)
            anno_file = self.common.get_anno_file(subset)

            print("Loading images rows")
            rows = Select.get_rows(labels_path, required_columns=required_columns)
            selected_image_ids = set()

            os.mkdir(os.path.join(images_folder, subset))

            if n is None:
                n = len(rows)
            else:
                print("Selecting {} rows".format(n))
                random.seed(seed)
                random.shuffle(rows)
            pos = 0
            pool = multiprocessing.Pool(n_jobs)
            downloader = partial(Common.pass_args_to_f,
                                 partial(Download.download_image, images_folder, download_folder=subset,
                                         attempts=attempts,
                                         timeout=timeout, wait=wait))
            req = n
            print("Downloading images")
            while req > 0:
                args = [[row["ImageID"], row["OriginalMD5"], row["OriginalURL"]] for row in rows[pos: pos + req]]
                successful_download_ids = tqdm(pool.imap(downloader, args))
                for image_id in successful_download_ids:
                    if image_id is not None:
                        selected_image_ids.add(image_id)
                pos += req
                available = len(rows) - pos
                failed = n - len(selected_image_ids)
                req = min(failed, available)
                if req > 0:
                    print("Failed to download {} images, trying to download next {} instead".format(failed, req))

            print("Creating new CSVs for subset")
            for csv_file in [labels_file, anno_file]:
                print("Creating new {}".format(csv_file))
                Common.copy_rows_on_image_id(root_dir, new_folder, csv_file, selected_image_ids)

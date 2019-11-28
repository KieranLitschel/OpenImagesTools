import random
import os
import csv
from tqdm import tqdm


def load_csv_as_dict(csv_path):
    """ Loads the csv DictReader

    Parameters
    ----------
    csv_path : str
        Path to csv

    Returns
    -------
    csv.DictReader
        DictReader object of path
    """

    f = open(csv_path, encoding='latin1')
    c = csv.DictReader(f)
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

    f = open(csv_path, 'w', encoding='latin1')
    c = csv.DictWriter(f, fieldnames=fieldnames)
    return c


def new_text_file(txt_path, lines):
    f = open(txt_path, 'w')
    f.writelines(lines)


class Select:
    @staticmethod
    def classes_to_names(desc_path):
        """ Maps class names to human descriptions

        Parameters
        ----------
        desc_path : str
            Path to csv file of class descriptions, typically "class-descriptions.csv". Note that by default the columns
            in this file do not have headers, so you'll need to add "LabelName" and "HumanLabel" at the top of the
            corresponding columns in the file

        Returns
        -------
        dict of str -> str
            Dictionary where key is the class name and value is the human description of the class
        """

        c = load_csv_as_dict(desc_path)
        label_to_human_label = {}
        for row in c:
            label_to_human_label[row["LabelName"]] = row["HumanLabel"]
        return label_to_human_label

    @staticmethod
    def get_class_names(classes_path):
        """ Loads the classes names from file into a set.

        Parameters
        ----------
        classes_path : str
            Path to text file of classes, typically "classes-trainable.txt"

        Returns
        -------
        set of str
            Classes names
        """

        f = open(classes_path, 'r', encoding='latin1')
        classes = set()
        label = f.readline().rstrip()
        while label:
            classes.add(label)
            label = f.readline().rstrip()
        return classes

    @staticmethod
    def select_random_classes(classes_path, n, seed=None):
        """ Loads the class classes from file and selects a random sample n.

        Parameters
        ----------
        classes_path : str
            Path to text file of classes, typically "classes-trainable.txt"
        n : int
            Number of classes to return
        seed : int
            Seed for random number generator

        Returns
        -------
        list of str
            n classes randomly sampled from the text file
        """

        seed = seed or 0
        random.seed(seed)
        classes = Select.get_class_names(classes_path)
        chosen_classes = random.sample(classes, n)
        return chosen_classes

    @staticmethod
    def select_images_with_class(annotations_path, classes):
        """ Loads the annotations file and returns a list of images in it that belong to one of the classes passed.

        Parameters
        ----------
        annotations_path : str
            Path to csv files with annotations, typically "XXX-annotations-human-imagelabels.csv"
        classes : iterable of str
            Classes that we want to find the images for

        Returns
        -------
        list of str
            List of image IDs that belong to at least one of the classes
        """
        if not isinstance(classes, set):
            classes = set(classes)
        c = load_csv_as_dict(annotations_path)
        images = set()
        for row in tqdm(c):
            image_id = row["ImageID"]
            label = row["LabelName"]
            if label in classes:
                images.add(image_id)
        return images


class Construct:

    @staticmethod
    def build_images_csv(anno_file, labels_file, new_folder, root_dir, classes):
        """ Given an annotations file and labels file, builds a new one containing only the specified classes in the new
            specified folder

        Parameters
        ----------
        anno_file : str
            Name of csv files with annotations, typically "XXX-annotations-human-imagelabels.csv"
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
            old_c = load_csv_as_dict(old_path)
            new_c = new_csv_as_dict(new_path, old_c.fieldnames)
            rows = []
            for row in tqdm(old_c):
                if row['ImageID'] in images_to_keep and (
                        row.get('LabelName') is None or row.get('LabelName') in classes):
                    rows.append(row)
            new_c.writeheader()
            new_c.writerows(rows)

    @staticmethod
    def build_classes_sub_files(classes, new_folder, root_dir):
        """ Given a set of classes to keep and the locations of CSV's, builds a new directory where only the specified
            classes are kept

        Parameters
        ----------
        classes : set of str
            Set of classes to be kept
        new_folder : str
            New folder to place new CSV's
        root_dir : str
            Root directory contianing csv files and new folder
        """

        for subset in ["train", "validation", "test"]:
            print("Building new CSVs for {}".format(subset))
            anno_file = "{}-annotations-human-imagelabels.csv".format(subset)
            labels_file = "{}-images-with-labels-with-rotation.csv".format(subset)
            Construct.build_images_csv(anno_file, labels_file, new_folder, root_dir, classes)

    @staticmethod
    def build_classes_sample(new_folder, root_dir, n, seed=None, classes_file=None):
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
        classes_file : str
            File name of text file containing all classes
        """

        os.mkdir(os.path.join(root_dir, new_folder))
        classes_file = classes_file or 'classes-trainable.txt'
        classes_path = os.path.join(root_dir, classes_file)
        print("Selecting random sample of {} classes".format(n))
        classes = Select.select_random_classes(classes_path, n, seed=seed)
        new_classes_path = os.path.join(root_dir, new_folder, classes_file)
        new_text_file(new_classes_path, classes)
        classes = set(classes)
        Construct.build_classes_sub_files(classes, new_folder, root_dir)

import random
from tqdm import tqdm
import Common


def class_names_to_human_names(desc_path):
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

    c = Common.load_csv_as_dict(desc_path)
    label_to_human_label = {}
    for row in c:
        label_to_human_label[row["LabelName"]] = row["HumanLabel"]
    return label_to_human_label


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
    classes = get_class_names(classes_path)
    chosen_classes = random.sample(classes, n)
    return chosen_classes


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
    c = Common.load_csv_as_dict(annotations_path)
    images = set()
    for row in tqdm(c):
        image_id = row["ImageID"]
        label = row["LabelName"]
        if label in classes:
            images.add(image_id)
    return images

import Select
import os
from tqdm import tqdm
import Common


def get_class_counts(root_dir, human_readable=None):
    """ Returns the counts of each class for the training, validation, and test sets

    Parameters
    ----------
    root_dir : str
        Root directory containing csv files and new folder
    human_readable : bool
        Whether the dictionary should use the class labels as keys or human descriptions

    Returns
    -------
    dict of str -> dict of str -> int
        Top level dictionary is keyed by labels or human descriptions, second level is train, validation, or test,
        the value of the second level dictionary is the counts for that labels subset
    """

    human_readable = human_readable or True
    class_counts = {}
    for subset in ["train", "validation", "test"]:
        print("Loading CSVs for {}".format(subset))
        anno_file = "{}-annotations-human-imagelabels.csv".format(subset)
        anno_path = os.path.join(root_dir, anno_file)
        c = Common.load_csv_as_dict(anno_path)
        for row in tqdm(c):
            label_name = row["LabelName"]
            if not class_counts.get(label_name):
                class_counts[label_name] = {}
            if not class_counts[label_name].get(subset):
                class_counts[label_name][subset] = 0
            class_counts[label_name][subset] += 1
    if human_readable:
        label_to_human_label = Select.class_names_to_human_names(os.path.join(root_dir, "class-descriptions.csv"))
        for label in label_to_human_label.keys():
            class_counts[label_to_human_label[label]] = class_counts[label]
            del class_counts[label]
    return class_counts


def number_of_images(root_dir):
    """ Returns the count of all images

    Parameters
    ----------
    root_dir : str
        Root directory containing csv files and new folder

    Returns
    -------
    int
        Count of all images
    """
    total = 0
    counts = get_class_counts(root_dir)
    for label in counts.keys():
        for subset in counts[label].keys():
            total += counts[label][subset]
    return total


def download_space_required(root_dir):
    """ Returns the space required in bytes to download all training, validation, and test files

    Parameters
    ----------
    root_dir : str
        Root directory containing csv files and new folder

    Returns
    -------
    int
        Bytes required to download all training, validation, and test files
    """

    size = 0
    for subset in ["train", "validation", "test"]:
        labels_file = "{}-images-{}with-rotation.csv".format(subset, "with-labels-" if subset == "train" else "")
        print("Reading {}".format(subset))
        c = Common.load_csv_as_dict(os.path.join(root_dir, labels_file))
        for row in tqdm(c):
            size += int(row["OriginalSize"])
    return size

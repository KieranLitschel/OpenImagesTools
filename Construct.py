import os
import Select
import Common
from tqdm import tqdm


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
        old_c = Common.load_csv_as_dict(old_path)
        new_c = Common.new_csv_as_dict(new_path, old_c.fieldnames)
        rows = []
        for row in tqdm(old_c):
            if row['ImageID'] in images_to_keep and (
                    row.get('LabelName') is None or row.get('LabelName') in classes):
                rows.append(row)
        new_c.writeheader()
        new_c.writerows(rows)


def build_classes_sub_files(classes, new_folder, root_dir):
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
        anno_file = "{}-annotations-human-imagelabels.csv".format(subset)
        labels_file = "{}-images-{}with-rotation.csv".format(subset, "with-labels-" if subset == "train" else "")
        build_images_csv(anno_file, labels_file, new_folder, root_dir, classes)


def build_classes_sample(new_folder, root_dir, n, seed=None):
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
    build_classes_sub_files(classes, new_folder, root_dir)
    new_classes_path = os.path.join(root_dir, new_folder, classes_file)
    Common.new_text_file(new_classes_path, classes)

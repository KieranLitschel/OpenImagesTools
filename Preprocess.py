import random


def get_label_names(labels_path):
    """ Loads the class labels from file into a set.

    Parameters
    ----------
    labels_path : str
        Path to text file of labels, typically "classes-trainable.txt"

    Returns
    -------
    set of str
        Class labels
    """

    f = open(labels_path, encoding='latin1')
    labels = set()
    label = f.readline()
    while label:
        labels.add(label)
        label = f.readline()
    return labels


def select_random_classes(labels_path, n, seed=0):
    """ Loads the class labels from file and selects a random sample n.

    Parameters
    ----------
    labels_path : str
        Path to text file of labels, typically "classes-trainable.txt"
    n : int
        Number of classes to return
    seed : int
        Seed for random number generator

    Returns
    -------
    list of str
        n labels randomly sampled from the text file
    """

    random.seed(seed)
    labels = get_label_names(labels_path)
    chosen_labels = random.sample(labels, n)
    return chosen_labels

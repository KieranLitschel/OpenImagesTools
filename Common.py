import csv


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

    f = open(csv_path, 'w', encoding='latin1', newline='')
    c = csv.DictWriter(f, fieldnames=fieldnames)
    return c


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

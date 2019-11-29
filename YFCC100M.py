import Common
import os
from tqdm import tqdm

dataset_rows = ["LineNumber", "ID", "Hash", "UserNSID", "UserNickname", "DateTaken", "DateUploaded",
                "CaptureDevice", "Title", "Description", "UserTags", "MachineTags", "Longitude", "Latitude",
                "LongLatAcc", "PageURL", "DownloadURL", "LicenseName", "LicenseURL", "ServerIdentifier",
                "FarmIdentifier", "Secret", "OriginalSecret", "OriginalExtension", "Video"]
places_row = ["ID", "PlacesInfo"]


def join_labels_to_yfcc(labels_path, yfcc_dir, dataset=None, places=None):
    """ Joins the Open Images labels file to the YFCC100M datasets specified, outputting the result in the same directory
        with the file ending "-extended.csv" instead of ".csv"

    Parameters
    ----------
    labels_path : str
        Path to the of csv files with labels, typically "XXX-images-with-labels-with-rotation.csv"
    yfcc_dir : str
        Directory where the YFCC files are stored
    dataset : bool
        Whether to extend with the dataset file, by default true
    places : bool
        Whether to extend with the places file, by default true
    """

    dataset = True if dataset is None else dataset
    places = True if places is None else places

    print("Building dictionary mapping Flickr ID to OpenImages ID")
    c = Common.load_csv_as_dict(labels_path)
    rows_by_flickr_id = {}
    order = []
    for row in tqdm(c):
        static_url = row["OriginalURL"]
        flickr_id = Common.extract_image_id_from_flickr_static(static_url)
        order.append(flickr_id)
        rows_by_flickr_id[flickr_id] = row
        for key in dataset_rows:
            rows_by_flickr_id[flickr_id][key] = ''
        for key in places_row:
            if key != "ID":
                rows_by_flickr_id[flickr_id][key] = ''

    if dataset:
        print("Matching Open Images to YFCC100M Dataset")
        yfcc100m_dataset = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_dataset"), fieldnames=dataset_rows,
                                                   delimiter="\t")
        for row in tqdm(yfcc100m_dataset):
            flickr_id = row["ID"]
            if rows_by_flickr_id.get(flickr_id):
                for key in row.keys():
                    rows_by_flickr_id[key] = row[key]

    if places:
        print("Matching Open Images to YFCC100M Places")
        yfcc100m_places = Common.load_csv_as_dict(os.path.join(yfcc_dir, "yfcc100m_places"), fieldnames=dataset_rows,
                                                  delimiter="\t")
        for row in tqdm(yfcc100m_places):
            flickr_id = row["ID"]
            if rows_by_flickr_id.get(flickr_id):
                for key in row.keys():
                    if key != "ID":
                        rows_by_flickr_id[key] = row[key]

    print("Writing results to file")
    fieldnames = list(rows_by_flickr_id[order[0]].keys())
    w = Common.new_csv_as_dict(labels_path.replace(".csv", "-extended.csv"),
                               fieldnames=fieldnames)
    for key in order:
        w.writerow(rows_by_flickr_id[key])

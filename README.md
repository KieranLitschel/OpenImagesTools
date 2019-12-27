# Purpose
I made this repository whilst working on my final years honours project. In it I have implemented tools for segmenting 
and downloading the Open Images dataset, support both bounding boxes and image level labels. It supports the Open Images 
V5 dataset, but should be backward compatibile with earlier versions with a few tweaks.

The most notable contribution of this repository is offering functionality to join Open Images with YFCC100M. There is an overlap between the images described by the two datasets, and this can be exploited to gather additional metadata like user and geo tags without 
having to query the API. This proves highly efficient, for instance in the classes I was working with I found that of the 
2.4 million images of those classes in Open Images, 720 thousand of them were also in the YFCC100M dataset. Given that
you can only make 3600 requests per hour, it would have taken 8 hours to get a single attribute of metadata for these 720 thousand
images via requests to the Flicker API, whereas my implementation joined all information in the YFCC100M dataset onto the
 720 thousand photos in 50 minutes.
 
Another notable contribution is that the method for downloading a subset of files keeps track of how many images couldn't be downloaded.
So if for n photos sampled, we fail to download m of them, we then discard of the m photos from our subset, and sample another m, and we
keep repeating this until no downloads fail. This guarantees the user will end up with exactly the number of photos they requested for each
subset.

# Folder structure maintained

This repository offers various functions to segment a subsection of the dataset, for example segmenting by specifying 
a subset of classes to keep, or how many images to keep for the train, validation, and test splits. When a function to segment is 
applied to the directory containing the dataset, a subdirectory within it is created to store the segment, and the 
relevant rows are copied over from the directory to the subdirectory.

I chose this approach as it offers a lot of flexibility in the combinations of functions you can apply together, as 
functions can also be applied to the subdirectories created. For example you could apply a function to the original
dataset stored in a directory "Dataset" to select a subset of classes and store this in a directory "MyClasses", and then
join YFCC100M on the subdirectory to create a subdirectory within that called "Extended". Then you would have a directory
 structure of "Dataset/MyClasses/Extended". Or you could apply them in the opposite order, which would result in the 
 structure "Dataset/Extended/MyClasses".

The downside to this approach though is that duplicates of the CSV's rows and images (if downloaded) are stored at each
level of the directory hierarchy. This could be fixed with a few tweaks to how files are read and stored, but this is not
a priority for me at the moment.

# How to use the library

## Setting up

1. Pip install the requirements.txt into your Python environment.
2. Download the CSV's from the [Open Images website](https://storage.googleapis.com/openimages/web/download.html) and 
store them all in the same directory.
    1. For image level labels you need at least:
        1. Human-verified labels for train, validation, and test
        2. Image IDs for train validation and test
    2. For bounding boxes you need at least:
        1. Boxes for train, validation, and test
        2. Image labels for train, validation, and test
        3. Image IDs for train, validation, and test
3. Clone this repository onto your own computer using git clone. When running code start Python in the directory
of the cloned repository.

## Core functions

Here I'll highlight some of the most useful functions, you may want to use some functions I haven't listed here, for
example the class Statistics offers some methods for calculating things like the storage space required for the 
downloaded dataset. All methods are documented so the purpose of and how to use each method should be clear to 
understand.

Some objects will have an argument image_level required for their constructor. This should be set to False if you are
using the bounding boxes dataset, and True if you are using the image level dataset. This is required as each dataset
has slightly different files.

### Construct.classes_subset

This function takes a list of classes by class ID's (e.g. ["/m/012t_z", "/m/0jbk"], corresponding to person and animal
respectively), the root directory the CSV's are stored in, and the name that should be used for the new folder. It then
iterates over the labels file and selects all images that contain at least one of the tags in the list of classes 
provided. It then copies over the rows of the CSV's for the matching images, and discards of any labels that are not in
the list provided. 

The human names corresponding class ID's for 
[bounding boxes](https://storage.googleapis.com/openimages/v5/class-descriptions-boxable.csv) and
[image level labels](https://storage.googleapis.com/openimages/v5/class-descriptions.csv) can be found on the Open 
Images website, or by clicking the links above.

#### Example usage

Say we only want images with People or Animals in them. Then we could use the following code.

```python
path = "C:\\path_to_csv"
new_folder = "PeopleAndAnimals"
classes = ["/m/012t_z", "/m/0jbk"]
from Construct import Construct
Construct(image_level=False).classes_subset(classes, new_folder, path)
```

### Construct.images_sample

This function is used for selecting a subset of images from the CSV's to download. It takes as arguments the root
directory of the CSV's and new folder name to save the images to. It also takes an argument ns, which should be a tuple
of integers describing the number of samples to be taken for the training, validation, and test subsets respectively. 
Setting the values to None will result in all samples being taken for the respective subsets. This method does not offer
a guarantee that the number of images sampled will be balanced for each class (although this functionality could be 
added with a few modifications), instead it samples randomly the number specified for each subset. This means that the
distribution of the images sampled should be representative of the distribution of the dataset sampled from.

As discussed previously this function offers two guarantees:
* If an image does not match the one that the sample in the dataset was built from (as judged by checking the MD5 hash
matches the hash listed in the image ID csv, and that the response to the HTTP request is 200), then the image is
considered invalid and not included in the sample.
* Each subset will always be the exact size the user specified, unless the user has requested the subset be larger than
the number of valid samples in the dataset, in which case the size will be the number of valid samples.

There also some other optional arguments that can be passed that are noteworthy, including:

* n_jobs - Number of jobs, by default set to 9, as there are around 9 farms, so this means on average we'll only be 
making 1 request to a farm at a time.
* fix_rotation - This rotates images so that are they saved in the orientation the original uploader specified. This is
by default set to True. You can read more about why this is necessary 
[here](https://storage.googleapis.com/openimages/web/2018-05-17-rotation-information.html).
* required_columns - This is most useful when combining Open Images with YFCC100M. If there's a column (e.g. long and 
lat) that you'd like to not be None, you can add these columns as a list here, and then the sample will only be built
from rows where these columns are not None.
* seed - Seed for the random number generator, used to ensure repeatability of the randomness in the function. By default
 will use seed of 0.
* common_download_errors - Whether to show common expected download error (HTTP 404 and 410) messages. By default False.


 
#### Example usage

Say we want to build and download a subset of our PeopleAndAnimals dataset we built earlier, with 80 training
images, 10 validation images, and 10 test images. Then we could use the following code.

```python
from Construct import Construct
new_folder = "80-10-10"
root_dir = "C:\\path_to_csv\\PeopleAndAnimals"
ns = (80,10,10)
Construct(image_level=False).images_sample(new_folder, root_dir, ns)
```

### YFCC100M.join_labels_to_yfcc

This function takes as arguments the directory where the CSVs are stored, and the directory where the decompressed 
YFCC100M files are stored. It then builds a set of the Flickr image IDs in the image IDs CSV, and then iterates over 
YFCC100M, checking if the image ID for each row matches any in the Open Images dataset, and if so adding the the columns
in the YFCC100M dataset to the respective Open Images rows. The arguments "dataset" and "places" allow to specify which
parts of the YFCC100M dataset to iterate over to look for matches, by default both are set to True, indicating to 
iterate over both. Only rows from the Open Images dataset that match those in the YFCC100M dataset are kept, and they
are stored at the location specified by the argument new_folder.

#### Example usage

Say we wanted to join YFCC100M to our downloaded sub sample of images, PeopleAndAnimals. Then we could use the following
code.

```python
from YFCC100M import YFCC100M
labels_dir = "C:\\path_to_csv\\PeopleAndAnimals\\80-10-10"
yfcc_dir = "C:\\path_to_yfcc"
YFCC100M(image_level=False).join_labels_to_yfcc(labels_dir, yfcc_dir)
```

## Acknowledgements

For some of the functionality of this repository I took inspiration from 
[open_images_downloader](https://github.com/dnuffer/open_images_downloader) and
[OIDv4_Toolkit](https://github.com/EscVM/OIDv4_ToolKit). I decided to write my own repository from scratch as I had 
different needs, but they're both worth checking out in case they better suit your needs.
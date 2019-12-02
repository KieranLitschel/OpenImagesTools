# Open Images Tools
I made this repository whilst working on my final years honours project. In it I have implemented tools for processing 
the CSV's in the Open Images dataset. It supports the Open Images V5 dataset, and should be backward compatibile with 
earlier version and offers functionality to segment the dataset into classes and download them. The most notable contribution
of this repository is offering functionality to join Open Images with YFCC100M. There is an overlap between the images 
described by the two datasets, and this can be exploited to gather additional metadata like user and geo tags without 
having to query the API. This proves highly efficient, for instance in the classes I was working with I found that of the 
2.4 million images of those classes in Open Images, 720 thousand of them were also in the YFCC100M dataset. Given that
you can only make 3600 requests per hour, it would have taken 8 hours to get a single attribute of metadata for these 720 thousand
images, whereas my implementation joined all information in the YFCC100M dataset onto the 720 thousand photos in 50 minutes.

# Purpose

The most notable modes are Construct and YFCC100M. Construct offers functionality for creating a subdirectory within the
one the Open Images csv's are stored in, where only user specified classes are described. The reasoning for creating a 
subdirectory is two-fold, firstly so that only the classses required can be downloaded, the other reason is to reduce the
expense of joining YFCC100M onto the Open Images dataset, as the implementation is very memory expensive. YFCC100M offers
functionality for joining it onto the Open Images dataset, as described previously.
# Music Catalog
---
### Project Description
This web application provides a list of items within a variety of categories and integrates third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.

### Running the Application

* Install Vagrant and VirtualBox
* Clone the udac_fsnd_catalog repository
* Launch the Vagrant VM (vagrant up)
* Run the application within the VM (python /vagrant/catalog/project.py)
* Access and test the application by visiting http://localhost:5000 locally


#### Expected Behaviour
* the homepage displays all current music genres - http://localhost:5000/
* Selecting a specific genre shows you all the artists available for that genre.
* Selecting an artist shows you additional information about that artist.
* After logging in, a user has the ability to add, update, or delete item information. Users should be able to modify only those items that they themselves have created.
* The application should provide a JSON endpoint at the very least.
    * http://localhost:5000/genre/JSON - Genres
    * http://localhost:5000/genre/1/artists/4/JSON - artist details
    * http://localhost:5000/genre/2/artists/JSON - all artists in selected genre


# Music Catalog
---
### Project Description
Developed a content management system using the Flask framework in Python. Authentication is provided via OAuth and all data is stored within a PostgreSQL database.
---
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

i. The IP address and SSH port so your server can be accessed by the reviewer.
- IP address: 209.182.216.21 Port: 2200
ii. The complete URL to your hosted web application.
- http://209.182.216.21/
iii. A summary of software you installed and configuration changes made.
* added new user with required security changes - grader
* generated ssh key pairs
* configured firewall settings
* configured PostreSQL


Installed following:
* sudo dpkg-reconfigure tzdata
* sudo apt-get install python-psycopg2
* sudo apt-get install postgresql
* sudo apt-get install python-pip
* sudo apt-get install python-flask
* sudo apt-get install python-sqlalchemy
* sudo pip install flask
* sudo pip install httplib2
* sudo pip install requests
* sudo pip install oauth2client
* sudo apt-get install git



iv. A list of any third-party resources you made use of to complete this project.
- https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
- https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04

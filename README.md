# Build a Catalog Project

## Description
Source code for an online Catalog.

This project is part of the Udacity full stack Nanodegree program and requires preparation of an online catalog incorporating the following functionality:
* Database Operations (Create, Read, Update, Delete data)
* User authentication (Login / Logout)
* Authorisation checks (Only creator of item can run update / delete operations)
* JSON endpoint provision


Built using the Flask microframework using SQLAlchemy as the ORM, Bootstrap for CSS, Google Oauth for authentication.

## Directory Structure:
* README.md
* app.py (Flask app)
* catalog.db (Database)
* database_setup.py (To create new database with required tables and fields)
* dummy_data.py (To add dummy test data to database)
* client_secrets.json (Used for authentication flow)
* templates/ (Folder containing templates for various views)
* static/ (Folder containing CSS)
* Vagrantfile (To configure environment)

## Prerequisites:
* Python
* Flask
* SQLAlchemy

Note: This project is run as per Udacity requirements using Vagrant + VirtualBox. If you do not have this setup this may not work.

You can learn more about and download [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/) from the links.

# Getting Started:
The instructions below assume that you have setup the environment using the Vagrantfile and have a virtual machine running.

Copy the catalog directory to the /vagrant folder of your local machine.

Connect to the vagrant Virtual Machine:

	vagrant up
	vagrant ssh

Navigate to the catalog folder:

	cd /vagrant/catalog

Run app.py to load the server on localhost port 8000.

    python app.py

Go to your browser and navigate to http://localhost:8000 to view the website. Anyone is allowed to view the categories, items and the JSON data but only logged in users are allowed to add new items. Only the respective item creators (determined based on login information) are allowed to edit / delete the items they have added.


The database is currently populated with dummy data / test data. Incase you want to create a fresh database, delete the catalog.db file and run the following command to initialise a new empty database named catalog.db with the required tables and fields :

	python database_setup.py

You can then modify the contents of dummy_data.py as you wish to add your own custom categories / items. Do note that the frontend only supports adding new items, so at a minimum you will need to specify the categories that you want available in dummy_data.py. Once you have updated dummy_data.py run the following command to load the data in the newly created database:

	python dummy_data.py

You can then run app.py again to reload the server.


## Installation :
Clone the repository or unzip the folder contents on to the /vagrant folder your local drive / Virtual Machine.


## Acknowledgements
Udacity

Authentication flow code from [Udacity Project](https://github.com/udacity/ud330/blob/master/Lesson2/step5/project.py)



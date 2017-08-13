# Volunteer Manager

This application was purpose-built for a particular group but I figured it might prove useful as a starting point for 
other groups who need to manage volunteers.

If you add customizations or new things you find useful, I'm happy to look at pull requests.

### Things you need to run this app:
* Python 3.5+
* Django 1.11.4+
* Postgres 9.5+
  * The app uses the Postgres array field -- might work on older versions but I've only run it on 9.5 and 9.6
* A Vagrant file using an Ubuntu 16.04 box is included for convenience, but the app runs fine in a virtualenv on any OS 
(nothing Linux specific going on)
* RECAPTCHA
  * Used on forgot password form
  * Sign up at https://www.google.com/recaptcha/intro/

### Initial Setup
* Plug the appropriate settings into a .env file in the root of the project, or adjust the location and file name accordingly
  * .envsample includes the settings required for the application
  * Email is used for forgot password functionality so if you want that to work you'll need to put in some valid mail settings
* Run the migrations against a clean Postgres database
* Load gis/fixtures/ZipCode.json fixture
* Load security/fixtures/AccountType.json fixture
* Create a superuser

## General Information About the Application

### Users, Volunteers, Contacts, and Callers
There are three separate and distinct models related to people:
1. Users: aka "Staff," can log into the application and manage data based on their permissions
2. Volunteers: People who have completed a volunteer form. They cannot log into the application.
3. Contacts: General contacts for the organization who are not volunteers, e.g. media contacts. Cannot log into the 
application.
4. Callers (phonecall.PhoneCall model): People who attended conference calls. Note this model is also used to track 
volunteers and staff who attended conference calls through optional generic foreign keys.

### Account Types
This app is set up with three account types:
1. National Lead
2. State Lead
3. Regional Lead

The account types are hierarchical in that order, i.e. national leads have the most access, regional leads the least.

Specifically:
* Account types can manage all account types below them (but not their peers)
* Account type determines what users can and cannot see
  * National leads can see data from all states
  * State leads can only see data from their state(s)
  * Regional leads can only see data from their state(s)
* Superusers can see everything and edit all accounts

Users MUST have an account type to be able to log into the application.

### Organizations
Users can be part of one or more organization. Is a user is not a national lead, they will only see data for the 
organizations to which they are assigned.

### Petitions
The petitions model is set up based on the SpeakOut! plugin for WordPress. You may need to adjust this for your specific 
needs.

### Phone Calls
The PhoneCall model is based on dumps from MaestroConference. You may need to adjust this for your specific needs.

### Events
This portion of the application is not implemented and is left out of the menus in the application. It was started with 
a generic concept of "Contacts" which doesn't now match the use of the Contact model in the rest of the application.

### Management Commands
These are random things I built to handle importing of data from Excel. They may or may not be useful to others but I 
figured I'd leave them in here in case they save anyone some time.

# Project: Catalog App 
## Desciption
Flask web app supporting CRUD operations on a catalog with categories and items, with authentication using OAuth2.0 with LinkedIn.

## Technology
* Python
* Flask 
* OAuth2.0
* SQLAlchemy
* SQLite
* VirtualBox with Vagrant

## Deploy code
1. Install VirtualBox: https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
2. Install Vagrant: https://www.vagrantup.com/downloads.html
3. Download VM configuration: https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip
4. In terminal cd into "vagrant" directory.
5. Start virtual machine in terminal by running "vagrant up"
6. Log-in to virtual machine in terminal by running "vagrant ssh"
7. Clone this repository to your "vagrant" directory.
8. Create database by running "python database_setup.py" in terminal
12. Execute python script by running "python application.py" in terminal
13. Enjoy!
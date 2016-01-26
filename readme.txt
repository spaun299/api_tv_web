## This project run on Python 3.3, Flask and PostgreSQL 9.2 ##
## TO START PROJECT YOU SHOULD: ##
1.) install necessary libraries:
cd projects/iptv
source venv/bin/activate
pip install -r requirements.txt -t lib/
2.) if you want to connect to your openshift db via local machine(read only) you should:
install rhc - https://developers.openshift.com/en/getting-started-debian-ubuntu.html#client-tools
rhc port-forward -a iptv
if you are use phppgadmin you need to change port in this file:
/etc/phppgadmin/config.inc.php
3.) when you add new models, change or delete models to/from your project you should run alembic
(if you add new model file you should import class Base from this model to alembic_models.py file):
on local machine run:
alembic revision --autogenerate -m "test;"
alembic upgrade head
then on openshift run
alembic --config='alembic_openshift.ini' upgrade head
Notice, alembic versions of changes must be equal on local machine and on openshift server
.
Also you need to add tvonline.in.ua to your localhost: Add 127.0.0.1 tvonline.in.ua to /etc/hosts

# TicketSystem
Application used for tracking tickets of workers in small business.
It allows to create and manage tickets, make additional comments by users and add or delete attachments.
Tracking of actions is done by emailing users addresses. Project has additional API for easier usage or connecting to
other applications or frontends.

# Technologies
Project is created with:
* Django: 4.1.1
* django-crispy-forms: 1.14.0
* django-tables2: 2.4.1
* django-filter: 22.1
* djangorestframework: 3.13.1
* Bootstrap: 5.2.1
* Celery: 5.0.5

# Install

1. First clone the repository from GitHub and switch to the new directory:
```
$ git clone https://github.com/Bachi-code/TicketSystem.git
$ cd TicketSystem
```
2. Create and activate the virtualenv for your project.
3. Install packages with pip and requirements file.
```
$ pip install -r requirements.txt
```
4. Copy settings_local.py to TicketSystem folder
```
$ cp docs/settings_local.py TicketSystem/settings_local.py
```
5. Generate secret key. 
```
$ python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
6. Change database settings if needed.
7. Add your email core, user and password if needed.
8. Make migrations and migrate to database.
```
$ python manage.py makemigrations
$ python manage.py migrate
```
## Usage
1. Run Celery for email signals in project directory.
```
$ celery -A TicketSystem worker -l info --pool=solo
```
2. Run Django Server.
```
$ python manage.py runserver
```
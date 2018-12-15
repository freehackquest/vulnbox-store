# remove excess (unnecessary) files. 

rm db.sqlite3 

rm checker.py


# install django

sudo apt-get install python3-pip

sudo pip3 install django


# run from dir "freelife"

python3 manage.py makemigrations

python3 manage.py migrate


# check

python3 manage.py runserver


#deploy

sudo pip3 install gunicorn

sudo gunicorn freelife.wsgi:application --bind 0.0.0.0:8000
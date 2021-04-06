export FLASK_APP=setup.py
flask db init
flask db migrate
flask db upgrade
flask run
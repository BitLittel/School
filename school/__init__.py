from flask import Flask

school = Flask(__name__)
school.config.from_object('config')


from school import views
from school import filter

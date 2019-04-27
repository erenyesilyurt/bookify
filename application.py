from flask import Flask
import config

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.secret_key = config.APP_SECRET_KEY
db.init_app(app)

import views
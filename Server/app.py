from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Server.api.bots import bots

app = Flask(__name__)

db_url = 'postgresql://active_bash_user:12345@13.95.149.226:5432/active_bash_db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)
app.config['database'] = db

app.config["POST_ADDRESS"] = "http://127.0.0.1:8080"

app.register_blueprint(bots, url_prefix="/api/bot")


def main():
    app.run()


if __name__ == '__main__':
    main()


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Server.api.bots import bots

app = Flask(__name__)

db_url = 'postgresql://active_bash:12345@localhost:5432/active_bash'

# engine = create_engine(db_url, echo=False)
# Session = sessionmaker(bind=engine)
# session = Session()

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(app)
app.config['database'] = db

app.config["POST_ADDRESS"] = "http://127.0.0.1:8080"


login_manager = LoginManager()
login_manager.init_app(app)

app.register_blueprint(bots, url_prefix="/api/bot")


def main():
    app.run()


if __name__ == '__main__':
    main()


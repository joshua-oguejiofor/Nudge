import logging
from datetime import timedelta

from flask import Flask, render_template

from .auth import auth_route
from .config import settings
from .extensions import db, login_manager, migrate
from .model import User
from .todo import todo_route

logging.basicConfig(
    level= logging.INFO, 
    format= '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d |  %(message)s'
)


logger = logging.getLogger(__name__)


logger.info("Starting the Flask application...")

    
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = settings.SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=10)

    
db.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)

login_manager.login_view = 'login'  
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
            "error.html", 
            error="Error",
            message="Resourse not found, check your spelling and try again."
        )

@app.errorhandler(Exception)
def handle_exception(error):
    logger.exception(error)
    return render_template(
        "error.html", 
        error="Error",
        message="Opps, something went wrong. Be sure stay authenticated."
    )


auth_route(app)
todo_route(app)


if __name__ == "__main__":
    app.run(debug=True)




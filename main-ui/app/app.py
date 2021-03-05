from flask import Flask, redirect, url_for, render_template, request, after_this_request
from flask_login import LoginManager, login_user, current_user, login_required

import requests

import logging


LOGGER = logging.getLogger("main_ui")

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)

AUTH_SERVER = "http://auth_app.demo:5432"
CREATE_ACCOUNT_URL = f"{AUTH_SERVER}/create"
LOGIN_URL = f"{AUTH_SERVER}/login"
VERIFY_TOKEN_URL = f"{AUTH_SERVER}/validate"

CONTAINER_MANAGER = "http://container_manager:3232"
LIST_CONTAINER_URL = f"{CONTAINER_MANAGER}/containers"
CONTAINER_CREATE_URL = f"{CONTAINER_MANAGER}/create"

app = Flask(__name__)
app.secret_key = "dsbgajkhv hjasbkjagblkj"


login_manager = LoginManager(app)
login_manager.login_view = "user_login"

USERS = {}


class User:
    def __init__(self, user_id, name, token):
        self.user_id = user_id
        self.name = name
        self.token = token

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.token

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"User(user_id={self.user_id}, name={self.name}, token={self.token})"


@login_manager.user_loader
def get_user(token):

    resp = requests.post(VERIFY_TOKEN_URL, data={"token": token})

    if resp.status_code != 200:
        LOGGER.error(f"Unable to login with {token}. {resp.text}")
        return None

    return USERS.get(resp.json()["user_id"])


@app.route("/")
def welcome():
    return render_template("index.html")


def login(data):
    resp = requests.post(LOGIN_URL, data=data)
    if resp.status_code != 200:
        LOGGER.error(resp.text)
        return False

    resp_data = resp.json()

    @after_this_request
    def add_header(response):
        response.headers["auth_token"] = resp_data["token"]

        return response

    user = User(resp_data["user_id"], data["name"], resp_data["token"])
    USERS[user.user_id] = user
    login_user(user)

    return user


@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("login.html")

    data = {
        "name": request.values.get("user_name"),
        "password": request.values.get("password"),
    }

    login_info = login(data)

    if login_info:
        return redirect(url_for("welcome"))

    return "Oops, there was an error!", 500


@app.route("/register", methods=["GET", "POST"])
def user_registration():
    if request.method == "GET":
        return render_template("create_user.html")

    data = {
        "name": request.values.get("user_name"),
        "password": request.values.get("password"),
    }

    resp = requests.post(CREATE_ACCOUNT_URL, data=data)
    if resp.status_code != 200:
        LOGGER.error(resp.text)
        return "Oops, looks like there was a problem creating your account", 500

    login_info = login(data)
    if login_info:
        return redirect(url_for("welcome"))
    else:
        return "Account created, but login failed. Please contact the support team", 500


@app.route("/containers")
@login_required
def containers_view():
    resp = requests.get(LIST_CONTAINER_URL, data={"token": current_user.token})
    if resp.status_code != 200:
        LOGGER.error(resp.text)
        return "Oops, there was an error!", 500

    return render_template("container.html", containers=resp.json()["containers"])


@app.route("/containers/<string:container_name>")
@login_required
def container_view(container_name):
    resp = requests.get(
        f"{LIST_CONTAINER_URL}/{container_name}", data={"token": current_user.token}
    )

    if resp.status_code != 200:
        LOGGER.error(resp.text)
        return "Oops, there was an error!", 500

    data = resp.json()

    return render_template("container_info.html", container=data)


@app.route("/containers/create")
@login_required
def create_container():
    resp = requests.post(CONTAINER_CREATE_URL, data={"token": current_user.token})

    if resp.status_code != 200:
        LOGGER.error(resp.text)
        return "Oops, there was an error!", 500

    return redirect(url_for("containers_view"))


if __name__ == "__main__":
    LOGGER.info("Starting the application!")
    app.run(debug=True, host="0.0.0.0", port=1234)

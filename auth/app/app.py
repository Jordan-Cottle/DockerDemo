import os
from hashlib import sha256
from uuid import uuid4

from flask import Flask, g, request
from sqlalchemy.orm.exc import NoResultFound

from database import User, inject_session, close_session


app = Flask(__name__)

app.before_request(inject_session)
app.after_request(close_session)


@app.route("/create", methods=["POST"])
def create():
    name = request.values.get("name")
    password = request.values.get("password")
    salt = os.urandom(32)
    hashed = sha256(salt + password.encode()).digest()

    user = User(name=name, password=hashed.hex(), salt=salt.hex())

    g.session.add(user)
    g.session.commit()
    return {"status": "success"}


@app.route("/login", methods=["POST"])
def login():
    name = request.values.get("name")
    password = request.values.get("password")

    user = g.session.query(User).filter_by(name=name).one()

    salt = bytes.fromhex(user.salt)

    hashed = sha256(salt + password.encode()).digest().hex()

    if hashed == user.password:
        user.active_token = str(uuid4())
    else:
        return {"status": "Failed to login"}, 404

    return {"status": "success", "user_id": user.id, "token": user.active_token}


@app.route("/validate", methods=["POST"])
def validate():
    token = request.values.get("token")
    try:
        user = g.session.query(User).filter_by(active_token=token).one()
    except NoResultFound:
        return {"status": "Invalid Token"}
    else:
        return {"status": "success", "user_id": user.id, "user_name": user.name}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5432)

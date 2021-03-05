import os
import logging

from random import randint

import requests
from flask import Flask, request

VERIFY_TOKEN_URL = f"http://auth_app.demo:5432/validate"


LOGGER = logging.getLogger("main_ui")

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)


class Container:
    def __init__(self, name, port):
        self.name = name
        self.port = port

        self.key_filename = f"/container/keys/{self.name}.key"
        self.address = f"http://lanparty.mynetgear.com:{self.port}"

    @property
    def key(self):
        self.gen_key()
        with open(self.key_filename) as keyfile:
            return keyfile.read()

    @property
    def ssh_config(self):
        return {
            "address": self.address,
            "port": self.port,
            "key": self.key,
            "user_name": "demo-user",
        }

    def gen_key(self):
        if not os.path.isfile(self.key_filename):
            os.system(f"ssh-keygen -t rsa -f {self.key_filename} -N ''")

    def run(self):
        self.gen_key()

        host_pubkey_file = (
            "/home/ubuntu/DockerDemo/container_manager/keys/"
            + self.key_filename.split("/keys/")[-1]
            + ".pub"
        )
        code = os.system(
            f"docker run -d -p {self.port}:22 "
            f"-v {host_pubkey_file}:/home/ubuntu/.ssh/authorized_keys "
            f"--name {self.name} demo"
        )

        return code == 0

    def __eq__(self, other):
        return self.name == other.name


def get_user_data(token):

    resp = requests.post(VERIFY_TOKEN_URL, data={"token": token})

    if resp.status_code != 200:
        LOGGER.error(f"Unable to login with {token}. {resp.text}")
        return None

    return resp.json()


app = Flask(__name__)

CONTAINERS = {}

USED_PORTS = set()


@app.route("/containers")
def get_containers():
    token = request.values.get("token")

    user_data = get_user_data(token)
    if not user_data:
        return {"status": "error"}, 500

    data = []
    for container in CONTAINERS.setdefault(user_data["user_id"], []):
        data.append(
            {
                "container_name": container.name,
                "port": container.port,
                "address": container.address,
                "user_name": "demo-user",
            }
        )

    return {"status": "success", "containers": data}


@app.route("/containers/<string:container_name>")
def get_container(container_name):
    token = request.values.get("token")

    user_data = get_user_data(token)
    if not user_data:
        return {"status": "error"}, 500

    container = Container(container_name, 0)

    user_containers = CONTAINERS.setdefault(user_data["user_id"], [])
    if container not in user_containers:
        return {"status": "error"}, 500

    container = user_containers[user_containers.index(container)]

    return container.ssh_config


@app.route("/create", methods=["POST"])
def container_view():
    token = request.values.get("token")
    container_name = request.values.get("container_name")

    user_data = get_user_data(token)
    if not user_data:
        return {"status": "error"}, 500

    port = randint(10000, 20000)
    while port in USED_PORTS:
        port = randint(10000, 20000)

    if not container_name:
        container_name = f"{user_data['user_name']}_{port}_demo"

    container = Container(container_name, port)

    if not container.run():
        return {"status": "failed"}, 500

    CONTAINERS.setdefault(user_data["user_id"], []).append(container)

    return {"status": "success", **container.ssh_config}


@app.route("/destroy", methods=["POST"])
def create_container():
    token = request.values.get("token")
    container_name = request.values.get("container_name")

    user_data = get_user_data(token)
    if not user_data:
        return {"status": "error"}, 500

    user_containers = CONTAINERS.setdefault(user_data["user_id"], [])

    container = Container(container_name, 0)

    if container not in user_containers:
        return {"status": "error"}, 500

    os.system(f"docker kill {container_name}")
    os.system(f"docker rm {container_name}")

    user_containers.remove(container)

    return {"status": "success"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="3232")

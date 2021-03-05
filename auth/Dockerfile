FROM flask-base

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY data/ /auth_app/data
COPY app/ /auth_app

WORKDIR /auth_app
CMD ["python3", "app.py"]

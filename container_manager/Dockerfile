FROM docker:latest

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN addgroup -g 998 -S docker && adduser -S containerusr -G docker -u 1000
RUN mkdir /container && mkdir /container/keys && chown -R containerusr /container


USER containerusr
WORKDIR /container

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app/ /container

CMD ["python3", "app.py"]

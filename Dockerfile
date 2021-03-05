FROM ubuntu:20.04 as python-base

RUN apt-get -y update && \
    apt-get -y  install python3 python3-venv python3-pip python-is-python3 && \
    apt-get clean

RUN useradd -ms /bin/bash python
USER python

CMD [ "python", "--version" ]

FROM python-base as flask-base

RUN pip3 install flask

CMD ["pip3", "freeze"]

from ubuntu:20.04

RUN apt-get -y update && \
    apt-get install -y openssh-server sudo
RUN apt-get install -y git

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 demo-user
RUN echo "demo-user:test" | chpasswd

WORKDIR /home/ubuntu
RUN mkdir /home/ubuntu/.ssh && \
    chmod 700 /home/ubuntu/.ssh && \
    touch /home/ubuntu/.ssh/authorized_keys && \
    chmod 644 /home/ubuntu/.ssh/authorized_keys && \
    chown demo-user /home/ubuntu/.ssh /home/ubuntu/.ssh/authorized_keys

RUN service ssh start

EXPOSE 22

CMD [ "/usr/sbin/sshd", "-D" ]


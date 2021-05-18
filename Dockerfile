FROM ubuntu:20.04

ENV TZ=Europe
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installing dependencies
RUN apt update \
  && apt -y upgrade \
  && apt-get install git curl wget openssh-server ssh unzip python3 python3-pip python3-dev -y

# Setup & Enable SSH
RUN service ssh start && mkdir -p /var/run/sshd/ && mkdir /root/.ssh && chmod 700 /root/.ssh && \
    ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' -C root@framework
#COPY ./ssh/ /root/.ssh/
# Adding benchmark to known host and installing the SSH key on the benchmark as an authorized key
#RUN service ssh start &&  ssh-keyscan -H benchmark >> /root/.ssh/known_hosts && \
#    ssh-copy-id -i /root/.ssh/id_rsa.pub root@benchmark

RUN git clone https://github.com/SecureThemAll/SecureThemAll
WORKDIR /SecureThemAll

# Init framework
RUN ./init.sh; exit 0

#ENTRYPOINT ["./scripts/repair.py"]
#CMD ["MUT-APR", "-c", "BitBlaster", "-v", "--ssh", "root@benchmark", "--bench_root", "/root/cb-repair/"]

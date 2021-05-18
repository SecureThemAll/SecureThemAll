FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:avsm/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget ocaml build-essential gcc unzip ssh

########################################################################################################################
# Setup & Enable SSH
########################################################################################################################
RUN service ssh start && mkdir /root/.ssh && chmod 700 /root/.ssh && \
    ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' -C root@$(hostname) && mkdir -p /shared/ssh/ && \
    cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys

RUN mkdir /opt/mutapr
WORKDIR /opt/mutapr
########################################################################################################################
# Download and unzip MUT-APR's source code and binaries
########################################################################################################################
RUN wget -O mutaprfl.zip http://www.cs.colostate.edu/~bieman/MutAPR/mutaprfl-code.zip && unzip mutaprfl.zip -d /tmp && \
    mv /tmp/mutaprfl-code/* . && rm -rf /tmp/mutaprfl-code mutaprfl.zip

########################################################################################################################
# Change /bin/sh link from /bin/dash to /bin/bash
########################################################################################################################
RUN mv /bin/sh /bin/sh.orig && ln -s /bin/bash /bin/sh

ENV PATH "/opt/mutapr:${PATH}"

VOLUME /opt/mutapr

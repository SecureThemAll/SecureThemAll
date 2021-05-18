### Using Docker Compose

#### 1) Install Docker Compose 
Follow the instructions on https://docs.docker.com/compose/install/

#### 2) Create folders 
Create the directory ```/tmp/shared``` to be used as a shared volume and the subdirectory ```/tmp/shared/ssh``` for 
exchanging the public keys between the containers (alternatively you can use ssh-copy-id):
```console
$ mkdir -p /tmp/shared/ssh
```

#### 3) Build the project
Build the images with 
```console
$ sudo docker-compose --project-name securethemall build
```

#### 4) Start the services
Run the following to start the containers in the background and leave them running:
```console
$ sudo docker-compose --project-name securethemall up -d
```

#### 5) SSH Passwordless Login
The containers communicate through SSH. Follow the next steps to setup the connection:

First, generate the key pairs for genprog:
```console
root@genprog:# apt-get install -y ssh && service ssh start && mkdir -p /var/run/sshd/ && mkdir /root/.ssh && chmod 700 /root/.ssh && \
ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' -C root@$(hostname)
```

Enable the ssh service for each service
```console
:# service ssh start
```

Upload the public key from each tool and framework to the benchmark:
```console
root@genprog:# cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys
root@mutapr:# cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys
root@cquencer:# cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys
root@framework:# cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys
root@benchmark:# cat /shared/ssh/authorized_keys >> /root/.ssh/authorized_keys
```
Upload the public key from the framework to each tool:
```console
root@framework:/SecureThemAll# rm /shared/ssh/authorized_keys && cat /root/.ssh/id_rsa.pub >> /shared/ssh/authorized_keys
root@genprog:# cat /shared/ssh/authorized_keys >> /root/.ssh/authorized_keys
root@mutapr:# cat /shared/ssh/authorized_keys >> /root/.ssh/authorized_keys
root@cquencer:# cat /shared/ssh/authorized_keys >> /root/.ssh/authorized_keys
```

#### 6) Enabling core dumps on Docker for the benchmark 
Execute on you local machine the following command that will make the system redirect 
core dumps with the specified format to the path under the echo command.
```
echo '/cores/core.%p.%E' | sudo tee /proc/sys/kernel/core_pattern
```

#### 7) Execute the framework
When executing the framework pass the specific ```ssh_tool```, ```ssh_bench```, ```working_dir```  and ```bench_root``` 
options.
```console
root@framework:/SecureThemAll# ./scripts/repair.py GenProg -c BitBlaster --ssh_tool root@genprog --ssh_bench root@benchmark --bench_root /cb-repair --working_dir /shared -v
```
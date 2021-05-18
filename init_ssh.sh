#!/bin/bash

# init ssh
#service ssh start

# cleanup
rm /root/.ssh/known_hosts
rm /root/.ssh/authorized_keys

for host_file in /data/ssh/*; do
  host="${host_file##*/}"
  at_host="root@$host"

  if [[ "$host" == $(hostname) ]]; then
    continue
  fi

  # add host's key to authorized keys
  echo $host $at_host
  cat $host_file >> /root/.ssh/authorized_keys

  # add host to known_hosts
  host_ip=$(getent hosts $host | awk '{ print $2","$1}')
  ssh-keyscan -Ht rsa $host_ip >> /root/.ssh/known_hosts

  echo $(ssh -o StrictHostKeyChecking=no $at_host hostname)

done

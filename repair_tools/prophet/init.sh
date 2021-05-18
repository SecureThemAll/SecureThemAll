# init file for the VM with Ubuntu 14.04.1-32bit supplied by the author
# make and install prophet
cd /home/fanl/Workspace/prophet
sudo ./configure && cd ./src
sudo make -j2 && sudo make install && sudo ldconfig
cd /home/fanl/Workspace/prophet/wrap && make
# install dependencies for Python 3.7
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget libbz2-dev curl lzma-dev liblzma-dev
cd /tmp
sudo wget https://www.openssl.org/source/openssl-1.1.0g.tar.gz
sudo tar -zxf openssl-1.1.0g.tar.gz && cd openssl-1.1.0g
sudo ./config && sudo make -j4
sudo mv /usr/bin/openssl ~/tmp
sudo make install
sudo ln -s /usr/local/bin/openssl /usr/bin/openssl
sudo ldconfig && cd ..
# install Python 3.7.4
sudo wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
tar -xf Python-3.7.4.tar.xz
cd Python-3.7.4
sudo ./configure && sudo make -j 4 && sudo make install && cd ..
# Install pip 2 and 3
sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
sudo curl https://bootstrap.pypa.io/2.7/get-pip.py -o get-pip.py
sudo python get-pip.py
# Download SecureThemAll
cd /home/fanl/Workspace
git clone --recurse-submodules https://github.com/SecureThemAll/SecureThemAll.git
# Install framework Python 3 dependencies
cd SecureThemAll && python3 -m pip install -r requirements.txt
sudo add-apt-repository ppa:george-edison55/cmake-3.x -y
sudo apt-get update -y
# Install benchmark dependencies
cd benchmark/cb-repair && sudo apt-get install -y libc6-dev gcc-multilib g++-multilib gdb python-dev software-properties-common cmake
export CBREPAIR=`pwd`/src/cb_repair.py
#sudo apt-get upgrade -y
# Install benchmark Python 2 and 3 dependencies
python3 -m pip install python-dev-tools
python3 -m pip install -r python3_requirements.txt
python -m pip install -r python2_requirements.txt
python -m pip install PYyaml
# Setup the benchmark
./src/init.py
ulimit -c unlimited && sudo mkdir -p /cores && sudo chmod 777 /cores
# Benchmark's negative tests produce crashes that are used
# These need to be enabled and written to a specific location
sudo apt-get install --reinstall systemd
sudo systemctl unmask apport.service
sudo systemctl enable apport.service
echo '/cores/core.%p.%E' | sudo tee /proc/sys/kernel/core_pattern
# Copy necessary includes for Prophet to run profile localization
cp /home/fanl/Workspace/prophet/_prophet_profile* /tmp/

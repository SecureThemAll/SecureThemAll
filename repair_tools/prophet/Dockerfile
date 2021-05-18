FROM i686/ubuntu

# Install dependencies
RUN apt-get update && \
    apt-get install -y  subversion git g++ python perl cmake unzip wget curl \
                        build-essential bison flex libexplain-dev autoconf automake libtool \
                        m4 zlib1g-dev libtinfo-dev ssh libc6-dev gcc-multilib g++-multilib

# Setup & Enable Password-less SSH Logon
RUN service ssh start && mkdir -p /var/run/sshd/ && mkdir /root/.ssh && chmod 700 /root/.ssh && \
    ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' -C root@$(hostname)

#ENV CXX=g++
# Download and untar prophet source files
COPY ./prophet-0.1-src.tar.gz ./prophet.tar.gz
RUN mkdir -p prophet && tar -xf prophet.tar.gz -C /prophet && cd prophet && mv ./prophet-gpl/* . && rm -rf prophet-gpl
#RUN mkdir -p prophet && cd /tmp && \
#	wget -O prophet.tar.gz http://www.cs.toronto.edu/~fanl/program_repair/prophet-rep/prophet-0.1-src.tar.gz && \
#	tar -xf prophet.tar.gz -C /prophet

# Download and install LLVM+Clang 3.6.2 (https://stackoverflow.com/a/53159552)
RUN cd /tmp && wget -O llvm.tar.xz https://releases.llvm.org/3.6.2/llvm-3.6.2.src.tar.xz && \
	tar -xJf llvm.tar.xz && mkdir /opt/llvm-3.6.2 && mv llvm-3.6.2.src/* /opt/llvm-3.6.2 && \
	wget -O clang.tar.xz https://releases.llvm.org/3.6.2/cfe-3.6.2.src.tar.xz && tar -xJf clang.tar.xz && \
	mkdir /opt/llvm-3.6.2/tools/clang && mv cfe-3.6.2.src/* /opt/llvm-3.6.2/tools/clang
WORKDIR /opt/llvm-3.6.2
RUN mkdir build && cd build && cmake -G "Unix Makefiles" .. -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_RTTI=ON && \ 
	make -j8 
RUN cd build && cmake -DCMAKE_INSTALL_PREFIX=/usr/local/llvm -P cmake_install.cmake 	
ENV PATH="/usr/local/llvm/bin:${PATH}"
# Link the libraries for LLVM+Clang
RUN cd /usr/local/llvm && echo /usr/local/llvm/lib > /etc/ld.so.conf.d/libs.conf && ldconfig

WORKDIR /prophet
# Configure prophet and remove Werror
RUN sed -i -- 's/-Werror/ /g' configure.ac && sed -i '/benchmarks/d' configure.ac && sed -i -- 's/benchmarks/ /g' Makefile* && \
	find . -type f -name 'Makefile*' | xargs sed -i -- 's/-Werror/ /g'  && aclocal && libtoolize && autoheader && \
	automake --add-missing && autoconf && ./configure
RUN make -j8 && make install && service ssh restart
#RUN apt remove cmake && cd /opt && wget -O cmake.sh https://github.com/Kitware/CMake/releases/download/v3.19.1/cmake-3.19.1-Linux-x86_64.sh && \
#	chmod +x cmake.sh && ./cmake.sh && ln -s /opt/cmake-3.19.1-Linux-x86_64/bin/* /usr/local/bin && ln -s /usr/local/bin/cmake /usr/bin/cmake
# Remove the Werror flag (some unused variables give error), compile prophet's source code, install and enable SSH
#RUN cd /prophet/src && sed -i -- 's/-Werror/ /g' Makefile* && make -j4 && chmod +x prophet && \
#    make install && cp /prophet/src/_prophet_profile.h /tmp && service ssh restart
# Build extra tools used by prophet
#RUN cd /prophet/wrap && sed -i -- 's/-Werror/ /g' Makefile* && make

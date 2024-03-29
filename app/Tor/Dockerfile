#
# Dockerfile for the Private Tor Network
#
FROM gramineproject/gramine:v1.5

# Sets which version of tor to use. See the Tor Projects git page for available tags
# Examples:
#  * tor-0.2.8.4-rc
#  * tor-0.2.7.6
#  * tor-0.2.7.5
#  * release-0.2.1
ENV TOR_VER="release-0.3.4"

# Sets the nickname if you didn't set one, default ports, and the path
#  where to mount the key material used by the clients.
ENV TERM=xterm \
    TOR_ORPORT=7000 \
    TOR_DIRPORT=9030 \
    TOR_DIR=/tor

# Install build dependencies
RUN apt-get update && \
    build_temps="build-essential automake" && \
    build_deps="libssl-dev zlib1g-dev libevent-dev ca-certificates\
        dh-apparmor libseccomp-dev debhelper dh-systemd \
        git" && \
    DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install $build_deps $build_temps \
        init-system-helpers \
        pwgen && \
    mkdir /src

# Copy the base tor configuration file
COPY ./polluted_target_app/config/torrc* /etc/tor/

# Copy docker-entrypoint and the fingerprint script
COPY ./polluted_target_app/scripts/ /usr/local/bin/

# Persist data (Usually don't want this)
#VOLUME /etc/tor /var/lib/tor

# Create the shared directory
RUN mkdir ${TOR_DIR}

# ORPort, DirPort, ObfsproxyPort
# TODO make these match the env variables
# TODO is this necessary anymore?
EXPOSE 9001 9030 9051


RUN apt-get update && apt-get install -y \
    make \
    vim \
    iproute2

WORKDIR /src/
RUN git clone https://github.com/lilione/tor.git
WORKDIR /src/tor
RUN git checkout sting

RUN cd /src && \
    cd tor && \
    ./autogen.sh && \
    ./configure --disable-asciidoc && \
    make && \
    make install

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3-pip

RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev

RUN apt-get update && apt-get install -y npm
RUN npm install -g npm@7
RUN npm install -g truffle@5.4.29

WORKDIR /
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN gramine-sgx-gen-private-key
RUN mkdir /usr/local/var

ENTRYPOINT ["docker-entrypoint"]

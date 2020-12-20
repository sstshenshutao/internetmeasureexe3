#!/bin/bash
# @author: Shutao Shen (sstbage@gmail.com)

# install dependencies (ubuntu 18/20)
sudo apt-get install g++ make binutils autoconf automake autotools-dev libtool pkg-config \
  zlib1g-dev libcunit1-dev libssl-dev libxml2-dev libev-dev libevent-dev libjansson-dev \
  libjemalloc-dev cython python3-dev python-setuptools

# install rust and cargo (side-effect to the environment)
curl https://sh.rustup.rs -sSf | sh -s -- -y -q

# set the dirs 
parentDir=$(pwd)
somewhere2="${parentDir}/nghttp2dist"
echo "nghttp2 dist: ${somewhere2}"
mkdir "${somewhere2}"

# build quiche
cd $parentDir
git clone --recursive https://github.com/cloudflare/quiche
export PATH="$HOME/.cargo/bin:$PATH"
echo $PATH
cd quiche
cargo build --release --features pkg-config-meta,qlog
mkdir -p deps/boringssl/src/lib
ln -vnf $(find target/release -name libcrypto.a -o -name libssl.a) deps/boringssl/src/lib/

# build nghttp2
cd $parentDir
wget https://github.com/nghttp2/nghttp2/releases/download/v1.42.0/nghttp2-1.42.0.tar.bz2
tar xf nghttp2-1.42.0.tar.bz2
cd nghttp2-1.42.0/
./configure --prefix=${somewhere2} --enable-lib-only
make
make install

# add curl
cd $parentDir
git clone https://github.com/curl/curl
cd curl
./buildconf
./configure LDFLAGS="-Wl,-rpath,${parentDir}/quiche/target/release" --with-ssl=${parentDir}/quiche/deps/boringssl/src --with-nghttp2=${somewhere2}
make
# mkdir -p "${parentDir}/curl_dist"
# make DESTDIR="${parentDir}/curl_dist" install


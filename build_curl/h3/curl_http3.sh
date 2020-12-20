#!/bin/bash
# @author: Shutao Shen (sstbage@gmail.com)

# install dependencies (ubuntu 18/20)
sudo apt-get install -y build-essential git autoconf libtool cmake golang-go curl

# install rust and cargo (side-effect to the environment)
curl https://sh.rustup.rs -sSf | sh -s -- -y -q

# set the dirs 
parentDir=$(pwd)

# build quiche
cd $parentDir
git clone --recursive https://github.com/cloudflare/quiche
export PATH="$HOME/.cargo/bin:$PATH"
echo $PATH
cd quiche
cargo build --release --features pkg-config-meta,qlog
mkdir -p deps/boringssl/src/lib
ln -vnf $(find target/release -name libcrypto.a -o -name libssl.a) deps/boringssl/src/lib/

# add curl
cd $parentDir
git clone https://github.com/curl/curl
cd curl
./buildconf
./configure LDFLAGS="-Wl,-rpath,${parentDir}/quiche/target/release" --with-ssl=${parentDir}/quiche/deps/boringssl/src --with-quiche=${parentDir}/quiche/target/release
make
# mkdir -p "${parentDir}/curl_dist"
# make DESTDIR="${parentDir}/curl_dist" install


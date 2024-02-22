#!/usr/bin/env bash

set -e
set -x

rm -rf /private-tor-network/data/enclave/*


if [[ "$SGX" == 1 ]]; then

  cd /private-tor-network/src
  make clean || true
  make

  cd /private-tor-network
  make clean || true
  make

  gramine-sgx tor

elif [[ "$SGX" == -1 ]]; then

  tor -f /etc/tor/torrc

fi
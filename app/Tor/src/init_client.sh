#!/usr/bin/env bash

set -e
set -x

rm -rf /data/enclave/*


if [[ "$SGX" == 1 ]]; then

  cd /src
  make clean || true
  make

  cd /
  make clean || true
  make

  gramine-sgx tor

elif [[ "$SGX" == -1 ]]; then

  tor -f /etc/tor/torrc

fi
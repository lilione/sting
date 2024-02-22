#!/usr/bin/env bash

set -e
set -x

if [[ "$SGX" == 1 ]]; then

    GRAMINE="gramine-sgx ./python"

    make clean
    make

elif [[ "$SGX" == -1 ]]; then

    GRAMINE="python3"

fi

data_dir=/private-tor-network/data/enclave
input_dir=/private-tor-network/data/input
output_dir=/private-tor-network/data/output

rm -rf $data_dir/*
rm -rf $input_dir/*
rm -rf $output_dir/*

#$GRAMINE -m enclave.python.gen_signing_key

$GRAMINE -m sf_mod.create_stinger
$GRAMINE -m sf_mod.process_stinger
$GRAMINE -m sf_mod.leave_backdoor

python3 -m informer.make_evidence

$GRAMINE -m sf_mod.verify_evidence
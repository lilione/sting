#!/usr/bin/env bash

set -e
set -x

cd framework/sol
rm -rf ./build
truffle compile
cd ../../

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

$GRAMINE -m framework.python.enclave.generate_signing_keys

if [[ "$SGX" == 1 ]]; then
    $GRAMINE -m framework.python.enclave.prepare_sgx_report &> OUTPUT
    grep -q "Generated SGX report" OUTPUT && echo "[ Success SGX report ]"
    $GRAMINE -m framework.python.enclave.prepare_sgx_quote &>> OUTPUT
    grep -q "Extracted SGX quote" OUTPUT && echo "[ Success SGX quote ]"
    cat OUTPUT
    gramine-sgx-ias-request report --api-key $RA_TLS_EPID_API_KEY --quote-path "${output_dir}/quote" --report-path ias.report --sig-path ias.sig -c ias.cert -v

    python3 -m framework.python.interact_contract setup_bounty_contract
    python3 -m framework.python.interact_contract submit_enclave
fi


$GRAMINE -m sf_mod.create_stinger
$GRAMINE -m sf_mod.process_stinger
$GRAMINE -m sf_mod.leave_backdoor

python3 -m informer.make_evidence

$GRAMINE -m sf_mod.verify_evidence

if [[ "$SGX" == 1 ]]; then
    python3 -m framework.python.interact_contract collect_bounty
fi

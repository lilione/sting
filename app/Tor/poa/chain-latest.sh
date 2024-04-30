#!/usr/bin/env bash

set -e
set -x

POADIR=${POADIR:-/opt/poa}
KEYSTORE=${POA_KEYSTORE:-/opt/poa/keystore/}
DATADIR=${POA_DATADIR:-/opt/poa/data}

pkill -f geth || true

sleep 1

rm -rf $DATADIR
mkdir $DATADIR

geth --datadir $DATADIR init $POADIR/genesis.json

geth \
    --datadir $DATADIR \
    --keystore $KEYSTORE \
    --mine --allow-insecure-unlock --miner.etherbase 123463a4b065722e99115d6c222f267d9cabb524 \
    --unlock 0x123463a4b065722e99115d6c222f267d9cabb524 \
    --password $POADIR/empty_password.txt \
    --http \
    --http.addr 0.0.0.0 \
    --http.corsdomain '*' \
    --http.api admin,debug,eth,miner,net,personal,shh,txpool,web3 \
    --ws \
    --ws.addr 0.0.0.0 \
    --ws.origins '*' \
    --ws.api admin,debug,eth,miner,net,personal,shh,txpool,web3 \
    --syncmode full \
    --ipcpath "$DATADIR/geth.ipc" \
    2>> $DATADIR/geth.log &

sleep infinity

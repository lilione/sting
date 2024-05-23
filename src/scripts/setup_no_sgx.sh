#!/usr/bin/env bash

docker compose -f docker-compose-no-sgx.yml -f ../../src/chain/docker-compose.yml up -d

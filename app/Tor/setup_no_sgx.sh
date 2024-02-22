#!/usr/bin/env bash

docker compose -f docker-compose-no-sgx.yml down -v --remove-orphans

sudo rm -rf ./tor
sudo rm -rf ./data

docker compose -f docker-compose-no-sgx.yml up -d

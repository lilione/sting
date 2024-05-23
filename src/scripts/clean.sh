#!/usr/bin/env bash

docker compose -f docker-compose-no-sgx.yml -f ../../src/chain/docker-compose.yml down -v --remove-orphans
docker compose down -v --remove-orphans

### for Tor application
sudo rm -rf ./tor
sudo rm -rf ./data

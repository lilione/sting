#!/usr/bin/env bash

docker compose -f docker-compose-no-sgx.yml down -v --remove-orphans
docker compose -f docker-compose.yml down -v --remove-orphans

sudo rm -rf ./data

### for Tor application
sudo rm -rf ./tor

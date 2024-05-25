#!/usr/bin/env bash

docker compose -f docker-compose.yml -f ../../src/chain/docker-compose.yml up -d

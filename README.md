# Tor

```cd app/Tor```

# Flashbots

```cd app/BlockBuilding```

## Non-SGX version demo 

```bash setup_no_sgx.sh```

```
docker compose -f docker-compose-no-sgx.yml logs -f da1
docker compose -f docker-compose-no-sgx.yml logs -f client
```
Wait until see `Bootstrapped 100%: Done` in logs.

```docker compose -f docker-compose-no-sgx.yml exec client bash```

```bash run_demo.sh```

```bash clean.sh```

## Demo with remote attestation

```bash setup.sh```

```
docker compose logs -f da1
docker compose logs -f client
```
Wait until see `Bootstrapped 100%: Done` in logs.

```docker compose exec client bash```

```bash run_demo.sh```

```bash clean.sh```
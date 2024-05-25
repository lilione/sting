# Tor

```cd app/Tor```

# Flashbots

```cd app/BlockBuilding```

## Start demo 

w/o SGX

```bash ../../src/scripts/setup_no_sgx.sh```

w/ SGX

```bash ../../src/scripts/setup.sh```

## Check if Tor demo is ready to run

```docker logs -f tor-client-1```

Wait until see `Bootstrapped 100%: Done` in logs.

## Run Tor demo

```
docker exec -it tor-client-1 bash
bash run_demo.sh
```

## Shut down demo
```bash ../../src/scripts/clean.sh```
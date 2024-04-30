cd app/Tor
bash setup_no_sgx.sh
docker compose -f docker-compose-no-sgx.yml exec client bash
bash run_demo.sh

bash setup.sh
docker compose exec client bash
bash run_demo.sh
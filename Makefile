build:
	docker build -t caveat4u/ssh_keypair_tests:latest .

run:
	docker run -it -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets/client_secrets.json:/data/client_secrets/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 caveat4u/ssh_keypair_tests:latest

daemon:
	docker run -d  -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets/client_secrets.json:/data/client_secrets/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 caveat4u/ssh_keypair_tests:latest

explore:
	docker run -it -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets/client_secrets.json:/data/client_secrets/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 --entrypoint "/bin/bash" \
								 caveat4u/ssh_keypair_tests:latest

auth:
	docker run -it -v $(PWD)/client_secrets/client_secrets.json:/data/client_secrets/client_secrets.json \
								 caveat4u/ssh_keypair_tests:latest

develop:
	docker run -it -v $(PWD):/data --entrypoint "/bin/bash" caveat4u/ssh_keypair_tests:latest
build:
	docker build -t keypair_generator:latest .

run:
	docker run -it -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets.json:/data/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 keypair_generator:latest

daemon:
	docker run -d  -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets.json:/data/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 keypair_generator:latest

explore:
	docker run -it -v $(PWD)/creds.txt:/data/creds.txt \
								 -v $(PWD)/client_secrets.json:/data/client_secrets.json \
								 -v $(PWD)/config.yml:/data/config.yml \
								 --entrypoint "/bin/bash" \
								 keypair_generator:latest

develop:
	docker run -it -v $(PWD):/data --entrypoint "/bin/bash" keypair_generator:latest
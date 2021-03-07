build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml  up -d
	docker attach $$(docker-compose ps -q paralink_node) 

down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

backend:
	docker-compose -f docker-compose.yml up
	docker attach $$(docker-compose ps -q paralink_node)

test:
	docker-compose -f docker-compose.yml up -d
	docker exec $$(docker-compose ps -q paralink_node) /wait-for-it.sh -t 0 rabbitmq:5672 -- pipenv run python3 -m pytest tests/ -svvv; \
	ret=$$?; \
	docker-compose -f docker-compose.yml -f docker-compose.test.yml down; \
	exit $$ret


ipython:
	docker exec -it $$(docker-compose ps -q dod-stream) python -m IPython
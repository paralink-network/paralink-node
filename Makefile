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
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build -d
	docker attach $$(docker-compose ps -q paralink_node); \
	ret=$$?; \
	docker-compose -f docker-compose.yml -f docker-compose.test.yml down; \
	exit $$ret


ipython:
	docker exec -it $$(docker-compose ps -q dod-stream) python -m IPython
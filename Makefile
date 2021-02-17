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

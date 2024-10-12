DC = docker compose
APP_DEV = docker_compose/app.dev.yaml
POSTGRES = docker_compose/postgres.yaml
APP_SERVICE = main-app
ENV = --env-file .env

.PHONY: up
up:
	${DC} -f ${APP_DEV} -f ${POSTGRES} ${ENV} up -d --build --remove-orphans

.PHONY: down
down:
	${DC} -f ${APP_DEV} -f ${POSTGRES} ${ENV} down --remove-orphans

.PHONY: app-dev
app-dev:
	${DC} -f ${APP_DEV} ${ENV} up --build -d

.PHONY: app-dev-logs
app-dev-logs:
	${DC} -f ${APP_DEV} ${ENV} logs -f

.PHONY: storages
storage:
	${DC} -f ${POSTGRES} ${ENV} up -d --build

.PHONY: storages
storage-down:
	${DC} -f ${POSTGRES} ${ENV} down

.PHONY: down-dev
down-dev:
	${DC} -f ${APP_DEV} ${ENV} down

.PHONY: shell
shell:
	${DC} -f ${APP_DEV} ${ENV} exec -it ${APP_SERVICE} bash

.PHONY: upgrade
upgrade:
	${DC} -f ${APP_DEV} ${ENV} exec -it ${APP_SERVICE} bash -c "cd / && alembic upgrade head"

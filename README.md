# FastAPI + Postgres URL Saver

## Зависимости

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)

## Как использовать

**Клонируем репозиторий:**

   ```bash
   git clone https://github.com/your_username/your_repository.git
   cd your_repository
```

### Подготовка переменных окружения
Создать `.env` файл из `.env.example`

```
cp .env.example .env
```


### Команды запуска

* `make up` - Поднять приложение и базу данных
* `make down` - Остановить прилоежние и базу данных
* 
* `make app-dev` - Поднять приложение
* `make down-dev` - Остановить приложение


* `make storage` - Поднять базу данных
* `make storage-down` - Остановить базу данных


* `make app-dev-logs` - Смотреть логи приложения


* `make shell` - Войти в контейнер shell (bash)


* `make upgrade` - Применить миграции

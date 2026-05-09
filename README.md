# Future Events Tracker

CRUD-приложение для работы с карточками будущих событий на стеке FastAPI + React.

## Конфигурация

Приложение читает настройки из переменных окружения. Для локального запуска можно создать `.env` по образцу `.env.example` и при необходимости использовать `config/local.yaml` по образцу `config/local.example.yaml`.

Приоритет источников конфигурации:

- переменные окружения;
- `config/local.yaml`;
- `.env`;
- значения по умолчанию.

## Быстрый запуск

### Локально

Backend:

```bash
python run.py
```

Документация API будет доступна по адресу `http://127.0.0.1:8000/docs`.

Frontend:

```bash
cd frontend
npm.cmd install
npm.cmd run build
cd ..
```

После сборки frontend главная страница будет доступна через FastAPI по адресу `http://127.0.0.1:8000/`.

Локально backend по умолчанию использует SQLite, если `POSTGRES_HOST` не задан.

### Через Docker Compose

```bash
docker compose up --build
```

В контейнерном режиме проект запускает четыре сервиса:

- `postgres` — база данных PostgreSQL;
- `redis` — централизованное хранилище пользовательских сессий;
- `backend` — FastAPI-приложение;
- `frontend` — Nginx со статикой React и проксированием API.

Frontend будет доступен по адресу `http://127.0.0.1:8080/`.
Swagger будет доступен через frontend-прокси по адресу `http://127.0.0.1:8080/docs`.

В контейнерном режиме backend использует PostgreSQL, а локально без Docker может работать с SQLite.

## Проверка

```bash
python -m pytest
docker compose config
docker compose up -d
```

Для проверки отказоустойчивости backend можно запустить несколько экземпляров сервиса:

```bash
docker compose up -d --build --scale backend=3
```

Пользовательские сессии хранятся в Redis, поэтому один и тот же пользователь может обращаться к разным экземплярам backend без потери авторизации.

## Практическая работа №5: сборка, релиз, запуск и масштабирование

### Пользователи и сессии

Backend предоставляет маршруты:

- `POST /api/auth/register` — регистрация пользователя;
- `POST /api/auth/login` — вход и установка HTTP-only cookie `session_id`;
- `GET /api/auth/me` — проверка активной сессии;
- `POST /api/auth/logout` — завершение сессии.

В Docker Compose сессии сохраняются в Redis (`REDIS_URL=redis://redis:6379/0`). Это убирает зависимость от памяти конкретного процесса и позволяет масштабировать backend горизонтально.

### Сборка образа и релизы

CI-пайплайн находится в `.github/workflows/docker-image.yml`. При пуше в `main` он собирает backend Docker-образ и публикует его в GitHub Container Registry с уникальными тегами:

```text
ghcr.io/<owner>/<repo>:<commit-sha>
ghcr.io/<owner>/<repo>:run-<github-run-number>
```

Собранный образ не содержит конфигурацию окружения. Настройки передаются при запуске через переменные окружения. В Compose используется переменная `APP_DEBUG`, которая передается в приложение как `DEBUG`, чтобы избежать конфликта с системной переменной оболочки. По умолчанию для контейнеров задано `APP_DEBUG=false`, чтобы масштабируемые процессы не запускались с autoreload.

Проверить релизные метаданные можно через:

```bash
curl http://127.0.0.1:8080/api/release
```

Для запуска уже собранного образа без пересборки используется `docker-compose.release.yml`:

```bash
docker compose -f docker-compose.release.yml up -d
```

Перед запуском нужно задать `IMAGE_REF`, `IMAGE_TAG`, `RELEASE_ID` и остальные переменные окружения. Для отката достаточно указать предыдущий тег образа в `IMAGE_REF` и перезапустить сервис.

### Проверка масштабирования

```bash
docker compose up -d --build --scale backend=3
docker compose ps
```

После этого frontend-прокси обращается к сервису `backend`, а сессии остаются валидными благодаря Redis. Для нагрузки можно использовать любой локальный инструмент, например `curl` в цикле или `hey`, если он установлен.

Проверить распределение запросов можно через runtime endpoint:

```powershell
$results = for ($i = 1; $i -le 60; $i++) {
    (Invoke-RestMethod http://127.0.0.1:8080/api/instance).hostname
}
$results | Group-Object | Select-Object Name, Count
```

В результате должны появиться разные hostname контейнеров `backend`, а счетчик `Count` покажет, что запросы попадали не в один процесс.

Если установлен `hey`, можно создать нагрузку отдельно:

```bash
hey -n 100 -c 10 http://127.0.0.1:8080/api/instance
```

## Практическая работа №6: API доступа к данным и логирование

Доступ к данным приложения выполняется через публичные REST API:

- `/api/events` — работа с карточками событий;
- `/api/auth` — регистрация, вход и пользовательская сессия;
- `/api/release` и `/api/instance` — служебная информация для проверки релиза и масштабирования.

Клиентский код не подключается к PostgreSQL напрямую. Детали хранения скрыты за слоями `repositories` и `services`.

Для каждого HTTP-запроса backend добавляет или принимает заголовок `X-Request-ID`. Этот идентификатор возвращается в ответе и попадает в JSON-лог запроса. При штатной обработке лог пишется в stdout, при исключениях — в stderr. Файловые логи не используются.

Пример просмотра логов:

```bash
docker compose logs -f backend
```

## Практическая работа №7: равенство сред и корректное завершение

Окружения разработки и запуска унифицированы через Docker Compose:

- backend: `python:3.12-alpine`;
- PostgreSQL: `postgres:16-alpine`;
- Redis: `redis:7-alpine`;
- frontend build: `node:22-alpine`;
- frontend runtime: `nginx:1.27-alpine`.

Backend запускается без autoreload в контейнерах (`APP_DEBUG=false`) и использует `STOPSIGNAL SIGTERM`. Для корректного завершения настроены:

- `SHUTDOWN_TIMEOUT_SECONDS` для Uvicorn graceful shutdown;
- `stop_grace_period: 15s` в Docker Compose;
- lifecycle shutdown hook, который закрывает Redis session store и SQLAlchemy engine;
- `/ready` readiness endpoint;
- middleware, который возвращает `503 Service Unavailable`, если приложение уже находится в состоянии завершения.

Для демонстрации длительного запроса используется endpoint:

```bash
curl "http://127.0.0.1:8080/api/runtime/slow?seconds=5"
```

Проверка SIGTERM:

```bash
docker compose up -d --build --scale backend=3
docker compose ps
docker kill --signal=SIGTERM <backend-container-name>
docker compose ps
docker compose logs --tail=80 backend
```

## Практическая работа №8: административные задачи

Один и тот же Docker-образ может запускаться в разных режимах:

```bash
python run.py server
python run.py migrate
python run.py create-admin --email admin@example.com --password admin-password --full-name "Admin User"
```

Команда `server` запускает основной FastAPI-сервис. Команда `migrate` выполняет `alembic upgrade head` и завершает процесс. Команда `create-admin` сначала применяет миграции, а затем идемпотентно создает администратора: если пользователь с таким email уже есть, повторный запуск не создает дубль.

Миграции находятся в каталоге `alembic/`, начальная ревизия создает таблицы `events` и `users`, а текущая версия схемы фиксируется в таблице `alembic_version`. Если база была создана более ранней учебной версией через SQLAlchemy `create_all`, команда `migrate` помечает существующую совместимую схему как примененную через `alembic stamp`.

В Docker одноразовые административные задачи запускаются из того же образа:

```bash
docker compose run --rm migrate
docker compose run --rm backend python run.py create-admin --email admin@example.com --password admin-password --full-name "Admin User"
```

Сервис `migrate` в `docker-compose.yml` подключается к PostgreSQL по имени сервиса `postgres`, ждет healthcheck базы данных и завершается после выполнения Alembic-миграций. Это временный контейнер: после флага `--rm` он удаляется, а данные остаются в volume PostgreSQL.

Перед деплоем новой версии в CI/CD миграция должна запускаться отдельным одноразовым контейнером из фиксированного тега образа. Если миграция завершилась ошибкой, деплой останавливается.

В GitHub Actions это вынесено в job `deploy`, который запускается вручную через `workflow_dispatch` для выбранной среды. Перед деплоем workflow валидирует секреты PostgreSQL целевой среды и запускает тот же опубликованный образ командой `python run.py migrate`. Если команда миграции возвращает ошибку, job завершается с ошибкой и следующий шаг деплоя не выполняется.

Пример полного цикла:

```bash
git push
docker compose -f docker-compose.release.yml run --rm migrate
docker compose -f docker-compose.release.yml up -d
docker compose -f docker-compose.release.yml ps
```

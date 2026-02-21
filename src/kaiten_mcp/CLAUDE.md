# Kaiten MCP Server — Setup Instructions

MCP-сервер для Kaiten API. 246 инструментов: карточки, доски, проекты, документы, автоматизации, Service Desk и др.

## ВАЖНО: Как работает MCP stdio transport

MCP-сервер общается через **stdin/stdout** по протоколу JSON-RPC. Это значит:
- Сервер ДОЛЖЕН получать JSON на stdin и отвечать JSON на stdout.
- **НЕЛЬЗЯ** выделять TTY — терминальные escape-последовательности ломают протокол.
- При использовании Docker: флаг `-i` (stdin open) — обязателен, флаг `-t` (TTY) — **запрещён**.
- При использовании `docker compose run`: флаг `-T` **обязателен** (отключает TTY).

## Быстрый старт

Если проект клонирован, используй `make help` для списка всех целей:

```bash
make help        # Показать доступные цели
make dev-build   # Собрать deps-only образ (dev)
make build       # Собрать полный образ (distribution)
make venv        # Создать venv + установить пакет
make test        # Запустить тесты (Docker)
make lint        # Запустить линтеры (Docker)
```

## Подключение к Claude Code

Пользователь должен предоставить два значения и записать их в `.env` файл в директории проекта:
- `KAITEN_DOMAIN` — поддомен компании (например `mycompany` для `mycompany.kaiten.ru`)
- `KAITEN_TOKEN` — API-токен из настроек Kaiten

```bash
cp /path/to/kaiten-mcp/.env.example /path/to/kaiten-mcp/.env
# Отредактировать .env — вписать KAITEN_DOMAIN и KAITEN_TOKEN
```

**Принцип: credentials живут в `.env`, а НЕ в команде `claude mcp add`.** Смена домена/токена = редактирование `.env` + перезапуск Claude Code. Не нужно перерегистрировать MCP.

Спроси у пользователя способ запуска.

---

### Способ 1: Docker Compose (рекомендуется)

Docker Compose автоматически читает `.env` из директории проекта. Credentials нигде не хардкодятся.

**Шаг 1 — Собрать образ (однократно):**

```bash
docker compose --project-directory /path/to/kaiten-mcp build kaiten-mcp-dev
```

Для dev-режима (volume-mount, мгновенные изменения кода):
```bash
docker compose --project-directory /path/to/kaiten-mcp build kaiten-mcp-dev
```

Для baked-режима (всё в образе):
```bash
docker compose --project-directory /path/to/kaiten-mcp build kaiten-mcp
```

**Шаг 2 — Зарегистрировать MCP-сервер (без `-e` флагов!):**

Dev-режим (исходный код монтируется volume):
```bash
claude mcp add kaiten \
  -- docker compose --project-directory /path/to/kaiten-mcp run --rm -T kaiten-mcp-dev
```

Baked-режим (всё в образе):
```bash
claude mcp add kaiten \
  -- docker compose --project-directory /path/to/kaiten-mcp run --rm -T kaiten-mcp
```

**Шаг 3 — Перезапустить Claude Code** (`/exit` и запусти заново).

**Смена домена/токена:** отредактируй `.env` → перезапусти Claude Code. Перерегистрация НЕ нужна.

**После изменения кода (dev):** перезапусти Claude Code. Пересборка НЕ нужна.
**После изменения кода (baked):** пересобери образ + перезапусти Claude Code.

Почему `--project-directory`:
- Без него Docker Compose ищет `.env`, `docker-compose.yml` и build context относительно CWD.
- `--project-directory` указывает на корень проекта — всё находится корректно.
- `-T` отключает TTY (обязательно для MCP stdio transport).
- `-f` **НЕ решает проблему** — он задаёт только путь к yml, но CWD для `.env` не меняется.

---

### Способ 2: Docker run (с -e флагами)

Для `docker run` без Compose credentials передаются через `-e`. Это менее удобно — при смене домена нужна перерегистрация.

Dev-режим:
```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- docker run --rm -i \
     --read-only --tmpfs /tmp:noexec,nosuid,size=64m \
     --security-opt=no-new-privileges:true --cap-drop=ALL \
     -v /path/to/kaiten-mcp/src:/app/src:ro \
     -e KAITEN_DOMAIN -e KAITEN_TOKEN \
     kaiten-mcp:dev
```

Baked-режим:
```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- docker run --rm -i \
     --read-only --tmpfs /tmp:noexec,nosuid,size=64m \
     --security-opt=no-new-privileges:true --cap-drop=ALL \
     -e KAITEN_DOMAIN -e KAITEN_TOKEN \
     kaiten-mcp:latest
```

Для сборки образов:
```bash
docker build --target deps -t kaiten-mcp:dev /path/to/kaiten-mcp    # dev
docker build --target baked -t kaiten-mcp:latest /path/to/kaiten-mcp # baked
```

---

### Способ 3: Python (venv)

Для venv credentials тоже читаются из `.env` автоматически (server.py вызывает `load_dotenv()`). Но `.env` должен быть в CWD откуда Claude Code запускает процесс, поэтому надёжнее передать через `-e`:

```bash
python3 -m venv /path/to/kaiten-mcp/.venv
/path/to/kaiten-mcp/.venv/bin/pip install -e /path/to/kaiten-mcp
```

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- /path/to/kaiten-mcp/.venv/bin/kaiten-mcp
```

**После изменения кода:** перезапусти Claude Code (editable install подхватывает изменения).

---

### Scope: проект vs глобально

По умолчанию MCP регистрируется для текущего проекта. Для глобальной регистрации добавь `-s user`:

```bash
claude mcp add kaiten -s user \
  -- docker compose --project-directory /path/to/kaiten-mcp run --rm -T kaiten-mcp-dev
```

---

## Проверка

```bash
claude mcp list
```

Должен быть виден сервер `kaiten` со статусом `connected`.

---

## Частые ошибки и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| `command not found: timeout` / TTY-символы в stdout | `docker compose run` без `-T` или `-t` флаг | Добавь `-T` / убери `-t` |
| Сервер подключён, но инструменты не видны | Инструменты загружаются при старте сессии | Перезапусти Claude Code: `/exit` и заново |
| `env_file not found` / build context ошибки | Docker Compose не может найти `.env` | Используй `--project-directory` или `docker run` |
| `externally-managed-environment` | macOS/Linux запрещает системный pip | Используй venv: `python3 -m venv .venv` |
| Сервер зацикливается / не отвечает | TTY включён | Убери `-t`, добавь `-T` для docker compose |
| `MCP server kaiten already exists` | Уже зарегистрирован | `claude mcp remove kaiten` и заново |
| Код изменился, но сервер использует старый | Docker baked: код в образе | Dev mode: volume mount. Baked: пересобери образ |
| Permission denied в контейнере | Non-root user + read-only | Ожидаемо; для записи используй отдельный mount |
| Нужно сменить домен/токен (Compose) | Credentials в `.env` | Отредактируй `.env` → перезапусти Claude Code. Перерегистрация НЕ нужна |
| Нужно сменить домен/токен (docker run) | Credentials в `-e` флагах | `claude mcp remove kaiten` → `claude mcp add` с новыми значениями |

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Да | Поддомен компании (`mycompany` для `mycompany.kaiten.ru`) |
| `KAITEN_TOKEN` | Да | API-токен из настроек пользователя Kaiten |
| `KAITEN_MCP_OUTPUT_DIR` | Нет | Директория для сохранения больших ответов API (>200KB) |
| `LOG_LEVEL` | Нет | Уровень логирования Python (по умолчанию: `INFO`) |

## Безопасность Docker

Все Docker-команды используют hardened security flags:

| Флаг | Назначение |
|------|------------|
| `--read-only` | Файловая система контейнера только для чтения |
| `--tmpfs /tmp:noexec,nosuid,size=64m` | Temp-директория без исполнения |
| `--security-opt=no-new-privileges:true` | Запрет эскалации привилегий |
| `--cap-drop=ALL` | Сброс всех Linux capabilities |
| `-v src:/app/src:ro` | Исходный код read-only (dev mode) |
| Non-root user `mcp` (UID 1000) | Контейнер не работает под root |

## После подключения

Когда MCP-сервер подключён и Claude Code перезапущен, доступны 246 инструментов. Типичные сценарии:

**Обзор аккаунта:**
1. `kaiten_get_current_user` — текущий пользователь
2. `kaiten_get_company` — информация о компании
3. `kaiten_list_spaces` — все пространства
4. `kaiten_list_boards(space_id=X)` — доски пространства

**Создание карточки:**
1. `kaiten_list_spaces` — найти space_id
2. `kaiten_list_boards(space_id=X)` — найти board_id
3. `kaiten_list_columns(board_id=X)` — найти column_id
4. `kaiten_create_card(title="...", board_id=X, column_id=Y)`

**Управление задачей:**
1. `kaiten_get_card(card_id=X)` — текущее состояние
2. `kaiten_list_card_blockers(card_id=X)` — блокировки
3. `kaiten_list_comments(card_id=X)` — обсуждение
4. `kaiten_move_card(card_id=X, column_id=Y)` — перемещение

## Важные ограничения

- **Rate limiting**: сервер ограничивает частоту до ~4.5 req/s с автоматическим retry при 429.
- **API-ключ**: НИКОГДА не вызывай `kaiten_delete_api_key` для активного токена — это инвалидирует сессию.
- **405 Method Not Allowed**: некоторые эндпойнты могут быть недоступны на определённых тарифах Kaiten.
- **Типы ID**: большинство сущностей используют числовые ID. Документы, группы, автоматизации и проекты — UUID строки.

## Тесты (для разработки)

Тесты запускаются **только в Docker**:

```bash
# Все тесты (100% покрытие)
make test
# или напрямую:
docker compose -f tests/docker-compose.test.yml up --build test-overseer

# Линтеры
make lint

# E2E-тесты (нужен .env с реальными KAITEN_DOMAIN и KAITEN_TOKEN)
docker compose -f tests/docker-compose.test.yml up --build test-e2e-expanded
```

## Сравнение режимов

| | Docker dev | Docker baked | Python venv |
|---|---|---|---|
| Установка | `make dev-build` | `make build` | `make venv` |
| Изменения кода | Мгновенно (volume) | Пересборка образа | Мгновенно (editable) |
| Изменения зависимостей | Пересборка образа | Пересборка образа | `pip install -e .` |
| Изоляция | Полная (Docker) | Полная (Docker) | venv only |
| Безопасность | Hardened container | Hardened container | Системный уровень |
| Требования | Docker | Docker | Python 3.11+ |

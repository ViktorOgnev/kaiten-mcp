# Kaiten MCP Server — Setup Instructions

MCP-сервер для Kaiten API. 246 инструментов: карточки, доски, проекты, документы, автоматизации, Service Desk и др.

## ВАЖНО: Как работает MCP stdio transport

MCP-сервер общается через **stdin/stdout** по протоколу JSON-RPC. Это значит:
- Сервер ДОЛЖЕН получать JSON на stdin и отвечать JSON на stdout.
- **НЕЛЬЗЯ** выделять TTY — терминальные escape-последовательности ломают протокол.
- При использовании Docker: флаг `-i` (stdin open) — обязателен, флаг `-t` (TTY) — **запрещён**.
- При использовании `docker compose run`: флаг `-T` **обязателен** (отключает TTY).

## Подключение к Claude Code

Пользователь должен предоставить два значения:
- `KAITEN_DOMAIN` — поддомен компании (например `mycompany` для `mycompany.kaiten.ru`)
- `KAITEN_TOKEN` — API-токен из настроек Kaiten

Спроси у пользователя способ запуска: **Docker** или **Python (venv)**.

---

### Способ 1: Docker (рекомендуется)

**Шаг 1 — Собрать образ (однократно):**

```bash
docker build -t kaiten-mcp /path/to/kaiten-mcp
```

Замени `/path/to/kaiten-mcp` на реальный абсолютный путь к клонированному репозиторию.

**Шаг 2 — Зарегистрировать MCP-сервер:**

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- docker run --rm -i -e KAITEN_DOMAIN -e KAITEN_TOKEN kaiten-mcp
```

Замени `ДОМЕН` и `ТОКЕН` на реальные значения пользователя.

Как это работает:
- `claude mcp add -e VAR=value` — устанавливает переменную окружения в процессе, который Claude Code запускает.
- `docker run -e VAR` (без `=value`) — пробрасывает переменную из окружения хоста внутрь контейнера.
- `--rm` — удаляет контейнер после остановки.
- `-i` — держит stdin открытым (необходимо для MCP).
- **НЕ ДОБАВЛЯЙ `-t`** — TTY ломает JSON-RPC протокол.

**Шаг 3 — Перезапустить Claude Code:**

Скажи пользователю: выйди из Claude Code (`/exit`) и запусти заново. Инструменты Kaiten (246 шт.) появятся после перезапуска.

**Шаг 4 — Проверить:**

```bash
claude mcp list
```

Должен быть виден сервер `kaiten` со статусом `connected`.

---

### Способ 2: Python (venv)

**Шаг 1 — Создать venv и установить пакет:**

```bash
python3 -m venv /path/to/kaiten-mcp/.venv
/path/to/kaiten-mcp/.venv/bin/pip install -e /path/to/kaiten-mcp
```

**Шаг 2 — Зарегистрировать MCP-сервер:**

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- /path/to/kaiten-mcp/.venv/bin/kaiten-mcp
```

**Шаг 3 — Перезапустить Claude Code** (аналогично Docker).

---

### Альтернатива: Docker Compose

Если пользователь предпочитает docker compose, **обязательно** используй `--project-directory` и `-T`:

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=ДОМЕН \
  -e KAITEN_TOKEN=ТОКЕН \
  -- docker compose --project-directory /path/to/kaiten-mcp run --rm -T kaiten-mcp
```

Почему именно так:
- `--project-directory` — без него Docker Compose ищет `docker-compose.yml`, build context и `.env` относительно текущей рабочей директории (CWD), а не директории проекта. Это **главная причина** ошибок при запуске из другой папки.
- `-T` — отключает TTY. Без этого `docker compose run` выделяет pseudo-TTY, и терминальные escape-коды ломают JSON-RPC.
- `-f` **НЕ решает проблему** — он задаёт только путь к yml-файлу, но CWD для build context и .env не меняется.

---

## Частые ошибки и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| `command not found: timeout` / `command not found: gtimeout` | Использован `docker compose run` без `-T`, TTY-символы в stdout | Добавь `-T` в команду `docker compose run` |
| Сервер подключён, но инструменты не видны | Инструменты загружаются при старте сессии Claude Code | Перезапусти Claude Code: `/exit` и запусти заново |
| `Board should be deleted with force` / `env_file not found` | Docker Compose не может найти `.env` или build context | Используй `--project-directory` или переключись на `docker run` |
| `externally-managed-environment` при `pip install` | macOS/Linux запрещает ставить пакеты в системный Python | Используй venv: `python3 -m venv .venv && .venv/bin/pip install -e .` |
| Сервер зацикливается / не отвечает | TTY включён (`-t` флаг или отсутствует `-T`) | Убери `-t`, добавь `-T` для docker compose |
| `MCP server kaiten already exists` | Сервер уже зарегистрирован | `claude mcp remove kaiten` и зарегистрируй заново |

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Да | Поддомен компании (`mycompany` для `mycompany.kaiten.ru`) |
| `KAITEN_TOKEN` | Да | API-токен из настроек пользователя Kaiten |

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
- **405 Method Not Allowed**: некоторые эндпойнты (get_webhook, delete_sprint, list_removed_*) могут быть недоступны на определённых тарифах Kaiten.
- **Типы ID**: большинство сущностей используют числовые ID. Документы, группы документов, автоматизации и проекты — UUID строки.

## Тесты (для разработки)

Тесты запускаются **только в Docker**:

```bash
# Все тесты (100% покрытие)
docker compose -f tests/docker-compose.test.yml up --build test-overseer

# E2E-тесты (нужен .env с реальными KAITEN_DOMAIN и KAITEN_TOKEN)
docker compose -f tests/docker-compose.test.yml up --build test-e2e-expanded
```

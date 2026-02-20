# kaiten-mcp

MCP-сервер для [Kaiten](https://kaiten.ru) — предоставляет 246 инструментов для работы с Kaiten API через протокол [Model Context Protocol](https://modelcontextprotocol.io).

## Возможности

| Область | Модуль | Кол-во |
|---------|--------|--------|
| Карточки | `cards` | 8 |
| Комментарии | `comments` | 4 |
| Участники карточек | `members` | 5 |
| Логи времени | `time_logs` | 4 |
| Теги | `tags` | 6 |
| Чеклисты | `checklists` | 8 |
| Блокировки | `blockers` | 5 |
| Связи карточек | `card_relations` | 9 |
| Внешние ссылки | `external_links` | 4 |
| Файлы карточек | `files` | 4 |
| Подписчики | `subscribers` | 6 |
| Пространства | `spaces` | 5 |
| Доски | `boards` | 5 |
| Колонки и подколонки | `columns` | 8 |
| Дорожки | `lanes` | 4 |
| Типы карточек | `card_types` | 5 |
| Кастомные свойства | `custom_properties` | 10 |
| Документы | `documents` | 10 |
| Вебхуки | `webhooks` | 9 |
| Автоматизации и воркфлоу | `automations` | 11 |
| Проекты и спринты | `projects` | 13 |
| Роли и группы | `roles_and_groups` | 14 |
| Аудит и аналитика | `audit_and_analytics` | 11 |
| Service Desk | `service_desk` | 47 |
| Графики и аналитика | `charts` | 15 |
| Дерево сущностей | `tree` | 2 |
| Утилиты | `utilities` | 14 |
| **Итого** | **27 модулей** | **246** |

## Требования

- Docker **или** Python >= 3.11
- Аккаунт Kaiten с API-токеном

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `KAITEN_DOMAIN` | Да | Поддомен компании (`yourcompany` для `yourcompany.kaiten.ru`) |
| `KAITEN_TOKEN` | Да | API-токен из настроек пользователя Kaiten |

## Подключение к Claude Code

### Способ 1: Docker (рекомендуется)

Собрать образ (однократно):

```bash
docker build -t kaiten-mcp .
```

Зарегистрировать MCP-сервер:

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -- docker run --rm -i -e KAITEN_DOMAIN -e KAITEN_TOKEN kaiten-mcp
```

Перезапустить Claude Code (`/exit` и запустить заново) — 246 инструментов Kaiten станут доступны.

### Способ 2: Python (venv)

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
claude mcp add kaiten \
  -e KAITEN_DOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -- .venv/bin/kaiten-mcp
```

Перезапустить Claude Code.

### Способ 3: Docker Compose

```bash
claude mcp add kaiten \
  -e KAITEN_DOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -- docker compose --project-directory /path/to/kaiten-mcp run --rm -T kaiten-mcp
```

Замените `/path/to/kaiten-mcp` на абсолютный путь к репозиторию.

> **Важно:** Используйте `--project-directory`, а не `-f`. Флаг `-f` задаёт только путь к yml-файлу, но build context и `.env` всё равно ищутся относительно CWD. Флаг `-T` обязателен — без него Docker выделяет pseudo-TTY, что ломает JSON-RPC протокол MCP.

### Проверка

```bash
claude mcp list
```

Сервер `kaiten` должен быть со статусом `connected`.

## Подключение к Claude Desktop

Добавьте в `claude_desktop_config.json`:

**Docker:**

```json
{
  "mcpServers": {
    "kaiten": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "KAITEN_DOMAIN", "-e", "KAITEN_TOKEN", "kaiten-mcp"],
      "env": {
        "KAITEN_DOMAIN": "yourcompany",
        "KAITEN_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Python:**

```json
{
  "mcpServers": {
    "kaiten": {
      "command": "/path/to/kaiten-mcp/.venv/bin/kaiten-mcp",
      "env": {
        "KAITEN_DOMAIN": "yourcompany",
        "KAITEN_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Важные замечания о Docker и MCP

MCP использует stdio transport (JSON-RPC через stdin/stdout). При запуске через Docker:

- Флаг `-i` (`--interactive`) — **обязателен**, держит stdin открытым.
- Флаг `-t` (`--tty`) — **запрещён**, TTY-символы ломают протокол.
- Для `docker compose run` — используйте `-T` (отключает TTY).
- `.env` файл **не нужен** — переменные передаются через `-e` флаги.

## Структура проекта

```
src/kaiten_mcp/
  server.py              # MCP-сервер (stdio transport)
  client.py              # HTTP-клиент Kaiten API (httpx, rate limiting)
  models.py              # Доменные перечисления
  tools/
    compact.py           # Компактификация ответов (аватары, лимиты)
    spaces.py            # Пространства
    boards.py            # Доски
    columns.py           # Колонки и подколонки
    lanes.py             # Дорожки (swimlanes)
    cards.py             # Карточки (включая bulk-листинг с авто-пагинацией)
    comments.py          # Комментарии
    members.py           # Участники и пользователи
    time_logs.py         # Логи времени
    tags.py              # Теги
    card_types.py        # Типы карточек
    custom_properties.py # Кастомные свойства
    checklists.py        # Чеклисты и элементы
    blockers.py          # Блокировки карточек
    card_relations.py    # Связи parent/child/planned
    external_links.py    # Внешние ссылки
    files.py             # Файлы карточек (загрузка, скачивание, удаление)
    subscribers.py       # Подписчики карточек
    documents.py         # Документы и группы документов
    webhooks.py          # Вебхуки пространств
    automations.py       # Автоматизации и воркфлоу
    projects.py          # Проекты и спринты
    roles_and_groups.py  # Роли, группы, участники пространств
    audit_and_analytics.py # Аудит, активность, сохранённые фильтры
    service_desk.py      # Service Desk (SLA, пользователи, статистика)
    charts.py            # Графики (CFD, control, cycle/lead time, throughput)
    tree.py              # Навигация по дереву сущностей
    utilities.py         # API-ключи, таймеры, календари, корзина
```

## API-клиент

- Базовый URL: `https://{domain}.kaiten.ru/api/latest`
- Авторизация: `Bearer` токен
- Rate limiting: 4.5 запросов/сек (серверный лимит — 5 req/s)
- Автоматический retry при HTTP 429 с exponential backoff (до 3 попыток)

## Тесты

Тесты запускаются **только в Docker**:

```bash
# Все тесты с проверкой 100% покрытия
docker compose -f tests/docker-compose.test.yml up --build test-overseer

# E2E-тесты (нужен .env с KAITEN_DOMAIN и KAITEN_TOKEN)
docker compose -f tests/docker-compose.test.yml up --build test-e2e-expanded
```

## Лицензия

MIT

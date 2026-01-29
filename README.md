# kaiten-mcp

MCP-сервер для [Kaiten](https://kaiten.ru) — предоставляет 178 инструментов для работы с Kaiten API через протокол [Model Context Protocol](https://modelcontextprotocol.io).

## Возможности

| Область | Модуль | Кол-во |
|---------|--------|--------|
| Карточки | `cards` | 7 |
| Комментарии | `comments` | 4 |
| Участники карточек | `members` | 5 |
| Логи времени | `time_logs` | 4 |
| Теги | `tags` | 5 |
| Чеклисты | `checklists` | 8 |
| Блокировки | `blockers` | 5 |
| Связи карточек | `card_relations` | 6 |
| Внешние ссылки | `external_links` | 4 |
| Подписчики | `subscribers` | 10 |
| Пространства | `spaces` | 5 |
| Доски | `boards` | 5 |
| Колонки | `columns` | 4 |
| Дорожки | `lanes` | 4 |
| Типы карточек | `card_types` | 5 |
| Кастомные свойства | `custom_properties` | 7 |
| Документы | `documents` | 10 |
| Вебхуки | `webhooks` | 5 |
| Автоматизации и воркфлоу | `automations` | 10 |
| Проекты и спринты | `projects` | 13 |
| Роли и группы | `roles_and_groups` | 14 |
| Аудит и аналитика | `audit_and_analytics` | 10 |
| Service Desk | `service_desk` | 14 |
| Утилиты | `utilities` | 14 |
| **Итого** | **24 модуля** | **178** |

## Требования

- Python >= 3.11
- Аккаунт Kaiten с API-токеном

## Установка и запуск

### Docker Compose (рекомендуется)

1. Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

```env
KAITEN_DOMAIN=yourcompany
KAITEN_TOKEN=your-api-token
```

`KAITEN_DOMAIN` — поддомен вашей компании (`yourcompany` для `yourcompany.kaiten.ru`).

2. Запустите:

```bash
docker compose up --build
```

### Локально

```bash
pip install -e .
kaiten-mcp
```

Переменные окружения `KAITEN_DOMAIN` и `KAITEN_TOKEN` должны быть установлены.

## Подключение к Claude Desktop

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kaiten": {
      "command": "docker",
      "args": ["compose", "-f", "/path/to/kaiten-mcp/docker-compose.yml", "run", "--rm", "kaiten-mcp"],
      "env": {
        "KAITEN_DOMAIN": "yourcompany",
        "KAITEN_TOKEN": "your-api-token"
      }
    }
  }
}
```

Или без Docker:

```json
{
  "mcpServers": {
    "kaiten": {
      "command": "kaiten-mcp",
      "env": {
        "KAITEN_DOMAIN": "yourcompany",
        "KAITEN_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Подключение к Claude Code

```bash
claude mcp add kaiten -- kaiten-mcp
```

Или с Docker:

```bash
claude mcp add kaiten -- docker compose -f /path/to/kaiten-mcp/docker-compose.yml run --rm kaiten-mcp
```

## Структура проекта

```
src/kaiten_mcp/
  server.py              # MCP-сервер (stdio transport)
  client.py              # HTTP-клиент Kaiten API (httpx, rate limiting)
  models.py              # Доменные перечисления
  tools/
    spaces.py            # Пространства
    boards.py            # Доски
    columns.py           # Колонки
    lanes.py             # Дорожки (swimlanes)
    cards.py             # Карточки
    comments.py          # Комментарии
    members.py           # Участники и пользователи
    time_logs.py         # Логи времени
    tags.py              # Теги
    card_types.py        # Типы карточек
    custom_properties.py # Кастомные свойства
    checklists.py        # Чеклисты и элементы
    blockers.py          # Блокировки карточек
    card_relations.py    # Связи parent/child
    external_links.py    # Внешние ссылки
    subscribers.py       # Подписчики + подколонки
    documents.py         # Документы и группы документов
    webhooks.py          # Вебхуки пространств
    automations.py       # Автоматизации и воркфлоу
    projects.py          # Проекты и спринты
    roles_and_groups.py  # Роли, группы, участники пространств
    audit_and_analytics.py # Аудит, активность, сохранённые фильтры
    service_desk.py      # Service Desk
    utilities.py         # API-ключи, таймеры, календари, корзина
```

## API-клиент

- Базовый URL: `https://{domain}.kaiten.ru/api/latest`
- Авторизация: `Bearer` токен
- Rate limiting: 4.5 запросов/сек (серверный лимит — 5 req/s)
- Автоматический retry при HTTP 429 с exponential backoff (до 3 попыток)

## Лицензия

MIT

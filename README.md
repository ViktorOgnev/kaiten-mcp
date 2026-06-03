# kaiten-mcp

MCP-сервер для [Kaiten](https://kaiten.ru) — предоставляет 246 инструментов для работы с Kaiten API через протокол [Model Context Protocol](https://modelcontextprotocol.io).

Поддерживает два transport-а:
- `stdio` для локального подключения из Claude Code / Claude Desktop
- `HTTP` для удалённого deployment-а в Docker

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
| `KAITEN_SUBDOMAIN` | Да* | Поддомен компании (`yourcompany` для `yourcompany.kaiten.ru`) |
| `KAITEN_BASE_DOMAIN` | Нет | Базовый домен, по умолчанию `kaiten.ru` |
| `KAITEN_BASE_URL` | Нет | Полный override URL API-хоста; имеет приоритет над `KAITEN_SUBDOMAIN`/`KAITEN_BASE_DOMAIN` |
| `KAITEN_DOMAIN` | Нет | Устаревший fallback для обратной совместимости вместо `KAITEN_SUBDOMAIN` |
| `KAITEN_TOKEN` | Да | API-токен из настроек пользователя Kaiten |
| `MCP_HTTP_HOST` | Нет | Хост для HTTP transport (по умолчанию `0.0.0.0`) |
| `MCP_HTTP_PORT` | Нет | Порт для HTTP transport (по умолчанию `8000`) |
| `MCP_HTTP_BASE_PATH` | Нет | Базовый путь HTTP transport (по умолчанию `/mcp`) |
| `MCP_AUTH_TOKEN` | Нет | Bearer token для защиты удалённого HTTP endpoint |

Заполняйте `KAITEN_TOKEN` и ровно один способ настройки хоста:
- `KAITEN_SUBDOMAIN` для обычного `*.kaiten.ru`
- `KAITEN_SUBDOMAIN` + `KAITEN_BASE_DOMAIN` для кастомного домена
- `KAITEN_BASE_URL` для полного override

`KAITEN_BASE_URL` нужен для нестандартных доменов и стендов. Примеры:
- `KAITEN_SUBDOMAIN=yourcompany` -> `https://yourcompany.kaiten.ru/api/latest`
- `KAITEN_SUBDOMAIN=kaiten` + `KAITEN_BASE_DOMAIN=kaiten.ru` -> `https://kaiten.kaiten.ru/api/latest`
- `KAITEN_BASE_URL=https://kaiten.kaiten.ru` -> `https://kaiten.kaiten.ru/api/latest`

Для локального запуска через Python сервер читает `.env` через `load_dotenv()`. Переменные процесса имеют приоритет над `.env`.

Быстрый старт с `.env`:

```bash
cp .env.example .env
```

Потом откройте `.env` и оставьте только подходящий вам вариант host-конфига.

## Подключение к Claude Code

Ниже описан локальный `stdio` режим. Он сохранён и работает как раньше.

### Способ 1: Docker (рекомендуется)

Собрать образ (однократно):

```bash
docker build -t kaiten-mcp .
```

Эта команда по умолчанию собирает локальный `stdio`-образ. Для удалённого HTTP transport используйте отдельный target `baked-http`.

Зарегистрировать MCP-сервер:

```bash
claude mcp add kaiten \
  -e KAITEN_SUBDOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -- docker run --rm -i -e KAITEN_SUBDOMAIN -e KAITEN_TOKEN kaiten-mcp
```

Перезапустить Claude Code (`/exit` и запустить заново) — 246 инструментов Kaiten станут доступны.

Для нестандартного домена добавьте `KAITEN_BASE_DOMAIN` или `KAITEN_BASE_URL`:

```bash
claude mcp add kaiten \
  -e KAITEN_SUBDOMAIN=kaiten \
  -e KAITEN_BASE_DOMAIN=kaiten.ru \
  -e KAITEN_TOKEN=your-api-token \
  -- docker run --rm -i \
     -e KAITEN_SUBDOMAIN -e KAITEN_BASE_DOMAIN -e KAITEN_TOKEN kaiten-mcp
```

### Способ 2: Python (venv)

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
claude mcp add kaiten \
  -e KAITEN_SUBDOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -- .venv/bin/kaiten-mcp
```

Перезапустить Claude Code.

### Способ 3: Docker Compose

```bash
claude mcp add kaiten \
  -e KAITEN_SUBDOMAIN=yourcompany \
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
      "args": ["run", "--rm", "-i", "-e", "KAITEN_SUBDOMAIN", "-e", "KAITEN_TOKEN", "kaiten-mcp"],
      "env": {
        "KAITEN_SUBDOMAIN": "yourcompany",
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
        "KAITEN_SUBDOMAIN": "yourcompany",
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
- Если используете `KAITEN_BASE_DOMAIN` или `KAITEN_BASE_URL`, их тоже нужно пробросить через `-e`.

Для удалённого deployment-а есть отдельный HTTP transport. Он не требует `-i`/`-T`, потому что работает как обычный web-service.

## Удалённый HTTP deployment

HTTP transport запускается отдельно и не заменяет локальный `stdio`.

### Способ 1: Docker Compose

```bash
docker compose --profile http --project-directory /path/to/kaiten-mcp up --build -d kaiten-mcp-http
```

Проверка:

```bash
curl http://127.0.0.1:8000/readyz
```

Если задан `MCP_AUTH_TOKEN`, клиент должен передавать:

```http
Authorization: Bearer <token>
```

MCP endpoint по умолчанию публикуется на:

```text
http://127.0.0.1:8000/mcp
```

### Способ 2: Docker run

```bash
docker build --target baked-http -t kaiten-mcp-http:latest .
docker run --rm \
  --read-only --tmpfs /tmp:noexec,nosuid,size=64m \
  --security-opt=no-new-privileges:true --cap-drop=ALL \
  -p 8000:8000 \
  -e KAITEN_SUBDOMAIN=yourcompany \
  -e KAITEN_TOKEN=your-api-token \
  -e MCP_AUTH_TOKEN=your-http-token \
  -e MCP_HTTP_HOST=0.0.0.0 \
  -e MCP_HTTP_PORT=8000 \
  -e MCP_HTTP_BASE_PATH=/mcp \
  kaiten-mcp-http:latest
```

Для нестандартного домена в HTTP-режиме можно так же пробросить `KAITEN_BASE_DOMAIN`
или `KAITEN_BASE_URL`.

### Важно для production

- Не публикуйте HTTP endpoint без `MCP_AUTH_TOKEN` или внешней reverse proxy-аутентификации.
- Для интернета лучше ставить сервис за Nginx, Caddy, Tailscale или VPN.
- Локальный `stdio` режим для Claude Code и Claude Desktop остаётся предпочтительным, если удалённый deployment не нужен.
- `GET /healthz` проверяет liveness процесса, `GET /readyz` проверяет готовность конфигурации сервиса.

## Структура проекта

```
src/kaiten_mcp/
  runtime.py             # Общая MCP runtime-логика для stdio и HTTP
  server.py              # MCP-сервер (stdio transport)
  http_server.py         # MCP-сервер (streamable HTTP transport)
  client.py              # HTTP-клиент Kaiten API (httpx, rate limiting)
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

- Базовый URL:
  - по умолчанию: `https://{subdomain}.kaiten.ru/api/latest`
  - c кастомным base domain: `https://{subdomain}.{base_domain}/api/latest`
  - при `KAITEN_BASE_URL`: override нормализуется до `.../api/latest`
- Авторизация: `Bearer` токен
- Rate limiting: 4.5 запросов/сек (серверный лимит — 5 req/s)
- Автоматический retry при HTTP 429 с exponential backoff (до 3 попыток)

## Тесты

Тесты запускаются **только в Docker**:

```bash
# Все тесты с проверкой 100% покрытия
docker compose -f tests/docker-compose.test.yml up --build test-overseer

# E2E-тесты (нужен .env с KAITEN_SUBDOMAIN/KAITEN_BASE_URL и KAITEN_TOKEN)
docker compose -f tests/docker-compose.test.yml up --build test-e2e-expanded
```

## Лицензия

MIT

## Автор 

Виктор Огнев

## Дисклеймер

Настоящий репозиторий и размещённое в нём программное обеспечение предоставляются по принципу “как есть” (“as is”) и “по мере доступности” (“as available”), без каких-либо гарантий, явных или подразумеваемых. Автор не предоставляет никаких заверений и гарантий в отношении корректности, надёжности, безопасности, пригодности для конкретных целей или отсутствия ошибок в данном решении.

Используя данный программный продукт, вы подтверждаете, что принимаете на себя все риски, связанные с его использованием, включая, но не ограничиваясь, прямыми, косвенными, случайными или последующими убытками.

Автор настоящего репозитория является единственным разработчиком и правообладателем данного кода. Данное решение разработано и распространяется независимо и не является официальным продуктом или услугой компании Kaiten Software.

Компания Kaiten Software не несёт никакой ответственности за качество работы, производительность, результаты использования или любые последствия, связанные с использованием данного решения. Любые упоминания Kaiten Software приведены исключительно в информационных целях и не означают одобрения, поддержки или аффилированности.

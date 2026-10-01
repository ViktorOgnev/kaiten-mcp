# Column and subcolumn acceptance tests

These tests cover the shared request-body helper and validation of column/subcolumn
updates. `test_body.py`, `test_layer2_handlers/test_columns.py` and
`test_columns_mcp.py` exercise helper, handler and in-process MCP behavior.

`test_columns_stdio.py` adds 24 black-box cases against an actual MCP subprocess:

- Both update tools reject ID-only requests, unknown fields, mixed known/unknown
  fields, null, string and boolean WIP limits. The local HTTP recorder must receive
  **zero requests** for each rejected call.
- All four create/update tools send the exact HTTP method, path and body for minimal
  arguments, zero WIP/sort order and all supported fields. Routing IDs stay out of
  the body.

## Run without Docker

Install the project with its test dependencies into a virtual environment, then:

```sh
python -m pytest tests/test_columns_stdio.py -v --timeout=60
```

No Kaiten account is needed. The MCP server is started with the test interpreter
and uses a local HTTP fixture and a dummy token.

## Run the same cases against Docker

```sh
docker build --target baked-stdio -t kaiten-mcp:columns-test .
KAITEN_TEST_DOCKER_IMAGE=kaiten-mcp:columns-test \
  python -m pytest tests/test_columns_stdio.py -v --timeout=60
```

The test runner stays on the host; the MCP application runs from the baked image,
without a source mount, with a read-only filesystem and temporary `/tmp`.
Docker cases require Linux host networking (including a Docker engine in WSL),
so the server can reach the loopback HTTP fixture. Docker is not required for the
default test suite.

## Opt-in live Kaiten tests

Provide `KAITEN_TOKEN` and `KAITEN_BASE_URL` or `KAITEN_SUBDOMAIN` through your
normal secret-loading mechanism. Set `KAITEN_COLUMNS_TEST_SPACE_ID` to a test space
where creating and deleting temporary boards is permitted. Do not commit tokens.

```sh
KAITEN_COLUMNS_E2E=1 python -m pytest tests/test_columns_live.py -v -rx --timeout=180
KAITEN_COLUMNS_E2E=1 KAITEN_TEST_DOCKER_IMAGE=kaiten-mcp:columns-test \
  python -m pytest tests/test_columns_live.py -v -rx --timeout=180
```

These eight cases create their own uniquely named boards. Each case removes its
board in `finally`, checks ownership before force deletion, then verifies absence
from the space. Cleanup uses the API directly because the existing delete-board
MCP tool does not expose the required `force` parameter. Existing boards and cards
are not modified. Abrupt process termination cannot guarantee cleanup; JUnit
properties record created board IDs and successful cleanup for recovery:

```sh
KAITEN_COLUMNS_E2E=1 python -m pytest tests/test_columns_live.py -v \
  -o junit_family=legacy --junitxml=columns-live.xml
```

The live cases verify rejection without changing persisted state, successful
rename with unrelated WIP preserved, creation with WIP 0/5, and updates 5 → 0.
State is verified with separate list requests, not only mutation responses.

### Known Kaiten subcolumn WIP limitation

On the tested service, subcolumn POST ignores `wip_limit` (both 0 and 5 read back
as null), and WIP-only PATCH returns HTTP 400. This was also reproduced directly
through the API without MCP. The exact outgoing bodies remain covered by the
passing stdio contract tests. This behavior predates the request-body refactor.

Three live subcolumn WIP cases are marked strict `xfail`: they expose this known
limitation rather than claiming persistence works. Unexpected success fails the
run so the marker can be removed when the behavior is fixed. Assertions occur
after cleanup; transport and cleanup exceptions are not expected failures.
Live validation/rename tests for subcolumns run normally. The expected current
result is **5 passed, 3 xfailed** in each runtime; xfailed is not PASS.

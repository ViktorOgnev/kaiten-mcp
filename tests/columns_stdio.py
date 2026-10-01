"""Launch the same MCP contract tests against Python or a baked Docker image."""

import json
import os
import sys
from contextlib import asynccontextmanager
from datetime import timedelta

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HOST_KEYS = ("KAITEN_BASE_URL", "KAITEN_SUBDOMAIN", "KAITEN_DOMAIN", "KAITEN_TOKEN")


@asynccontextmanager
async def column_session(env):
    image = os.environ.get("KAITEN_TEST_DOCKER_IMAGE")
    if image:
        # Linux Docker host networking lets the container reach the local HTTP fixture.
        args = ["run", "--rm", "-i", "--network", "host", "--read-only", "--tmpfs", "/tmp"]
        for key in env:
            args.extend(["--env", key])  # Values stay in the environment, not argv.
        params = StdioServerParameters(command="docker", args=[*args, image], env=env)
    else:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-c", "from kaiten_mcp.server import main; main()"],
            env=env,
        )
    with open(os.devnull, "w") as errors:  # noqa: ASYNC230 -- immediate null-device open
        async with (
            stdio_client(params, errlog=errors) as (reader, writer),
            ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=45)) as session,
        ):
            await session.initialize()
            yield session


async def call_json(session, name, args):
    result = await session.call_tool(name, args)
    text = " ".join(c.text for c in result.content if c.type == "text")
    assert not result.isError, f"{name}: {text}"
    # Large lists may be followed by the runtime's informational footer.
    return json.JSONDecoder().raw_decode(text)[0]

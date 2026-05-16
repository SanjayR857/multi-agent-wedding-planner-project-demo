from multiprocessing.connection import Client
import asyncio
from langchain_mcp_adapters import MultiprocessMCPServer
from mcp.shared.exceptions import McpError
from mcp.types import CallToolResult, TextContent

RETRYABLE_MCP_CODES = {-32603}


class RetryMCPInterceptor:
    """
    Intercept MCp tool calls: retry transient failure, surface all errora gracefully.

    - Retryable errors: internal server error (-32603)
    - No retry on invalid params, invalid tool name, cancelled calls, etc.
    - Max 3 retries with 1s exponential backoff

    This class implements the interceptor interface required by LangChain MCP client.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def __call__(self, request, handler):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await handler(request)
            except McpError as exc:
                last_error = exc
                print(
                    f"[MCP interceptor] {type(exc).__name__} on {request.name} "
                    f"(code {exc.error.code}, attempt {attempt + 1}/{self.max_retries}): {exc}"
                )

                if exc.error.code not in RETRYABLE_MCP_CODES:
                    return CallToolResult(
                        content=[
                            TextContent(
                                text=f"Tool call failed (non- retryable): {exc.error.message}"
                            )
                        ],
                        isError=False,
                    )
            except Exception as exc:
                last_error = exc
                print(
                    f"[MCP interceptor] {type(exc).__name__} on {request.name} "
                    f"(attempt {attempt + 1}/{self.max_retries}): {exc}"
                )

            if attempt + 1 < self.max_retries:
                await asyncio.sleep(1 * (2**attempt))  # exponential backoff 1, 2, 4s

        print
        return CallToolResult(
            content=[
                TextContent(
                    text=f"Tool call failed after {self.max_retries} attempts: {last_error}"
                )
            ],
            isError=True,
        )


Client = MultiprocessMCPServer(
    {
        "travel_server": {
            "transport": "streamable_http",
            "url": "https://mcp.kiwi.com",
        },
    },
    tool_interceptors=[RetryMCPInterceptor()],
)


async def get_tools():
    tools = await Client.get_tools()
    print("available tools:")
    print(tools)
    return tools

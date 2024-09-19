from dotenv import load_dotenv

load_dotenv()

from integration_agent.main import call_agent
import os
from typing import List
import asyncio
import click


async def main() -> str:
    await call_agent("./robinhood.har")


if __name__ == "__main__":
    asyncio.run(main())

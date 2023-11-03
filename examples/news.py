from malar import Api
from rich.console import Console


import asyncio


console = Console()


async def main() -> None:
    outages = await Api.News.current_outages()

    console.log(outages)


if __name__ == "__main__":
    asyncio.run(main())


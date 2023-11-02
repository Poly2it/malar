from malar import Api, Sector
from datetime import datetime, timedelta
from rich.console import Console


import asyncio


console = Console()


async def main() -> None:
    cache = await Api.Json.Pricing.recent(
        sector = Sector.SE1,
    )

    recent_pricing  = await Api.Pricing.recent(
        sector = Sector.SE1,
        start  = datetime.now() - timedelta(days = 1),
        end    = datetime.now(),
        cache  = cache,
    )
    current_pricing = await Api.Pricing.current(
        sector = Sector.SE1,
        cache  = cache,
    )

    console.log(recent_pricing)
    console.log(current_pricing)


if __name__ == "__main__":
    asyncio.run(main())


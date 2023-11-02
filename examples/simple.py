from malar import Api, Sector
import asyncio


async def main():
    print(await Api.Pricing.recent(Sector.SE1))
    print(await Api.Pricing.current(Sector.SE1))


if __name__ == "__main__":
    asyncio.run(main())


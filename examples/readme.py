from malar import Api, Sector
import asyncio


async def main():
    price = await Api.Pricing.current(Sector.SE1)
    print(f"The energy price in öre/kWh for sector SE1 is {price[2]}")


if __name__ == "__main__":
    asyncio.run(main())


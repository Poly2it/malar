# Malar
Malar is an asynchronous wrapper for the Mälarenergi API. It can be used for reading
energy pricing data in different energy sectors in Sweden.

## Usage
`./install`

```py
from malar import Api, Sector
import asyncio


async def main():
    _, _, price = await Api.Pricing.current(Sector.SE1)
    print(f"The energy price in öre/kWh for sector SE1 is {price}")


if __name__ == "__main__":
    asyncio.run(main())

```

```
The energy price in öre/kWh for sector SE1 is 41.97
```

---

<img src="docs/lgpl.svg" alt="drawing" width="200" align="right"/>

This project and its contributors are in no way assoicated with Mälarenergi AB or any of
their associates. Their name is used in this project for attribution and illustrative
purposes, such as clearly displaying the origin of the data available with this API 
wrapper.


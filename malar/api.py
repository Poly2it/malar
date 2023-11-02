from typing import List, Tuple, Union, TypedDict
from datetime import datetime


from .common import Sector


import httpx


class Types:
    class Json:
        class Interval(TypedDict):
            interval: str
            startDateTime: str
            endDateTime:   str
            price: int

        class Historical(TypedDict):
            version: str

            area: str

            unit: str
            currency: str

            average:  float
            current:  "Types.Json.Interval"
            todayMin: "Types.Json.Interval"
            todayMax: "Types.Json.Interval"

            hasTomorrow: bool

            intervals: List["Types.Json.Interval"]


class Api:
    class Json:
        class Pricing:
            @staticmethod
            async def recent(
                sector: Sector,
                *,
                client: httpx.AsyncClient = httpx.AsyncClient(),
            ) -> Types.Json.Historical:
                """
                Returns JSON data about various subjects on recent pricing information.

                Parameters:
                    sector: The energy sector. Energy sectors split the Swedish 
                            territory in four sectors used when deciding local pricing.
                    client: An httpx async compatible client.

                Returns:
                    Types.Json.Historical: All JSON fields.
                """

                HOST = f"https://bff.malarenergi.se/spotpriser/api/v1/prices/area/{sector}"
                
                async with client:
                    response = await client.get(HOST)

                return response.json()

    class Pricing:
        @staticmethod
        async def current(
            sector: Sector,
            *,
            cache: Union[None, Types.Json.Historical] = None,
            client: httpx.AsyncClient = httpx.AsyncClient(),
        ):
            """
            Returns the current pricing information in öre/kWh.

            Parameters:
                sector: The energy sector. Energy sectors split the Swedish territory in
                        four sectors used when deciding local pricing.
                cache:  A cached JSON request value.
                client: An httpx async compatible client.

            Returns:
                Tuple[
                    datetime: start time
                    datetime: end time
                    int:      price
                ]
            """

            if cache == None:
                response = await Api.Json.Pricing.recent(sector, client = client)
            else:
                response = cache

            interval_start = datetime.fromisoformat(
                response["current"]["startDateTime"]
            ).replace(tzinfo=None)
            interval_end   = datetime.fromisoformat(
                response["current"]["endDateTime"]
            ).replace(tzinfo=None)
            interval_price = response["current"]["price"]

            return (
                interval_start,
                interval_end,
                interval_price,
            )

        @staticmethod
        async def recent(
            sector: Sector,
            start: datetime = datetime.min, 
            end:   datetime = datetime.max, 
            *,
            cache: Union[None, Types.Json.Historical] = None,
            client: httpx.AsyncClient = httpx.AsyncClient(),
        ) -> List[Tuple[datetime, datetime, int]]:
            """
            Returns recent pricing information in öre/kWh.

            Parameters:
                sector: The energy sector. Energy sectors split the Swedish territory in
                        four sectors used when deciding local pricing.
                start:  The earliest possible date of a returned value.
                end:    The last possible date of a returned value.
                cache:  A cached JSON request value.
                client: An httpx async compatible client.

            Returns:
                List[
                    Tuple[
                        datetime: start time
                        datetime: end time
                        int:      price
                    ]
                ]
            """
 
            if cache == None:
                response = await Api.Json.Pricing.recent(sector, client = client)
            else:
                response = cache
            
            intervals = []
            for interval in response["intervals"]:
                interval_start = datetime.fromisoformat(
                    interval["startDateTime"]
                ).replace(tzinfo=None)
                interval_end   = datetime.fromisoformat(
                    interval["endDateTime"]
                ).replace(tzinfo=None)
                interval_value = int(interval["price"])

                if interval_start >= start and interval_end <= end:
                    intervals.append([interval_start, interval_end, interval_value])

            return intervals


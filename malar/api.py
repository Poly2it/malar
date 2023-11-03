from typing import List, Tuple, Union, TypedDict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup, Comment, Tag


from .common import Sector, Service, Status


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

                HOST = f"https://bff.malarenergi.se/spotpriser/api/v1/prices/area/{sector.name}"
                
                async with client:
                    response = await client.get(HOST)

                return response.json()
    
    class Html:
        class News:
            @staticmethod
            async def interruptions(
                *,
                client: httpx.AsyncClient = httpx.AsyncClient(),
            ) -> BeautifulSoup:
                """
                Returns HTML data in the form of a soup about service interruptions.
                Cleans the site of unnecessary data.

                Parameters:
                    client: An httpx async compatible client.

                Returns:
                    BeautifulSoup: A site soup.
                """

                HOST = "https://www.malarenergi.se/avbrott/"
                async with client:
                    response = await client.get(HOST)

                soup = BeautifulSoup(response.text, features="html.parser")
                comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    comment.extract()

                assert (html := soup.html) != None

                destructables = [
                    *[match for name in [
                        "head",
                        "header",
                        "script",
                        "noscript",
                        "iframe",
                        "img",
                        "path",
                    ] for match in html.find_all(name)],
                    *[match for name in [
                        # general navigation
                        "user-functions-nav__node",
                        "user-functions-nav__link",
                        "user-functions-nav",
                        # assorted information
                        "htmlblock",
                        # placeholders
                        "icon-placeholder",
                        # social pages
                        "social-lang-nav__node",
                        "social-lang-nav__link",
                        # footer
                        "page-footer",
                    ] for match in html.find_all(class_ = name)],
                ]
                for destructable in destructables:
                    destructable.decompose()

                meta_tag = soup.new_tag("meta", charset="utf-8")
                html.insert(0, meta_tag)

                return soup

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
            TIMEZONE = ZoneInfo("Europe/Stockholm")

            if cache == None:
                response = await Api.Json.Pricing.recent(sector, client = client)
            else:
                response = cache

            interval_start = datetime.fromisoformat(
                response["current"]["startDateTime"]
            ).replace(tzinfo=TIMEZONE)
            interval_end   = datetime.fromisoformat(
                response["current"]["endDateTime"]
            ).replace(tzinfo=TIMEZONE)
            interval_price = response["current"]["price"]

            return (
                interval_start,
                interval_end,
                interval_price,
            )

        @staticmethod
        async def recent(
            sector: Sector,
            start: datetime = datetime.min.replace(tzinfo=timezone.utc), 
            end:   datetime = datetime.max.replace(tzinfo=timezone.utc), 
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
            TIMEZONE = ZoneInfo("Europe/Stockholm")

            if cache == None:
                response = await Api.Json.Pricing.recent(sector, client = client)
            else:
                response = cache
            
            intervals = []
            for interval in response["intervals"]:
                interval_start = datetime.fromisoformat(
                    interval["startDateTime"]
                ).replace(tzinfo=TIMEZONE)
                interval_end   = datetime.fromisoformat(
                    interval["endDateTime"]
                ).replace(tzinfo=TIMEZONE)
                interval_value = int(interval["price"])

                if (
                    interval_start.timestamp() >= start.timestamp() and \
                    interval_end.timestamp()   <= end.timestamp()
                ):
                    intervals.append([interval_start, interval_end, interval_value])

            return intervals
    
    class News:
        @staticmethod
        async def current_outages(
            *,
            cache: Union[None, BeautifulSoup] = None,
            client: httpx.AsyncClient = httpx.AsyncClient(),
        ) -> List[Tuple[List[str], Service, datetime, datetime, Status, int]]:
            """
            Returns a list of current outages and data about them. Relies on parsing the
            website and may as such break on some types of website updates.

            Parameters:
                cache:  A cached HTML request value.
                client: An httpx async compatible client.

            Returns:
                List[
                    Tuple[
                        List[str]: names of the affected locations
                        Service:   affected service
                        datetime:  start time
                        datetime:  end time
                        Status:    status of the outage
                        int:       number of affected customers
                    ]
                ]
            """

            if cache == None:
                response = await Api.Html.News.interruptions(client = client)
            else:
                response = cache

            current = response.find(id="pagaende")
            assert isinstance(current, Tag)
            current.extract()

            outages = []
            
            for outage in current.find_all(class_="outageinfo__list-item"):
                SERVICE_ALIAS = {
                    "Vatten": Service.WATER,
                    "Fjärrvärme": Service.DISTRICT_HEATING,
                }
                STATUS_ALIAS = {
                    "Felsökning pågår": Status.UNDER_INVESTIGATION,
                    "Underhåll": Status.UNDER_SERVICE,
                }
                TIMEZONE = ZoneInfo("Europe/Stockholm")

                metadata: Tag = outage.find(
                    class_="outageinfo__list-item--bottom-inner-wrapper"
                ).extract()
                status_string, start_time_string, affected_customers_string, \
                end_time_string = [
                    str(s.string) for s in metadata.find_all("dd")
                ]

                locations: List[str] = outage.find(
                    class_="outageinfo__list-item--header1"
                ).text.split(", ")
                service: Service = SERVICE_ALIAS[outage.find(
                    class_="outageinfo__list-item--header2"
                ).text]
                start_time: datetime = datetime.strptime(
                    start_time_string, "%y-%m-%d %H:%M"
                ).replace(tzinfo=TIMEZONE)
                end_time: datetime   = datetime.strptime(
                    end_time_string,   "%y-%m-%d %H:%M"
                ).replace(tzinfo=TIMEZONE)
                status: Status = STATUS_ALIAS[status_string]
                affected_customers: int = int(affected_customers_string)

                outages.append((
                    locations, 
                    service, 
                    start_time, 
                    end_time, 
                    status, 
                    affected_customers,
                ))
            
            return outages


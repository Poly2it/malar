from typing import List
from malar import Api, Service, Status
from datetime import datetime
from rich.console import Console


import asyncio


console = Console()


SERVICE_STRING = {
    Service.WATER: "A water",
    Service.DISTRICT_HEATING: "A district heating",
    Service.ELECTRICITY: "An electricity",
}

STATUS_STRING = {
    Status.NOMINAL: "The situation is resolved.",
    Status.UNDER_INVESTIGATION: "The situation is under investigation.",
    Status.UNDER_SERVICE: "The affected service is under service.",
    Status.REPARATION_ONGOING: "The affected system is under repair.",
}


def natural_join(list: List[str]):
    return f"{', '.join(list[0:-2])}{' and ' if len(list) > 2 else ''}{list[-1]}"


def natural_quantity(number: int):
    match number:
        case 0:
            return "zero"
        case 1:
            return "one"
        case 2:
            return "two"
        case 3:
            return "three"
        case 4:
            return "four"
        case 5:
            return "five"
        case 6:
            return "six"
        case 7:
            return "seven"
        case 8:
            return "eight"
        case 9:
            return "nine"
        case 10:
            return "ten"
        case 11:
            return "eleven"
        case 12:
            return "twelve"
        case _:
            return str(number)


def natural_timestring(time: datetime):
    current_day = datetime.now().day
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year

    if time.day == current_day + 1:
        time_string = time.strftime("tomorrow %H:%M")
    elif time.day == current_day:
        time_string = time.strftime("%H:%M")
    elif time.day == current_day - 1:
        time_string = time.strftime("yesterday %H:%M")
    elif time.isocalendar()[1] == current_week:
        time_string = time.strftime("%A %H:%M")
    elif time.year == current_year:
        if   time.day % 10 == 1:
            time_string = time.strftime("%H:%M, %B the %-dst")
        elif time.day % 10 == 2:
            time_string = time.strftime("%H:%M, %B the %-dnd")
        elif time.day % 10 == 3:
            time_string = time.strftime("%H:%M, %B the %-drd")
        else:
            time_string = time.strftime("%H:%M, %B the %-dth")
    else:
        if   time.day % 10 == 1:
            time_string = time.strftime("%H:%M, %B the %-dst %Y")
        elif time.day % 10 == 2:
            time_string = time.strftime("%H:%M, %B the %-dnd %Y")
        elif time.day % 10 == 3:
            time_string = time.strftime("%H:%M, %B the %-drd %Y")
        else:
            time_string = time.strftime("%H:%M, %B the %-dth %Y")

    return time_string


def natural_timedelta(start: datetime, end: datetime):
    start_string = natural_timestring(start)
    if start.day == end.day:
        end_string = end.strftime("%H:%M")
    else:
        end_string = natural_timestring(end)

    return (start_string, end_string)


async def main() -> None:
    outages = await Api.News.current_outages()

    for outage in outages:
        locations, service, start, end, status, customers = outage
        parts = []
        parts.append(SERVICE_STRING[service])
        if end is None:
            parts.append(" interruption has been affecting ")
        else:
            parts.append(" interruption is affecting ")
        parts.append(natural_quantity(customers))
        if customers > 1:
            parts.append(" customers")
        else:
            parts.append(" customer")
        parts.append(" in ")
        parts.append(natural_join(locations))
        if end is None:
            parts.append(" since ")
            parts.append(natural_timestring(start))
        else:
            start_string, end_string = natural_timedelta(start, end)
            parts.append(" since ")
            parts.append(start_string)
            parts.append(" and is estimated to end ")
            parts.append(end_string)
        parts.append(". ")
        parts.append(STATUS_STRING[status])

        print("".join(parts))


if __name__ == "__main__":
    asyncio.run(main())


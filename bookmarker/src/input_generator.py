import csv
from typing import Iterator

from pyluach import parshios
from pyluach.dates import HebrewDate
from pyluach.parshios import PARSHIOS_HEBREW
from src.utils import Row


class HebrewCalendar:
    def __init__(
        self,
        start_date: HebrewDate,
        end_date: HebrewDate,
        /,
        major_holidays: bool = True,
        minor_holidays: bool = False,
        extra_holidays: bool = True,
    ):
        self._date_info = list(
            self._generate_hebrew_dates(
                start_date,
                end_date,
                major_holidays=major_holidays,
                minor_holidays=minor_holidays,
                extra_holidays=extra_holidays,
            )
        )

    @staticmethod
    def _get_yom_haatzmaut(year: int) -> HebrewDate:
        date = HebrewDate(year=year, month=2, day=5)
        match date.weekday():
            case 6:
                return date.subtract(days=1)
            case 7:
                return date.subtract(days=2)
            case 2:
                return date.add(days=1)
            case _:
                return date

    @staticmethod
    def _get_extra_holiday(date: HebrewDate) -> str | None:
        purim = date.replace(month=1, day=14).subtract(months=1)
        yom_haatzmaut = HebrewCalendar._get_yom_haatzmaut(date.year)
        tishaa_beav = date.replace(month=5, day=9)
        holidays = (purim, tishaa_beav)
        if date in holidays:
            return date.holiday(israel=True, hebrew=True)
        if date == yom_haatzmaut:
            return "יום העצמאות"

        return None

    def _generate_hebrew_dates(
        self,
        current_date: HebrewDate,
        end_date: HebrewDate,
        /,
        major_holidays: bool = True,
        minor_holidays: bool = False,
        extra_holidays: bool = True,
    ):
        while current_date <= end_date:
            info = None
            day_of_week = current_date.weekday()
            if day_of_week == 7:
                # shabbos title
                parasha = parshios.getparsha(current_date, israel=True)
                if parasha:
                    info = "-".join(PARSHIOS_HEBREW[i] for i in parasha)
                else:
                    info = current_date.holiday(
                        israel=True, hebrew=True, prefix_day=True
                    )
            else:
                # major holiday title
                if major_holidays:
                    info = current_date.festival(
                        israel=True,
                        hebrew=True,
                        prefix_day=True,
                        include_working_days=minor_holidays,
                    )
                if not info and extra_holidays:
                    # Add Purim & Tisha Beav & Yom Haatzmaut
                    info = HebrewCalendar._get_extra_holiday(current_date)

            yield (
                f"{current_date.hebrew_day(False)} {current_date.month_name(True)}",
                info,
            )
            current_date = current_date.add(days=1)

    def learning_days(self, shabbos: bool = True) -> int:
        return sum(1 for date, info in self._date_info if not (info and shabbos))

    def generate_csv(
        self,
        input_iterator: Iterator,
        /,
        shabbos: bool = True,
        bold: bool = True,
    ) -> list[Row]:
        """
        shabbos -- do not learn on shabbos
        bold -- bold shabbos dates or any any unlearning dates
        """
        full_csv = []
        try:
            for date, info in self._date_info:
                if info and shabbos:
                    full_csv.append(Row(date=date, info=info, bold=bold))
                else:
                    full_csv.append(
                        Row(
                            date=date,
                            info=next(input_iterator),
                            bold=bold and info is not None,
                        )
                    )
        except StopIteration:
            print("short input csv file. not enough rows")
            return full_csv

        try:
            next(input_iterator)
            print("long input csv file. rows exceed the end date")
        except StopIteration:
            pass

        return full_csv

    def generate_csv_from_file(
        self,
        start_date: HebrewDate,
        end_date: HebrewDate,
        input_csv: str,
        /,
        shabbos: bool = True,
        major_holidays: bool = True,
        minor_holidays: bool = False,
        extra_holidays: bool = True,
        bold: bool = True,
    ) -> list[Row]:
        with open(input_csv, mode="r") as file:
            p_iter = csv.reader(file)

            def it_wrapper(it):
                return map(lambda x: x[0], it)

            return self.generate_csv(
                start_date,
                end_date,
                it_wrapper(p_iter),
                shabbos=shabbos,
                major_holidays=major_holidays,
                minor_holidays=minor_holidays,
                extra_holidays=extra_holidays,
                bold=bold,
            )


def write_to_csv(hebrew_dates, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(hebrew_dates)

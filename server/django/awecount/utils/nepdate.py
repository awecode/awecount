# ## BEGIN LICENSE
# Copyright (C) 2013 Shritesh Bhattarai shritesh@shritesh.com.np
# This library is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License, as published
# by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
# ## END LICENSE
import datetime

'''
A module to convert Bikram Samwat (B.S.) to A.D. and vice versa.
Usage:
print nepdate.ad2bs((1995,9,12))
print nepdate.bs2ad((2052,05,27))
Range:
1944 A.D. to 2033 A.D.
2000 B.S. to 2089 B.S.
bs : a dictionary that contains the number of days in each month of the B.S. year
bs_equiv, ad_equiv  : The B.S. and A.D. equivalent dates for counting and calculation
'''

(bs_equiv, ad_equiv) = ((2000, 9, 17), (1944, 1, 1))

bs = {}
bs[2000] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2001] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2002] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2003] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2004] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2005] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2006] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2007] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2008] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31)
bs[2009] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2010] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2011] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2012] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30)
bs[2013] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2014] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2015] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2016] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30)
bs[2017] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2018] = (31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2019] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2020] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2021] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2022] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30)
bs[2023] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2024] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2025] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2026] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2027] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2028] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2029] = (31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30)
bs[2030] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2031] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2032] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2033] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2034] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2035] = (30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31)
bs[2036] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2037] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2038] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2039] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30)
bs[2040] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2041] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2042] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2043] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30)
bs[2044] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2045] = (31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2046] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2047] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2048] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2049] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30)
bs[2050] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2051] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2052] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2053] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30)
bs[2054] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2055] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2056] = (31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30)
bs[2057] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2058] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2059] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2060] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2061] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2062] = (30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31)
bs[2063] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2064] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2065] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2066] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31)
bs[2067] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2068] = (31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2069] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2070] = (31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30)
bs[2071] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2072] = (31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30)
bs[2073] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31)
bs[2074] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2075] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2076] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30)
bs[2077] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31)
bs[2078] = (31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2079] = (31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30)
bs[2080] = (31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30)
bs[2081] = (31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2082] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2083] = (31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2084] = (31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2085] = (31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30)
bs[2086] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2087] = (31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30)
bs[2088] = (30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30)
bs[2089] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30)
bs[2090] = (30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30)


def string_from_tuple(tuple_to_convert):
    """
    Returns the given tuple as string in the format YYYY-MM-DD
    tuple_to_convert : A tuple in the format (year,month,day)
    """
    if not tuple_to_convert:
        return
    (year, month, day) = tuple_to_convert
    return str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)


def tuple_from_string(string_to_convert):
    """
    Returns the given string as tuple in the format (year, month, day)
    string_to_convert : A tuple in the format 'YYYY-MM-DD
    """
    return tuple([int(x) for x in string_to_convert.split('-')])


def date_from_tuple(tuple_to_convert):
    """
    Returns the given tuple as datetime.date object
    tuple_to_convert : A tuple in the format (year,month,day)
    """
    (year, month, day) = tuple_to_convert
    return datetime.date(year, month, day)


def tuple_from_date(date_to_convert):
    """
    Returns the given date object as tuple in the format (year,month,day)
    date_to_convert : A date object
    """
    (year, month, day) = (date_to_convert.year, date_to_convert.month, date_to_convert.day)
    return year, month, day


def count_ad_days(begin_ad_date, end_ad_date):
    """
    Returns the number of days between the two given A.D. dates.
    begin_ad_date : A tuple in the format (year,month,day) that specify the date to start counting from.
    end_ad_date : A tuple in the format (year,month,day) that specify the date to end counting.
    """
    date_begin = date_from_tuple(begin_ad_date)
    date_end = date_from_tuple(end_ad_date)
    delta = date_end - date_begin
    return delta.days


def count_bs_days(begin_bs_date, end_bs_date):
    """
    Returns the number of days between the two given B.S. dates.
    begin_ad_date : A tuple in the format (year,month,day) that specify the date to start counting from.
    end_ad_date : A tuple in the format (year,month,day) that specify the date to end counting.
    NOTE:
    Tuple in the dictionary starts from 0
    The range(a,b) function starts from a and ends at b-1
    """
    begin_year, begin_month, begin_day = begin_bs_date
    end_year, end_month, end_day = end_bs_date
    days = 0
    # 1) First add total days in all the years
    for year in range(begin_year, end_year + 1):
        for days_in_month in bs[year]:
            days = days + days_in_month
    # 2) Subtract the days from first (n-1) months of the beginning year
    for month in range(0, begin_month):
        days = days - bs[begin_year][month]
    # 3) Add the number of days from the last month of the beginning year
    days = days + bs[begin_year][12 - 1]
    # 4) Subtract the days from the last months from the end year
    for month in range(end_month - 1, 12):
        days = days - bs[end_year][month]
    # 5) Add the beginning days excluding the day itself
    days = days - begin_day - 1
    # 5) Add the last remaining days excluding the day itself
    days = days + end_day - 1
    return days


def add_ad_days(ad_date, num_days):
    """
    Adds the given number of days to the given A.D. date and returns it as a tuple in the format (year,month,day)
    ad_date : A tuple in the format (year,month,day)
    num_days : Number of days to add to the given date
    """
    date = date_from_tuple(ad_date)
    day = datetime.timedelta(days=num_days)
    return tuple_from_date(date + day)


def add_bs_days(bs_date, num_days):
    """
    Adds the given number of days to the given B.S. date and returns it as a tuple in the format (year,month,day)
    bs_date : a tuple in the format (year,month,day)
    num_days : Number of days to add to the given date
    Note:
    Tuple in the dictionary starts from 0
    """
    (year, month, day) = bs_date
    # 1) Add the total number of days to the original days
    day = day + num_days
    # 2) Until the number of days becomes applicable to the current month,
    # subtract the days by the number of days in the current month and increase the month
    while day > bs[year][month - 1]:
        day = day - bs[year][month - 1]
        month = month + 1
        # 3) If month reaches 12, increase the year by 1 and set the month to 1
        if month > 12:
            month = 1
            year = year + 1
    return (year, month, day)


def bs2ad(bs_date):
    """
    Returns the A.D. equivalent date as a tuple in the format (year,month,day) if the date is within range, else returns None
    bs_date : A tuple in the format (year,month,day)
    """
    if isinstance(bs_date, datetime.date):
        bs_date = tuple_from_date(bs_date)
    if isinstance(bs_date, str):
        bs_date = tuple(map(int, bs_date.split('-')))

    (year, month, day) = bs_date
    if year < 2000 or year > 2090 or month < 1 or month > 12 or day < 1 or day > 32:
        # return None
        raise ValueError('Invalid BS Date')
    else:
        date_delta = count_bs_days(bs_equiv, bs_date)
        return add_ad_days(ad_equiv, date_delta)


def ad2bs(ad_date):
    """
    Returns the B.S. equivalent date as a tuple in the format (year,month,day) if the date is within range, else returns None
    bs_date : A tuple in the format (year,month,day)
    """
    if not ad_date:
        return
    if isinstance(ad_date, str):
        ad_date = tuple_from_string(ad_date)
    if isinstance(ad_date, datetime.date):
        ad_date = tuple_from_date(ad_date)
    (year, month, day) = ad_date
    if year < 1944 or year > 2033 or month < 1 or month > 12 or day < 1 or day > 31:
        # return None
        raise ValueError('Invalid AD Date')
    else:
        date_delta = count_ad_days(ad_equiv, ad_date)
        return add_bs_days(bs_equiv, date_delta)


def today():
    """
    Returns today's date in B.S. as tuple in the format (year, month, day)
    """
    return ad2bs(tuple_from_date(datetime.date.today()))


def today_as_str():
    """
    Returns today's date in B.S. as string in the format 'YYYY-MM-DD'
    """
    (year, month, day) = ad2bs(tuple_from_date(datetime.date.today()))
    return str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)


def is_valid(date_as_str):
    """
    Checks if the fed date string is a valid B.S. date
    date_as_str: String in the format 'YYYY-MM-DD'
    Returns True for valid date, False for invalid.
    """
    try:
        (year, month, day) = [int(p) for p in date_as_str.split('-')]
    except ValueError:
        return False
    if not 0 < month < 13:
        return False
    try:
        if not 0 < day <= bs[year][month - 1]:
            return False
    except:
        raise Exception('The year ' + str(year) + ' isn\'t supported.')
    return True
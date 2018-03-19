#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

=============
annual_report
=============

Annual Report Link Aggregator and Downloader.

The program scrapes the links to Annual Reports for NSE Symbols and
downloads them.


Quick Summary
-------------

If you want to follow all the sensible defaults, make sure there is a
file called ``download_symbols.txt`` alongside this file which contains
the NSE symbols you are interested in (see ``all_symbols.txt`` for
example), then run:

    python3 annual_report.py -a -d

To see all the available arguments, pass the ``-h`` or ``--help``
argument like:

    python3 annual_report.py -h
    annual_report.exe --help

If you are using annual_report.exe instead of the Python script, then
replace ``python3 annual_report.py`` with ``annual_report.exe`` in all
the commands you run. For example:

    python3 annual_report.py -a -d

becomes:

    annual_report.exe -a -d

"""

__author__ = "Aditya <code.aditya (at) gmail>"
__version__ = "0.1-dev"
__license__ = "GNU GPL v3"


import argparse
import datetime
import json
import logging
import os
import sys

import requests
from bs4 import BeautifulSoup

#### Global Variables #########################################################
LINK_URL = "http://nseindia.com/corporates/shldInformation/shldinfo_annualReports.jsp?symbol={0}"
REPORT_URL = "http://nseindia.com"
JSON_FILE = "annual_report_links.json"
SYMBOL_FILE = "download_symbols.txt"
TEST_FOLDER = "test_data"
WRITE_TEST_DATA = False
USE_TEST_DATA = False
DEBUG = False

if WRITE_TEST_DATA:
    # os.makedirs(TEST_FOLDER, exist_ok=True)     # exist_ok was added in Py3.2
    if not os.path.isdir(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)

help_msg = dict(
    description="Annual Report Link Aggregator and Downloader.",
    epilog=("Author: {0}, Version: {1}, License: {2}"
            "".format(__author__, __version__, __license__)),
    verbose = "get more verbose output including the debug logs",
    symbol_file=("the file containing all the NSE symbols for which this "
                 "program is to be used"),
    offset=("the number of NSE symbols which should be skipped from the "
            "beginning of symbol-file, keep it as a positive integer unless "
            "you know what you are doing"),
    aggregate=("aggregate the links to all the annual reports available for "
               "symbols in the given symbol-file"),
    force_update=("force the link page for symbols to be scraped even if the "
                  "link for the latest financial year for it already exists"),
    download=("download the reports for a given financial-year for all the "
              "symbols in the given symbol-file; if --rename-existing "
              "argument is passed as well, then reports aren't downloaded, "
              "just the existing ones are renamed : see --rename-existing for "
              "more information about how this works"),
    financial_year=("the financial year for which the reports are to be "
                    "downloaded"),
    base_download_folder="the base folder where reports would be downloaded",
    simulate=("simulate the running of download command without actually "
              "downloading any report"),
    size_only=("don't download the report, but only show the size of the file "
               "that would be downloaded by making a HEAD request"),
    rename_existing=("rename the existing output files to strip everything "
                     "before the Symbol string, you need to pass the -d "
                     "argument for it to work; by default only the reports "
                     "for the latest financial year are renamed, for others "
                     "add the -fy argument; you may also use the --simulate "
                     "argument which would show how the files would be "
                     "renamed without actually renaming them; it is highly "
                     "experimental at this stage and may be modified/removed "
                     "in future versions"),
)
###############################################################################


def _update_logging_level():
    """Update the logging level for the logger object and all the
    handlers based on DEBUG global variable.

    """
    logging_level = logging.DEBUG if DEBUG else logging.INFO
    logger.setLevel(logging_level)
    ch.setLevel(logging_level)


#### Add logging functionality ################################################
logger = logging.getLogger(__name__)
# Output formatting
# formatter = logging.Formatter("{asctime} - {levelname:8s} - {message}",
#                               style="{")  # style keyword was added in Py 3.2
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
# Console handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
# Change logging level based on DEBUG global variable
_update_logging_level()
# Add console handler to logger object
logger.addHandler(ch)
###############################################################################


def read_symbol_file(symbol_file):
    """Reads the name of Symbols separated by newlines and returns them
    as a list.

    :param symbol_file: the file containing the symbol of scrips
    :type symbol_file: str

    :returns: list of symbols
    :rtype: list

    """
    logger.debug("Reading the file of NSE Symbols...")
    try:
        with open(symbol_file, "r") as f:
            scrips = f.read().splitlines()
    except FileNotFoundError:
        logger.error("Symbol file could not be found: {0}".format(symbol_file))
        scrips = []
    return list(filter(None, scrips))


def read_json():
    """Reads the JSON file containing links to Annual Report and returns
    it as a dictionary.

    :returns: dictionary of links for each financial year
    :rtype: dict

    """
    try:
        logger.debug("Reading the JSON File containing links...")
        with open(JSON_FILE, "r") as f:
            annual_report_links = json.load(f)
        return annual_report_links
    except FileNotFoundError:
        return dict()


def write_json(annual_report_links):
    """Writes the JSON file containing links to Annual Report.

    :param annual_report_links: links to Annual Report to be written as
                                JSON
    :type annual_report_links: dict

    """
    logger.debug("Writing fresh JSON File with latest links...")
    with open(JSON_FILE, "w") as f:
        json.dump(annual_report_links, f, sort_keys=True, indent=4)


def encode_special_characters(symbol):
    """Encodes the special characters in symbol and returns it.

    :param symbol: the symbol string to be encoded
    :type symbol: str

    :rtype: str

    """
    return symbol.replace("&", "%26")


def get_link_page_for(symbol):
    """Fetch the page containing links to Annual Reports for symbol and
    return it as html text.

    :param symbol: NSE Symbol for which page containing links to its
                   Annual Reports is to be fetched
    :type symbol: str

    :rtype: str

    """
    test_file = os.path.join(TEST_FOLDER, symbol + ".html")
    if USE_TEST_DATA:
        logger.debug("Using the test data...")
        try:
            with open(test_file, "r") as link_page:
                return link_page.read()
        except FileNotFoundError:
            logger.error("Test file could not be found: {0}".format(test_file))
    else:
        encoded_symbol = encode_special_characters(symbol)
        url = LINK_URL.format(encoded_symbol)
        r = requests.get(url)
        if WRITE_TEST_DATA:
            with open(test_file, "w") as link_page:
                link_page.write(r.text)
        return r.text


def scrape_links_for(symbol):
    """Scrape the links to Annual Reports for symbol and return it as a
    JSON dictionary of links for each financial year.

    :param symbol: NSE Symbol for which links to its Annual Report is
                   to be scrapped
    :type symbol: str

    :returns: JSON dictionary of links for each financial year
    :rtype: str

    """
    logger.info("Scraping links for: {symbol}".format(symbol=symbol))
    html_text = get_link_page_for(symbol)
    soup = BeautifulSoup(html_text)
    scrapped_links = soup.find_all("a")
    report_links = dict()
    if not scrapped_links:
        logger.warning("{symbol}: No links available.".format(symbol=symbol))
    for item in scrapped_links:
        year = item.text
        if len(year) == 4 and year.isdigit():
            year = item.text + "-" + str(int(item.text) + 1)
        link = REPORT_URL + item.get("href")
        report_links[year] = link
    return json.dumps({symbol: report_links},
                      sort_keys=True, indent=4)


def apply_server_timestamp(output_file, last_modified):
    """Changes the last modified and last access time of the output file
    to the one as received from Last-Modified response header.

    :param output_file: the file whose timestamp is to be altered
    :param last_modified: time string as received from Response headers

    :type output_file: str
    :type last_modified: str

    """
    server_datetime = datetime.datetime.strptime(last_modified,
                                                 "%a, %d %b %Y %H:%M:%S GMT")
    server_utc_time = server_datetime.replace(tzinfo=datetime.timezone.utc)
    server_timestamp = server_utc_time.timestamp()
    os.utime(output_file, times=(server_timestamp, server_timestamp))


def download_to_save(url, download_location):
    """Downloads the file and saves it on disk.

    :param url: link to download and save
    :param download_location: folder where to save the downloaded file

    :type url: str
    :type download_location: str

    """
    os.makedirs(download_location, exist_ok=True)
    file_name = os.path.basename(url)
    file_name_components = file_name.split("_")
    output_file_name = "_".join(file_name_components[-4:])
    output_file = os.path.join(download_location, output_file_name)
    download_file_name = output_file_name + ".downloading"
    download_file = os.path.join(download_location, download_file_name)
    # Get local copies since these would be accessed a lot of times
    write = sys.stdout.write
    flush = sys.stdout.flush
    # Download the file
    r = requests.get(url, stream=True)
    if not r.ok:
        logger.error("Could not be downloaded: {url}".format(url=url))
        return
    total_length = int(r.headers.get("Content-Length", default=0))
    # If we encounter any Exception, we always want to indicate the un-finished
    # download as bad and re-raise the same Exception
    try:
        with open(download_file, "wb") as f:
            downloaded_length = 0
            for chunk in r.iter_content(1024 * 64):    # 64KiB
                f.write(chunk)
                downloaded_length += len(chunk)
                if total_length:
                    progress_pct = (downloaded_length / total_length) * 100
                    progress_bars = int(50 * (progress_pct / 100))
                    write("\r[{indicator:50}] {progress}% of {total:.2f} MiB"
                          "".format(indicator="=" * progress_bars,
                                    progress=int(progress_pct),
                                    total=total_length / (1024 * 1024)))
                else:
                    write("\rDownloaded so far: {length:.2f} MiB"
                          "".format(length=downloaded_length / (1024 * 1024)))
                flush()
    except:
        write("\n")
        raise
    else:
        write("\n")
        os.replace(download_file, output_file)
        last_modified = r.headers.get("Last-Modified")
        if last_modified:
            apply_server_timestamp(output_file, last_modified)
        logger.debug("Downloaded: {url}".format(url=url))


def get_download_size(url, symbol):
    """Makes a HEAD request to the ``url`` and returns the download size
    based on Content-Length response header.

    :param url: the url for which download size is required
    :param symbol: the NSE symbol to which the url relates to

    :type url: str
    :type symbol: str

    :returns: download size in MiB
    :rtype: int

    """
    r = requests.head(url)
    total_length = int(r.headers.get("Content-Length", default=0))
    total_length = total_length / (1024 * 1024)
    logger.info("{symbol} : {url} : {length:.2f} MiB"
                "".format(symbol=symbol, url=url, length=total_length))
    return total_length


def get_latest_financial_year():
    """Returns the latest financial year based on system date.

    :rtype: str

    """
    current_year = datetime.date.today().year
    latest_financial_year = str(current_year - 1) + "-" + str(current_year)
    return latest_financial_year


def aggregate_links(symbol_file, force_update=False, offset=0):
    """Scrapes the link page for all the symbols in ``symbol_file`` to
    update the JSON file.

    Link page for a symbol is not scrapped if there already exists the
    link for it for the latest financial year. To scrap them as well,
    set ``force_update`` to ``True``.

    :param symbol_file: the file containing the NSE symbol of scrips
    :param force_update: link page for symbols are downloaded and
                         scrapped even if the link for the latest
                         financial year for it already exists if this
                         parameter is set to ``True``
    :offset: the number of symbols which should be skipped from the
             beginning of ``symbol_file``

    :type symbol_file: str
    :type force_update: bool
    :type offset: int

    """
    annual_report_links = read_json()
    symbol_list = read_symbol_file(symbol_file)
    latest_financial_year = get_latest_financial_year()
    symbols_scraped = 0
    links_added = 0
    links_modified = 0
    links_added_for = []
    links_modified_for = []
    # If any Exception occurs, we always want to write the JSON file
    # whatever be the Exception. So, we catch the Exception, write our
    # JSON file and re-raise the same Exception.
    try:
        for symbol in symbol_list[offset:]:
            symbol = symbol.upper()
            if (force_update or not annual_report_links.get(symbol)
                    or not annual_report_links[symbol].get(latest_financial_year)):
                symbol_json = scrape_links_for(symbol)
                symbol_links = json.loads(symbol_json)
                symbols_scraped += 1
                if symbol not in annual_report_links:
                    logger.debug("{symbol} would be added to the JSON File..."
                                 "".format(symbol=symbol))
                    annual_report_links[symbol] = dict()
                for year in symbol_links.get(symbol):
                    link = symbol_links[symbol][year]
                    msg_add = [symbol, year, "Added", link]
                    msg_mod = [symbol, year, "Modified", link]
                    if year not in annual_report_links[symbol]:
                        annual_report_links[symbol][year] = link
                        logger.info(" : ".join(msg_add))
                        links_added += 1
                        links_added_for.append(symbol)
                    elif annual_report_links[symbol][year] != link:
                        annual_report_links[symbol][year] = link
                        logger.warning(" : ".join(msg_mod))
                        links_modified += 1
                        links_modified_for.append(symbol)
    except:
        raise
    finally:
        write_json(annual_report_links)
        logger.info("Total symbols scraped: {0}".format(symbols_scraped))
        logger.info("Total links added: {0} {1}"
                    "".format(links_added, links_added_for))
        logger.info("Total links modified: {0} {1}"
                    "".format(links_modified, links_modified_for))
    logger.info("Aggregation finished...")


def download_reports(symbol_file, financial_year, base_download_folder,
                     simulate=False, show_download_size_only=False,
                     rename_existing=False, offset=0):
    """Downloads the Annual Report for a given ``financial_year`` for
    all the symbols in ``symbol_file``.

    Report for all the financial years are downloaded in its own
    sub-folder inside the ``base_download_folder``.

    :param symbol_file: the file containing the NSE symbol of scrips
    :param financial_year: financial year for which reports are to be
                           downloaded
    :param base_download_folder: base folder where reports would be
                                 saved inside a sub-folder for every
                                 financial year
    :param simulate: simulates the running of this function without
                     actually downloading any Annual Report if this
                     argument is set to ``True``
    :param show_download_size_only: the report isn't downloaded, but
                                    only a HEAD request is made to show
                                    the size of the file that would be
                                    downloaded if this argument is set
                                    to ``True``
    :param rename_existing: rename the existing output files to strip
                            everything before the Symbol string
    :param offset: the number of symbols which should be skipped from
                   the beginning of ``symbol_file``

    :type symbol_file: str
    :type financial_year: str
    :type base_download_folder: str
    :type simulate: bool
    :type show_download_size_only: bool
    :type rename_existing: bool
    :type offset: int

    """
    download_location = os.path.join(base_download_folder, financial_year)
    annual_report_links = read_json()
    symbol_list = read_symbol_file(symbol_file)
    total_size = 0
    for symbol in symbol_list[offset:]:
        symbol = symbol.upper()
        if not annual_report_links.get(symbol):
            logger.warning("{symbol} : No links available"
                           "".format(symbol=symbol))
            continue
        url = annual_report_links[symbol].get(financial_year)
        if url:
            file_name = os.path.basename(url)
            output_file = os.path.join(download_location, file_name)
            file_name_components = file_name.split("_")
            renamed_file_name = "_".join(file_name_components[-4:])
            renamed_file = os.path.join(download_location, renamed_file_name)
            if rename_existing:
                if os.path.exists(output_file):
                    logger.info("{0} renamed to {1}"
                                "".format(file_name, renamed_file_name))
                    try:
                        if not simulate:
                            os.rename(output_file, renamed_file)
                    except OSError:
                        logger.warning("{output_file} couldn't be renamed"
                                       "".format(output_file=output_file))
                continue
            existing_file = (renamed_file_name if os.path.exists(renamed_file)
                                               else file_name)
            if os.path.exists(output_file) or os.path.exists(renamed_file):
                logger.debug("{symbol} : Already exists : {file_name}"
                             "".format(symbol=symbol, file_name=existing_file))
            else:
                if show_download_size_only:
                    total_size += get_download_size(url, symbol)
                else:
                    logger.info("{symbol} : Downloading : {url}"
                                "".format(symbol=symbol, url=url))
                    if not simulate:
                        download_to_save(url, download_location)
        else:
            logger.debug("{symbol} : No report available : {year}"
                         "".format(symbol=symbol,
                                   year=financial_year))
    if show_download_size_only:
        logger.info("Total estimated download size: {size:.2f} MiB"
                    "".format(size=total_size))
    logger.info("Downloading finished...")


def main():
    """Implements the Command Line Interface for the program.

    """
    # create a parser
    parser = argparse.ArgumentParser(
        description=help_msg.get("description"),
        epilog=help_msg.get("epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # add all the arguments
    # common arguments
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        help=help_msg.get("verbose")
    )
    parser.add_argument(
        "-s", "--symbol-file",
        default=SYMBOL_FILE,
        dest="symbol_file",
        help=help_msg.get("symbol_file") + " [default: %(default)s]"
    )
    parser.add_argument(
        "-o", "--offset",
        type=int,
        default=0,
        dest="offset",
        help=help_msg.get("offset") + " [default: %(default)s]"
    )
    # aggregate-only arguments
    aggregate_group = parser.add_argument_group("aggregate links")
    aggregate_group.add_argument(
        "-a", "--aggregate",
        action="store_true",
        dest="aggregate",
        help=help_msg.get("aggregate")
    )
    aggregate_group.add_argument(
        "--force-update",
        action="store_true",
        dest="force_update",
        help=help_msg.get("force_update")
    )
    # download-only arguments
    download_group = parser.add_argument_group("download reports")
    download_group.add_argument(
        "-d", "--download",
        action="store_true",
        dest="download",
        help=help_msg.get("download")
    )
    download_group.add_argument(
        "-fy", "--financial-year",
        default=get_latest_financial_year(),
        dest="financial_year",
        help=help_msg.get("financial_year") + " [default: %(default)s]"
    )
    download_group.add_argument(
        "--base-download-folder",
        default=os.getcwd(),
        dest="base_download_folder",
        help=help_msg.get("base_download_folder") + "[default: %(default)s]"
    )
    download_group.add_argument(
        "--simulate", "--dry-run",
        action="store_true",
        dest="simulate",
        help=help_msg.get("simulate")
    )
    download_group.add_argument(
        "--size-only", "--show-download-size-only",
        action="store_true",
        dest="size_only",
        help=help_msg.get("size_only")
    )
    download_group.add_argument(
        "--rename-existing",
        action="store_true",
        dest="rename_existing",
        help=help_msg.get("rename_existing")
    )
    # parse the arguments
    args = parser.parse_args()
    # perform the necessary action based on arguments parsed
    try:
        if args.verbose:
            global DEBUG
            DEBUG = True
            _update_logging_level()
        if args.aggregate:
            aggregate_links(args.symbol_file,
                            force_update=args.force_update,
                            offset=args.offset)
        if args.download:
            download_reports(args.symbol_file,
                             args.financial_year,
                             args.base_download_folder,
                             simulate=args.simulate,
                             show_download_size_only=args.size_only,
                             rename_existing=args.rename_existing,
                             offset=args.offset)
    except requests.exceptions.ConnectionError:
        logger.error("Please check your network connection...")
    except ConnectionError:
        logger.error("Try to resume program after some time - an hour atleast. "
                     "It looks like you have been using the program for a long "
                     "time and NSE doesn't like it.")
    except KeyboardInterrupt:
        logger.info("Prematurely exiting the program...")


if __name__ == "__main__":
    main()

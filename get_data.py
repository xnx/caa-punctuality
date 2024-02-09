import sys
import calendar
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# The website domain from which we will download the
# airline punctuality data.
ROOT_URL = "https://www.caa.co.uk"
# The local directory in which to store the downloaded CSV files.
DATA_DIR = Path("data")

# The year for which data are requested is specified on the
# command line.
try:
    year = int(sys.argv[1])
except (IndexError, ValueError):
    print(f"Usage: {sys.argv[0]} <year as YYYY>")
    sys.exit(1)

# Each year's data gets its own directory: create this if
# it doesn't already exist.
year_dir = DATA_DIR / str(year)
if not year_dir.exists():
    year_dir.mkdir()

# There is an index page for CSV files for each year's data:
# we're going to store a loca copy of this if we don't already
# have it.
index_local_html_file = year_dir / f"{year}-index.html"


def download_from_url(url):
    """Download the web page (or CSV data) from url."""
    page = requests.get(url)
    if page.status_code != 200:
        # If something goes wrong (e.g. server error or page
        # not found) then exit the script with the status code.
        print(f"Failed to download from {url}")
        print(f"Attempt failed with HTTP status code {page.status_code}")
        sys.exit(1)
    return page


if not index_local_html_file.exists():
    print(f"Getting index page for year {year}...")
    index_page_url = f"https://www.caa.co.uk/data-and-analysis/uk-aviation-market/flight-punctuality/uk-flight-punctuality-statistics/{year}/"
    page = download_from_url(index_page_url)
    # Save a local copy of the HTML page with the index of data
    # for the requested year.
    with open(index_local_html_file, "w") as fo:
        fo.write(page.text)
    print(f"Index page saved as {index_local_html_file}")
    page_html = page.text
else:
    with open(index_local_html_file) as fi:
        page_html = fi.read()

# Parse the downloaded page text into HTML soup.
soup = BeautifulSoup(page_html, "html.parser")

def get_link_text(year, month):
    """
    A generator yielding possible link texts for the monthly
    CSV punctuality data files. Unfortunately, these have
    changed in the index pages over the years.
    """

    if year > 2017:
        # The recent files are consistently named as follows:
        yield f"{year}{month:02d} Punctuality Statistics Full Analysis Arrival Departure (CSV document)"
    yield f"{year}{month:02d} Full Analysis Arr Dep"
    yield f"{year}{month:02d}Full Analysis Arr Dep"
    yield f"{year}{month:02d}FullAnalysisArrDep"


for month in range(1, 13):
    month_and_year = f"{calendar.month_name[month]} {year}"

    # Get all the HTML <a> tags matching the link text.
    # We need to try different link texts until one matches
    # because these have changed on the CAA website over time.
    link_text_generator = get_link_text(year, month)
    for link_text in link_text_generator:
        atag = soup.select_one(f'a:-soup-contains("{link_text}")')
        if atag:
            break
    # Skip missing tags (e.g. data not yet available, unmatched
    # link text).
    else:
        print(f"Missing CSV link for {month_and_year}")
        continue

    # Now form the full url for this month's CSV file...
    csv_url = ROOT_URL + atag.attrs["href"]
    # ... and download the CSV data if we don't already have it.
    csv_filename = year_dir / f"{year}{month:02d}.csv"
    if not csv_filename.exists():
        print(f"Downloading CSV data for {month_and_year} from {csv_url}")
        page = download_from_url(csv_url)
        csv_data = page.text
        with open(csv_filename, "w") as fo:
            fo.write(csv_data)
    else:
        print(f"Skipping data download for {month_and_year}: {csv_filename} exists.")

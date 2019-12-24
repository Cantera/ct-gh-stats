"""Retrieve clone and download statistics for Cantera/cantera on GitHub."""

import sys
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime, timezone

import requests
import pandas as pd

HERE = Path(__file__).parent
token = (HERE / "access.cred").read_text().strip()
URL = "https://api.github.com/repos/Cantera/cantera/"

headers = {
    "Authorization": "token {}".format(token),
    "Accept": "application/vnd.github.v3+json",
}


def get_traffic(endpoint):
    """Get data from the traffic API at the input endpoint.

    Gets the specified data, ``'clones'`` or ``'views'``, from the GitHub
    traffic API. Uses the v3 API to retrieve JSON output. The data from this API
    contains 2 weeks of data at a daily frequency. The data are loaded into a
    `~pandas.DataFrame` and combined with any existing data. Historical data are
    stored in JSON files in the local directory named for the ``endpoint``
    passed in. The JSON storage is probably a temporary solution until we see
    what other means would be more appropriate.

    :param endpoint: String representing the endpoint to get data from. Designed
        to be one of ``'clones'`` or ``'views'``.
    """
    traffic = "traffic/{}".format(endpoint)
    r = requests.get(urljoin(URL, traffic), headers=headers)
    r.raise_for_status()

    database = HERE / "{}.json".format(endpoint)
    if database.exists():
        old_df = pd.read_json(database, convert_dates=True)
    else:
        old_df = pd.DataFrame()

    new_df = pd.DataFrame.from_dict(r.json()[endpoint])
    datetime_index = pd.to_datetime(new_df["timestamp"])
    new_df = new_df.set_index(datetime_index)
    new_df = new_df.drop("timestamp", axis=1)
    new_df = new_df.astype(int)

    # Combine the new data with the old, overwriting any old data with
    # new data. This ensures any overlapping data are the most up-to-date.
    df = new_df.combine_first(old_df)
    df.to_json(database, date_format="iso")


def get_releases():
    """Get data about release assets from the releases API.

    Gets download counts for each of the assets attached to the releases on
    GitHub. The GitHub API only provides total download counts and no historical
    data, so this function should be run with the desired frequency of data
    collection. The data are loaded into a `~pandas.DataFrame` and combined with
    any existing data. Historical data are stored in JSON files in the local
    directory named for the ``endpoint`` passed in. The JSON storage is probably
    a temporary solution until we see what other means would be more
    appropriate.
    """
    r = requests.get(
        urljoin(URL, "releases"), headers={"Accept": "application/vnd.github.v3+json"}
    )
    r.raise_for_status()

    new_df = pd.DataFrame(index=[datetime.now(tz=timezone.utc)])
    for release in r.json():
        if release["draft"]:
            continue
        for asset in release["assets"]:
            col_name = asset["name"]
            if asset["name"] in new_df.columns:
                col_name += "_" + release["tag_name"]

            new_df[col_name] = int(asset["download_count"])

    database = HERE / "releases.json"
    if database.exists():
        old_df = pd.read_json(database, convert_dates=True)
    else:
        old_df = pd.DataFrame()

    # Combine the new data with the old, overwriting any old data with
    # new data. This ensures any overlapping data are the most up-to-date.
    df = new_df.combine_first(old_df)
    df.to_json(database, date_format="iso")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Must pass an argument to the script")
    elif sys.argv[1] in ["clones", "views"]:
        get_traffic(sys.argv[1])
    elif sys.argv[1] == "releases":
        get_releases()
    else:
        raise ValueError(
            "Argument to the script must be one of 'clones', 'views', or 'releases'"
        )

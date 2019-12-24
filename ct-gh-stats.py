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


def get_clones():
    r = requests.get(urljoin(URL, "traffic/clones"), headers=headers)
    r.raise_for_status()

    if (HERE / "clones.json").exists():
        old_df = pd.read_json(HERE / "clones.json", convert_dates=True)
    else:
        old_df = pd.DataFrame()

    new_df = pd.DataFrame.from_dict(r.json()["clones"])
    datetime_index = pd.to_datetime(new_df["timestamp"])
    new_df = new_df.set_index(datetime_index)
    new_df = new_df.drop("timestamp", axis=1)
    new_df = new_df.astype(int)

    df = new_df.combine_first(old_df)
    df.to_json("clones.json", date_format="iso")


def get_views():
    r = requests.get(urljoin(URL, "traffic/views"), headers=headers)
    r.raise_for_status()

    if (HERE / "views.json").exists():
        old_df = pd.read_json(HERE / "views.json", convert_dates=True)
    else:
        old_df = pd.DataFrame()

    new_df = pd.DataFrame.from_dict(r.json()["views"])
    datetime_index = pd.to_datetime(new_df["timestamp"])
    new_df = new_df.set_index(datetime_index)
    new_df = new_df.drop("timestamp", axis=1)
    new_df = new_df.astype(int)

    df = new_df.combine_first(old_df)
    df.to_json("views.json", date_format="iso")


def get_releases():
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

    if (HERE / "releases.json").exists():
        old_df = pd.read_json(HERE / "releases.json", convert_dates=True)
    else:
        old_df = pd.DataFrame()

    df = new_df.combine_first(old_df)
    df.to_json("releases.json", date_format="iso")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Must pass an argument to the script")
    if sys.argv[1] == "clones":
        get_clones()
    elif sys.argv[1] == "views":
        get_views()
    elif sys.argv[1] == "releases":
        get_releases()
    else:
        raise ValueError(
            "Argument to the script must be one of 'clones', 'views', or 'releases'"
        )

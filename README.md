# Cantera GitHub Stats

The Python script `ct-gh-stats.py` pulls data about Cantera from the GitHub API. It must be used by passing one argument to the script:

```shell
$ python ct-gh-stats.py [clones, views, releases]
```

where the arguments are:

- `clones`: Get data about clones of the Cantera/cantera repository
- `views`: Get data about views of the Cantera/cantera repository
- `releases`: Get data about the download of the release assets for all releases

The GitHub API returns two weeks of data for the `clones` and `views` endpoints, so those options should be run every two weeks. The `releases` endpoint provides no historical data, so that option should be run daily.

Collecting this data requires a GitHub Access Token generated for the Cantera/cantera repository. This can be done in the GitHub web interface. The token should be stored in a file called `access.cred`. Please protect this file, and make sure to only give it read permissions on the repositories.

The data from each of the options is stored in a JSON file for convenience. At some point, a longer-term data storage solution should be identified.

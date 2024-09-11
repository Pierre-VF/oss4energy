# Listing of open-source for energy applications

(This is a work in progress)

## Installation

The installation is straightforward if you are used to Python.

Create a virtual environment with Python 3.12 (the code is not tested for previous versions).

Then install the package:
> pip install .

It is highly recommended to operate with a Github token (which you can create [here](https://github.com/settings/tokens/new)) 
in order to avoid being blocked by Github's rate limit on the API. These are much lower for unauthenticated accounts.

Make sure to generate this token with permissions to access public repositories.

The token can be imported by generating a *.env* file in the root of your repository with the following content:

```bash
# This is your token generated here: https://github.com/settings/tokens/new
GITHUB_API_TOKEN="...[add your token here]..."

# You can adjust the position of the cache database here (leave to default if you don't need adjustment)
SQLITE_DB=".data/db.sqlite"
```

## Running the code

Once you have completed the steps above, you can run the following commands (only valid on Unix systems):

- To generate an output dataset:
    > make run
- To refresh the list of targets to be scraped:
    > make update_list


## Need new features or found a bug?

Please open an issue on the repository [here](https://github.com/Pierre-VF/oss4energy/issues).
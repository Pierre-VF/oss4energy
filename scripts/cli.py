"""
CLI module
"""

import typer

from oss4energy import scripts

app = typer.Typer()


@app.command()
def add(url: str):
    """Adds a resource to the index

    :param url: URL to add to the index
    """
    pass


@app.command()
def format():
    """Formats I/O files"""
    scripts.format_files()


@app.command()
def discover():
    """Generates an index"""
    scripts.discover_projects()


@app.command()
def publish():
    """Publishes the data to an online FTP"""
    scripts.publish_to_ftp()


@app.command()
def generate_listing():
    """Generates the updated listing"""
    scripts.generate_listing()


if __name__ == "__main__":
    app()

"""
CLI module
"""

import typer

from oss4energy import scripts

app = typer.Typer()


@app.command()
def add():
    """Adds a resource to the index

    :param url: URL to add to the index
    """
    urls_to_add = []
    x = "?"
    while x != "":
        x = input("Enter URL to be added (ENTER to stop adding): ")
        urls_to_add.append(x)
    print(f"Adding {urls_to_add}")
    scripts.add_projects_to_listing(urls_to_add)


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

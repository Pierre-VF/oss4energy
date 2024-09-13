"""
CLI module
"""

import typer

app = typer.Typer()


@app.command()
def add(url: str):
    """Adds a resource to the index

    :param url: URL to add to the index
    """
    pass


@app.command()
def index():
    """Generates an index"""
    pass


@app.command()
def publish():
    """Publishes the data to an online FTP"""
    pass


@app.command()
def generate():
    """Generates the updated listing"""
    pass


if __name__ == "__main__":
    app()

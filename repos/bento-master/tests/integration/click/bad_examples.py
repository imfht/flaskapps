import click


# should trigger CLC001
@click.command()
@click.option("-d")
def bad_help(d):
    pass


# should trigger CLC100
@click.command()
@click.option("-d", help="Hi mom")
def bad_option_one():
    pass


# should trigger CLC101
@click.command()
@click.option("d", help="Hi mom")
def bad_option_name(d):
    pass


# should trigger CLC102
@click.command()
@click.argument("-a", help="Hi mom")
def bad_argument_name(a):
    pass


# should trigger CLC103
@click.command()
@click.option(help="Hi mom")
def missing_option():
    pass


# should trigger CLC200
def bad_launch(x: str) -> None:
    click.launch(x)

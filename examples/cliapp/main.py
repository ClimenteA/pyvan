import click


@click.command()
@click.argument(
    "numbers",
    nargs=-1,
    type=float
)
def cli(numbers):
    if len(numbers) == 0:
        click.echo("Enter one or more numbers.")
        return
    click.echo("Computing the sum of the entered numbers:")
    click.echo(sum(numbers))


if __name__ == "__main__":
    cli()

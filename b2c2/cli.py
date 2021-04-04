import decimal
from json import JSONDecodeError

import click
from requests import HTTPError, RequestException

from b2c2.http_client import B2C2Client

URLS = {
    'sandbox': 'https://api.uat.b2c2.net',
    'production': 'https://api.b2c2.net',
}
MAX_ALLOWED_DECIMALS = 4


def validate_quantity(ctx, param, value) -> str:
    """
    Validates that `value` is a Decimal with 4 decimal maxium precision

    :param ctx:
    :param param:
    :param value:
    :raises click.BadParameter: When the format is invalid
    :return:
    """
    try:
        quantity = decimal.Decimal(value)
    except decimal.InvalidOperation:
        raise click.BadParameter("invalid format")

    if quantity.as_tuple().exponent * -1 > MAX_ALLOWED_DECIMALS:
        raise click.BadParameter("quantity parameter can have a maximum of 4 decimals")
    return str(quantity)


def echo_dict(data: dict):
    for k, v in data.items():
        click.echo(f"{k}: {v}")


@click.group()
@click.option('--env', type=click.Choice(URLS), default="sandbox")
@click.option('--api-token', envvar='API_TOKEN', required=True)
@click.pass_context
def cli(ctx, env, api_token):
    ctx.ensure_object(dict)
    ctx.obj['url'] = URLS[env]
    ctx.obj['http_client']: B2C2Client = B2C2Client(url=URLS[env], token=api_token)


@click.option(
    "--client-rfq-id", type=str, required=True,
    help="A universally unique identifier that will be returned to you if the request succeeds."
)
@click.option(
    "--quantity",
    required=True,
    type=decimal.Decimal,
    callback=validate_quantity,
    help="Quantity in base currency (maximum 4 decimals)."
)
@click.option("--side", required=True, type=click.Choice(("buy", "sell")))
@click.option("--instrument", required=True, type=str, help="Instrument as given by the /instruments/ endpoint.")
@cli.command()
@click.pass_context
def rfq(ctx, instrument, side, quantity, client_rfq_id):
    """
    Request For Quote and place and prompt the user to place an order if they want to.
    """
    click.echo("Sending Request For Quote..")
    response = ctx.obj['http_client'].request_for_quote(
        instrument=instrument, side=side, quantity=quantity, client_rfq_id=client_rfq_id
    )
    click.echo("Request For Quote response received:\n")
    echo_dict(response)
    click.confirm('\nDo you want to execute this RFQ and make an order?', abort=True)

    # Order
    ctx.invoke(
        order, instrument=instrument, side=side, quantity=quantity,
        client_order_id=client_rfq_id, price=response['price'],
        valid_until=response['valid_until']
    )


@click.option(
    "--price", required=True, type=str,
    help="Price at which you want the order to be executed. Only FOK."
)
@click.option(
    "--quantity",
    required=True,
    type=decimal.Decimal,
    callback=validate_quantity,
    help="Quantity in base currency (maximum 4 decimals)."
)
@click.option("--side", required=True, type=click.Choice(("buy", "sell")))
@click.option("--instrument", required=True, type=str, help="Instrument as given by the /instruments/ endpoint.")
@click.option("--valid-until", required=True, type=str, help="Datetime field formatted “%Y-%m-%dT%H:%M:%S”.")
@click.option(
    "--client-order-id", required=True, type=str,
    help="A universally unique identifier that will be returned to you in the response."
)
@cli.command()
@click.pass_context
def order(ctx, client_order_id, valid_until, instrument, side, quantity, price):
    response = ctx.obj['http_client'].post_order(
        instrument=instrument, side=side, quantity=quantity,
        price=price, order_type="FOK", valid_until=valid_until,
        client_order_id=client_order_id
    )
    executed_price = response['executed_price']
    if executed_price is None:
        click.secho("Your order was rejected.", fg="red")
        return
    click.secho(f"Order placed. Executed price {executed_price}", fg="green")

    trades = response.pop('trades')
    echo_dict(response)

    for trade in trades:
        click.secho(f"Trade {trade.pop('trade_id')}", fg="blue")
        echo_dict(trade)

    # Show the balance
    ctx.invoke(balance)


@cli.command()
@click.pass_context
def instruments(ctx):
    """List all your tradable instruments."""
    click.echo("Getting the list of your tradable instruments..")
    response = ctx.obj['http_client'].instruments()
    click.echo("Your tradable instruments are:")
    click.echo('\n'.join(instrument["name"] for instrument in response))


@cli.command()
@click.pass_context
def balance(ctx):
    """
    This shows the available balances in the supported currencies.
    Your account balance is the net result of all your trade and settlement activity.
    A positive number indicates that B2C2 owes you the amount of the given currency.
    A negative number means that you owe B2C2 the given amount.
    """
    click.echo("Getting your balance..")
    response = ctx.obj['http_client'].balance()
    click.echo("Your balance is:")
    echo_dict(response)


@cli.command()
@click.pass_context
def account_info(ctx):
    """
    Returns generic account information related to trading: current risk exposure,
    maximum risk exposure and maximum quantity allowed per trade.
    Note that the risk exposure can be computed by doing the sum of all of the
    negative balances in USD.
    """
    click.echo("Getting your account information..")
    response = ctx.obj['http_client'].account_info()
    echo_dict(response)


MESSAGE_FOR_STATUS = {
    401: "You are not authorized to do this operation",
    403: "You are not allowed to do this operation",
    # The idea is to have custom messages per status code. For this test, I am not adding them all.
}


def show_http_error(exception: HTTPError):
    message = MESSAGE_FOR_STATUS.get(exception.response.status_code)
    click.secho(message, err=True, fg='red')
    try:
        json_response = exception.response.json()
    except JSONDecodeError:
        click.echo(exception, err=True)
        return
    for error in json_response.get('errors', []):
        if error['field'] == 'non_field_errors':
            click.secho(error['message'], err=True, fg='red')
            continue
        click.secho(f"{error['field']}: {error['message']}", err=True, fg='red')


if __name__ == '__main__':
    try:
        cli()
    except HTTPError as e:
        show_http_error(e)
    except RequestException as e:
        click.secho("The communication with the API failed. Please review the error below and try again", fg="red")
        click.echo(e)

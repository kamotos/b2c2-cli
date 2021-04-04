# b2c2-cli 

## Installation

```shell
python3 -m venv ./venv
source  ./venv/bin/activate
python setup.py install
```

## Unit tests

```shell
$ pytest
```


## Commands usage
- **API TOKEN**: the api token can be either passed to the command using an environment variable "API_TOKEN" or command option `--api-token`
- **--env**: Valid values are "sandbox" and "production" 

### rfq 
Request For Quote

```shell
Usage: b2c2-cli rfq [OPTIONS]

  Request For Quote and place and prompt the user to place an order if they
  want to.

Options:
  --instrument TEXT     Instrument as given by the /instruments/ endpoint.
                        [required]

  --side [buy|sell]     [required]
  --quantity DECIMAL    Quantity in base currency (maximum 4 decimals).
                        [required]

  --client-rfq-id TEXT  A universally unique identifier that will be returned
                        to you if the request succeeds.  [required]

  --help                Show this message and exit.
```

e.g:
```shell
API_TOKEN=e13e627c49705f83cbe7b60389ac411b6f86fee7 ENV=sandbox python b2c2/cli.py rfq --instrument BTCUSD --side buy --quantity 0.0005 --client-rfq-id 99
```

### balance

```shell
$ b2c2-cli balance --help

Usage: b2c2-cli balance [OPTIONS]

  This shows the available balances in the supported currencies. Your
  account balance is the net result of all your trade and settlement
  activity. A positive number indicates that B2C2 owes you the amount of the
  given currency. A negative number means that you owe B2C2 the given
  amount.

Options:
  --help  Show this message and exit.
```
#### Example result

```
b2c2-cli balance
Getting your balance..

Your balance is:
LTC: 352.1
USD: -56850.16557
ETH: 304.1
MXN: -1199800
UST: 581135.456
GBP: 33290.8462
CHF: -11027.003
SGD: 22462.9415
EOS: 121
XRP: 3056.5
BCH: -496.9815
BTC: 11.4587212
EUR: -17902.73846
CAD: 9091.098
JPY: 8875795.3
AUD: 41240.6042
NZD: -118638.816945
CNH: 0
DOT: 0
ETC: 0
LNK: 0
USC: 0
XAU: 0
XLM: 0
XMR: 0
```

### Account info
```shell
b2c2-cli account-info --help
Usage: b2c2-cli account-info [OPTIONS]

  Returns generic account information related to trading: current risk
  exposure, maximum risk exposure and maximum quantity allowed per trade.
  Note that the risk exposure can be computed by doing the sum of all of the
  negative balances in USD.

Options:
  --help  Show this message and exit.
 ```

### Instruments
```shell
b2c2-cli instruments --help
Usage: b2c2-cli instruments [OPTIONS]

  List all your tradable instruments.

Options:
  --help  Show this message and exit.
```

### Order 

```shell

$ b2c2-cli order --help

Usage: b2c2-cli order [OPTIONS]

Options:
  --client-order-id TEXT  A universally unique identifier that will be
                          returned to you in the response.  [required]

  --valid-until TEXT      Datetime field formatted “%Y-%m-%dT%H:%M:%S”.
                          [required]

  --instrument TEXT       Instrument as given by the /instruments/ endpoint.
                          [required]

  --side [buy|sell]       [required]
  --quantity DECIMAL      Quantity in base currency (maximum 4 decimals).
                          [required]

  --price TEXT            Price at which you want the order to be executed.
                          Only FOK.  [required]

  --help                  Show this message and exit
```
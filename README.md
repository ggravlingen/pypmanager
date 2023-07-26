### PyP(ortfolio)Manager

Summarize transactions in funds into a simple portfolio report.

### Why

I have been looking for a library where I can download a set of transactions from my broker and pension fund manager and compile them into a report giving me an overview of all holdings.

Alternative solutions expected me to store my data in the cloud. I don't want that, so I wrote this local-only library. The only thing cloud is that the library allows you to fetch market data from the Internet.

### Installing

There are other ways of getting this to work, this is how I use it:

- Clone the library from GitHub: `git clone https://github.com/ggravlingen/pypmanager.git`
- Install Docker Desktop
- Install `VSCode` from Microsoft and the `Dev Containers` extension.
- Open the library in VSCode and choose the option to open the folder in a container.

### Data format for transactions

There is currently support for three types of data: [Avanza](https://www.avanza.se/start), [Lysa](https://www.lysa.se/) and custom. For Avanza and Lysa, just download the transactions in CSV-format and place them in the `data`-folder in the root of this library.

The custom format allows you to run the calculations on any set of transactions as long as the correct format is followed:

```
transaction_date;transaction_type;name;isin_code;no_traded;price;amount;commission;currency
2021-02-15;buy;Fund A;NO0010000000;1000;100;-100000;-2,200;NOK
2021-02-15;sell;Fund A;NO0010000000;1000;100;100000;-2,200;NOK
```

Save the data as `other.csv` in the `data` folder.

#### Transaction format

`transaction_format` may be any of `buy`, `sell`, `interest`, `dividend` and `tax`.

### Downloading market data

I have provided a few data sources built-in. Configuration is done by appending `config/market_data.yaml` with the securities you want to download data for.

When the configuration file is updated, you can simply type `python -m pypmanager -l` to download all data.

### Running the library

In `VSCode`, click the `Run and debug` option. Press play next to `Python: FastAPI`. Navigate to http://localhost:8001/ in your browser.

### Some unimplemented ideas
- Calculate IRR per security and on a total.
- Split the overview by account or maybe tag.
- Investments made in other currencies
- Support other online brokers by extending the `DataLoader` class.
- <s>Adding scrapers to download historical closing data.</s>
- <s>Output the result as well-formatted HTML instead of in a CLI table.</s>
- <s>Allow setting an arbitrary date to calculate the value of the portfolio.</s>

### Architecture

#### Loading transactions

Transactions are loaded using a loader class in the `pypmanager.loader_transaction`. A loader class should inherit from the `pypmanager.loader_transaction.TransactionLoader` class, which does some normalising of data.

The helper function `pypmanager.helpers.load_transaction_files` merges data from all transaction loaders and return them as a dataframe.

#### Loading market data

The helper function `pypmanager.helpers.download_market_data` loads all sources in `config.market_data.yaml` and parses each source using its associated loader class. Each loader class should inherit from `pypmanager.loader_market_data.base_loader.BaseMarketDataLoader`. A loader class typically fetches data from a JSON endpoint or HTML-table and parses it so that it fits into the `pypmanager.loader_market_data.models.SourceData` dataclass.

Historical market data is written, rather naively, to the `data/market_data.csv` file.

#### The general ledger

The general ledger, which we can load using the helper `pypmanager.helpers.get_general_ledger`, is a Pandas dataframe. The dataframe contains each loaded transaction but split into separate components for the transaction's effect on your equity, cash balance, PnL, and so on.

Any PnL effect is written to the cash record of the general ledger.

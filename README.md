# PyLocalP(portfolio)Manager

Summarize transactions in funds into a simple portfolio report.

Available features:

- A transaction list: merge data from multiple sources into one transaction list.
- Profit- and loss statement: show the historical result from your transactions.

## Screenshots from app

Transaction list
![Screenshot of the transaction list.](/docs/assets/transaction_list.png)

Income statement:
![Screenshot of the general ledger.](/docs/assets/income_statement.png)

## Why

I have been looking for a library where I can download a set of transactions from my broker and pension fund manager use the merged data for analysis.

## Local-only data

Alternative solutions expected me to store my data in the cloud. I don't want that, so I wrote this library where your data is stored locally. The only thing cloud is that the library allows you to fetch market data from the Internet.

## Installing

There are other ways of getting this to work but this is how I use it:

- Clone the library from GitHub: `git clone https://github.com/ggravlingen/pypmanager.git`
- Install Docker Desktop
- Install `VSCode` from Microsoft and the `Dev Containers` extension.
- Open the library in VSCode and choose the option to open the folder in a container.
- Run the install script `./scipt/install.sh`.
- Start the server `uvicorn --port 8001 pypmanager.api:app` or, in VSCode, use `Run and Debug` and `Pypmanager server`.
- Browse to the transaction list on `http://localhost:8001/#/transaction`.

## Where to store your data

Your own data goes into the folder `data`. If you make contributions to this library, no files in this folder should be committed to the library.

## Market data (end-of-day prices on funds and equities)

This library is capable of calculating the current value of your portfolio. For this, we need end-of-day prices on funds and equities (market data).

I have provided a few data sources built-in. Download this data using `python -m pypmanager -l`.

Configuration is done by appending `pypmanager/configuration/market_data.yaml` with the securities you want to download data for.

Currently, there is support for loading data from the following sites:

- Morningstar
- The Financial Times
- Svenska Handelsbanken

## Unimplemented ideas

- Calculate IRR per security and on a total.
- Split the overview by account or maybe tag.
- Investments made in other currencies

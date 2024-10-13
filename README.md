# PyLocalP(portfolio)Manager

Summarize transactions in funds into a simple portfolio report.

Transaction list
![Screenshot of the transaction list.](/docs/assets/transaction_list.png)

Income statement:
![Screenshot of the general ledger.](/docs/assets/general_ledger.png)

## Why

I have been looking for a library where I can download a set of transactions from my broker and pension fund manager and compile them into a report giving me an overview of all holdings.

## Local-only data

Alternative solutions expected me to store my data in the cloud. I don't want that, so I wrote this library where your data is stored locally. The only thing cloud is that the library allows you to fetch market data from the Internet.

## Installing

There are other ways of getting this to work, this is how I use it:

- Clone the library from GitHub: `git clone https://github.com/ggravlingen/pypmanager.git`
- Install Docker Desktop
- Install `VSCode` from Microsoft and the `Dev Containers` extension.
- Open the library in VSCode and choose the option to open the folder in a container.
- Run the install script `./scipt/install.sh`.
- Start the server `uvicorn --port 8001 pypmanager.api:app`.
- Browse to the transaction list on `http://localhost:8001/#/transaction`.

## Market data (end-of-day prices on funds and equities)

This library is capable of calculating the current value of your portfolio. For this, we need end-of-day prices on funds and equities (market data)- I have provided a few data sources built-in. Download this data using `python -m pypmanager -l`.

Configuration is done by appending `pypmanager/configuration/market_data.yaml` with the securities you want to download data for.

### Data format for transactions

There is currently support for three types of data: [Avanza](https://www.avanza.se/start), [Lysa](https://www.lysa.se/) and custom. For Avanza and Lysa, just download the transactions in CSV-format and place them in the `data`-folder in the root of this library.

The custom format allows you to run the calculations on any set of transactions as long as the correct format is followed:

```csv
transaction_date;transaction_type;name;isin_code;no_traded;price;amount;commission;currency
2021-02-15;buy;Fund A;NO0010000000;1000;100;-100000;-2,200;NOK
2021-02-15;sell;Fund A;NO0010000000;1000;100;100000;-2,200;NOK
```

Save the data as `other.csv` in the `data` folder.

#### Transaction format

`transaction_format` may be any of `buy`, `sell`, `interest`, `dividend` and `tax`.

### Some unimplemented ideas

- Calculate IRR per security and on a total.
- Split the overview by account or maybe tag.
- Investments made in other currencies
- Support other online brokers by extending the `DataLoader` class.

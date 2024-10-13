# Your transaction data

This folder contains your transaction data and market data.

## Data format for transactions

There is currently support for three types of data: [Avanza](https://www.avanza.se/start), [Lysa](https://www.lysa.se/) and custom. For Avanza and Lysa, just download the transactions in CSV-format and place them in the `data`-folder in the root of this library.

The custom format allows you to run the calculations on any set of transactions as long as the correct format is followed:

```csv
source_transaction_date;source_transaction_type;source_name;source_isin_code;source_volume;source_price;amount;source_fee;source_currency;source_broker
2022-01-11;buy;Fund A;SE0005188836;200;345.00;;0;EUR;Broker
```

Save the data as `other.csv` in the `data/transactions` folder.

### Transaction type

`source_transaction_type` may be any of `buy`, `sell`, `interest`, `dividend` and `tax`.

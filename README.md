# Local Portfolio Manager

[![Coverage Status](https://coveralls.io/repos/github/ggravlingen/pypmanager/badge.svg?branch=main)](https://coveralls.io/github/ggravlingen/pypmanager?branch=main)

Summarize transactions in securities into a portfolio report tool.

Available features:

- Holdings overview: a table of your current holdings, and the market value of the positions.
- A transaction list: merge data from multiple sources into one transaction list.
- A transaction chart: show historical price data along with markers for purchases and divestments.
- Profit- and loss statement: show the historical result from your transactions.

## What is this exactly?

It's a web app running on your computer.

## Why

I've been looking for a library where I can download a set of transactions from my broker and pension fund manager use the merged data for analysis. When I couldn't find one, I decided to build it instead.

## No-cloud storage

Your data is stored locally. The only thing cloud is that the library allows you to fetch market data from the Internet.

## Screenshots from app

Click the images to view a larger version.

### Portfolio overview

![Screenshot of the general ledger.](/docs/assets/portfolio_overview.png)

### Transaction list

![Screenshot of the transaction list.](/docs/assets/transaction_list.png)

### Income statement

![Screenshot of the general ledger.](/docs/assets/income_statement.png)

## Installing

Choose one of the two options below. I'm personally using (1).

### (1) Running in VS Code

- Clone the library from GitHub: `git clone https://github.com/ggravlingen/pypmanager.git`
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on your computer.
- Install [VSCode](https://code.visualstudio.com/download) from Microsoft.
- Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
- Open the library in VSCode and choose the option to open the folder in a container.
- Run the install script by typing `./scipt/install.sh`.
- Start the server in VSCode by clicking `Run and Debug` and then `Pypmanager server`.
- Browse to the transaction list on `http://localhost:8001/#/transaction`.

### (2) Running as a stand-alone Docker service

- Build the Docker image file: `docker build . --tag pypmanager:latest`.
- Spin up a container and mount your data folders: `docker run -p 8001:8001 -v ./data:/code/app/data pypmanager:latest`.
- Browse to the transaction list on `http://localhost:8001/#/transaction`.

## How do add transactions

Your own data goes into the folder `data/transactions`. If you make contributions to this library, _no_ files from the `data` folder should be committed to the library as it contains your own, private, data.

## Market data (end-of-day prices on funds and equities)

This library is capable of calculating the current value of your portfolio. For this, we need end-of-day prices on funds and equities (market data).

I have provided a few data sources built-in. Download this data using `python -m pypmanager -l`.

Configuration is done by appending `pypmanager/configuration/market_data.yaml` with the securities you want to download data for.

Currently, there is support for loading data from the following sites:

- Morningstar
- The Financial Times
- Svenska Handelsbanken

Please feel free to subsmit your own data source.

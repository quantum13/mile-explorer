* Transactions
  - pagination
    - ~~prev/next/~~ goto date
  - filters
    - fee/no fee
    - with description
    - by wallet
  - in descr - address with reg node, rate with get rate, etc
* Transaction page
* Blocks
  - pagination
    - prev/next/goto block/goto date
  - filters
    - no empty blocks
* Block page
* Wallets
  - by date
  - top
    - total (miles*rate + xdr)
    - by miles
    - by xdr
    - by miles staked
    - by xdr staked
* Wallet page
  - last transactions and lint to transactions
* Exchanges
  - exchanges transactions
* Rate history (get rate)
  - current rate to home
* Charts
  - block producers income
* Strange tx
  - date
  - description
* wallet alias
* wallet comments
----
* Infra
  - docker compose
  - service
----
* Logging
  - response from api
  - stacktrace on exceptions (failed to get block by id: Block ID absent in database)
* Indexer
  - process dirty wallets 1 time/1min
  - fee & bp emission tx separated
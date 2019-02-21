* Search
  - ~~go to tx, wallet, block~~
* Transactions
  - pagination
    - ~~prev/next/~~ goto date
  - filters
    - ~~fee/no fee~~
    - with description
    - ~~by wallet~~
    - by type
  - in descr - address with reg node, rate with get rate, etc
* Transaction page
  - ~~first view~~
* Blocks
  - pagination
    - prev/next/goto block/goto date
  - filters
    - no empty blocks
* Block page
  - ~~first view~~
* Wallets
  - by date
  - top
    - total (miles*rate + xdr)
    - ~~by miles~~
    - ~~by xdr~~
    - by miles staked
    - by xdr staked
* Wallet page
  - ~~last transactions and link to transactions~~
  - node addr whois
* Exchanges
  - exchanges transactions
* Rate history (get rate)
  - current rate to home
* BP page
  - by fee income
  - by tx signed
* Charts & stats
  ! do not calc stat if more than 10 blocks unfetched
  - block producers income
  - total miles & xdr
  - total blocks by days
  - total bp income by days
  - interest rate for 100k staked
  - bp count (register-unregister)
  - registered bp, realy worked bp
* Strange tx
  - date
  - description
  - long period between blocks
* wallet alias
* wallet comments
----
* Infra
  - docker compose (nginx, ssl, redirects)
  - service
----
* Logging
  - response from api
  - stacktrace on exceptions (failed to get block by id: Block ID absent in database)
* Indexer
  - process dirty wallets 1 time/1min
  - fee & bp emission tx separated
  - ~~2 modes, start, work, different pool of pg~~
  !! healthcheck (1b miles)

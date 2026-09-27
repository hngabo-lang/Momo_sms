# MoMo SMS 

## Team Name: Data Wranglers
## Team Members
- Aristote Henry Ngabo
- Precious Amarachi Azubuike
- Griphen Mweene

## Overview
Parses MTN Mobile Money SMS transaction data (exported as XML), cleans and
categorizes it, loads it into SQLite, and serves it to a static dashboard.

## Our focus is
- Understanding the structure of the momo SMS XML data.
- Identifying the important information that needs to be stored.
- Designing the database and its relationships.
- Implementing the database using MySQL.
- Adding sample data for testing.
- Testing basic CRUD operations.
- Representing database information using JSON.
- Making sure the database maintains accurate and consistent data.

## Repository Structure

```text
Momo_sms/
├── api/
│   ├── server.py             # Custom http.server REST API implementation
│   └── transactions.json     # Data store backing the API endpoints
├── DSA/
│   ├── parse_xml.py          # XML SMS parsing script
│   └── search_benchmark.py   # DSA search algorithm benchmarking script
├── docs/
│   ├── api_docs.md           # API endpoint specifications and examples
│   └── erd_diagram.png       # Database ERD model
├── data/
│   ├── database_setup.sql    # Database schema definitions
│   └── momo_sms.db           # SQLite database instance
├── screenshots/              # Evidence screenshots for API test cases & DSA benchmark
│   ├── 01_successful_get_all.png
│   ├── 02_successful_get_by_id.png
│   ├── 03_unauthorized_request.png
│   ├── 04_successful_post.png
│   ├── 05_successful_put.png
│   ├── 06_successful_delete.png
│   └── 07_dsa_benchmark.png
├── README.md
└── requirements.txt
## Database
Stores mobile money transactions, client's data, transaction types, and system processing logs.

## Files

- `database/database_setup.sql` 
- `docs/erd_diagram.png` 
- `examples/json_schemas.json`

## Tables

**Users**: senders and receivers. One table, two roles.

**Transactions**: the money movements. Links to a sender and receiver, has an amount, date, and status.

**Transaction_Categories**: transaction types (People to People Transfer, Airtime Purchase, etc).

**Transaction_Category_Mapping**: junction table linking transactions to categories, since one transaction can have more than one category.

**System_Logs**: tracks what happened while a transaction was processed.

## Key design choices

- **UUIDs, not auto-increment IDs**: To avoid conflicts since data comes in from SMS, not a single controlled source.
- **One Users table for both roles**: the same person can be a sender in one transaction and a receiver in another.
- **Junction table for categories**: the standard fix for a many-to-many relationship.

## SQL -> JSON

Our JSON doesn't just copy the tables directly. Foreign keys like `sender_id` are replaced with the actual user details, and categories/logs are nested inside the transaction, so the data reads like a real API response instead of a raw database dump.

## Links
- Architecture diagram: https://miro.com/app/board/uXjVHq7ens8=/
- Trello board: https://trello.com/invite/b/6a993b48091b405a76a20cbb/ATTI13be4d226f0cd69cb75d38712ed8e966D7271BF2/enterprise-web-dev-project
- Lucidchart: https://lucid.app/lucidchart/0ce04555-5fe4-4c3f-9fee-26a182c7b652/edit?viewport_loc=216%2C-267%2C1495%2C649%2C0_0&invitationId=inv_92a4b0c0-f8cb-4805-9710-f49c9e62f109
- Link to SQL Database Implementation screenshots: https://docs.google.com/document/d/1Jzo0JaXtIp2ocGSjO2ETHiEebs29eiYS0Ln0mNBuYlM/edit?usp=sharing
- Link to the team task sheet: https://docs.google.com/spreadsheets/d/1S0xm5j8I43kKKTh2M_qVrZCBBK66oAN7SLFkv2QZU48/edit?usp=sharing
- Link to team task sheet formative 3: https://docs.google.com/spreadsheets/d/1iXm2f6r2NkduzjPPgUPX7PybRx1mIhQp8P6tP12SPvQ/edit?usp=sharing

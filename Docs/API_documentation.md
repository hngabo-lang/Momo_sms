# MoMo SMS API Documentation

**Base URL:** `http://localhost:8000`

**Auth:** Every endpoint requires HTTP Basic Auth:  username `user`, password `momo123`. Use `curl -u user:momo123 ...` like the examples below, or send `Authorization: Basic <base64(user:momo123)>` yourself.

> Examples use PowerShell's backtick (`` ` ``) for line continuation, since that's what `curl` on Windows needs. On macOS/Linux, swap the backtick for a backslash (`\`).

## Endpoints at a glance

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/transactions` | List all transactions |
| GET | `/transactions/{id}` | Get one transaction |
| POST | `/transactions` | Create a transaction |
| PUT | `/transactions/{id}` | Update a transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |

---

## GET /transactions

Returns the full list of transactions.

**Request**
```bash
curl -u user:momo123 http://localhost:8000/transactions
```

**Response — 200 OK**
```json
[
  {
    "id": 1,
    "type": "received_money",
    "amount": 2000,
    "fee": null,
    "balance": 2000,
    "sender": "Jane Smith",
    "receiver": "me",
    "phone": null,
    "transaction_ref": "76662021700",
    "timestamp": "10 May 2024 4:30:58 PM",
    "raw_body": "You have received 2000 RWF from Jane Smith..."
  }
]
```

**Errors**

| Code | Reason |
|---|---|
| 401 | Missing or wrong credentials |

---

## GET /transactions/{id}

Returns one transaction by id.

**Request**
```bash
curl -u user:momo123 http://localhost:8000/transactions/1
```

**Response — 200 OK**
```json
{
  "id": 1,
  "type": "received_money",
  "amount": 2000,
  "fee": null,
  "balance": 2000,
  "sender": "Jane Smith",
  "receiver": "me",
  "phone": null,
  "transaction_ref": "76662021700",
  "timestamp": "10 May 2024 4:30:58 PM",
  "raw_body": "You have received 2000 RWF from Jane Smith..."
}
```

**Errors**

| Code | Reason |
|---|---|
| 401 | Missing or wrong credentials |
| 404 | `{ "error": "Transaction 1 not found" }` |

---

## POST /transactions

Creates a new transaction. The server assigns the `id` — leave it out of the body, since anything you send gets overwritten anyway.

**Request**
```bash
curl -u user:momo123 -X POST http://localhost:8000/transactions `
  -H "Content-Type: application/json" `
  -d '{"type":"payment","amount":500,"fee":0,"balance":1500,"sender":"me","receiver":"Griphen Mweene","phone":null,"transaction_ref":"51732499999","timestamp":"26 Sep 2026 9:00:00 AM","raw_body":"TxId: 51732499999. Your payment of 500 RWF..."}'
```

**Response — 201 Created**
```json
{
  "id": 6,
  "type": "payment",
  "amount": 500,
  "fee": 0,
  "balance": 1500,
  "sender": "me",
  "receiver": "Griphen Mweene",
  "phone": null,
  "transaction_ref": "51732499999",
  "timestamp": "26 Sep 2026 9:00:00 AM",
  "raw_body": "TxId: 51732499999. Your payment of 500 RWF..."
}
```

**Errors**

| Code | Reason |
|---|---|
| 400 | Empty body, invalid JSON, or body isn't a JSON object |
| 401 | Missing or wrong credentials |

---

## PUT /transactions/{id}

Updates an existing transaction. Only send the fields you want changed, anything left out stays as it is. The `id` in the URL always wins over whatever's in the body.

**Request**
```bash
curl -u user:momo123 -X PUT http://localhost:8000/transactions/6 `
  -H "Content-Type: application/json" `
  -d '{"balance":1400}'
```

**Response — 200 OK**
```json
{
  "id": 6,
  "type": "payment",
  "amount": 500,
  "fee": 0,
  "balance": 1400,
  "sender": "me",
  "receiver": "Samuel Carter",
  "phone": null,
  "transaction_ref": "51732499999",
  "timestamp": "26 Sep 2026 9:00:00 AM",
  "raw_body": "TxId: 51732499999. Your payment of 500 RWF..."
}
```

**Errors**

| Code | Reason |
|---|---|
| 400 | Empty body, invalid JSON, or body isn't a JSON object |
| 401 | Missing or wrong credentials |
| 404 | `{ "error": "Transaction 6 not found" }` |

---

## DELETE /transactions/{id}

Deletes a transaction for good.

**Request**
```bash
curl -u user:momo123 -X DELETE http://localhost:8000/transactions/6
```

**Response — 200 OK**
```json
{ "message": "Transaction 6 deleted" }
```

**Errors**

| Code | Reason |
|---|---|
| 401 | Missing or wrong credentials |
| 404 | `{ "error": "Transaction 6 not found" }` |
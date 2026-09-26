
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DATA_FILE = "transactions.json"
LIST_PATH = "/transactions"
ID_PATH_RE = re.compile(r"^/transactions/(\d+)/?$")


def load_transactions(path=DATA_FILE):
    """Load transactions.json into a list (ordered) and a dict (by id)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    by_id = {t["id"]: t for t in data}
    return data, by_id


TRANSACTIONS, TRANSACTIONS_BY_ID = load_transactions()
NEXT_ID = max(TRANSACTIONS_BY_ID.keys(), default=0) + 1


def save_transactions(path=DATA_FILE):
    """Persist the current in-memory list back to disk."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(TRANSACTIONS, f, indent=2, ensure_ascii=False)


class TransactionHandler(BaseHTTPRequestHandler):

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        """Read and parse the request body as JSON.
        Returns (data, error_message) -- error_message is None on success."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None, "Request body is empty"
        raw = self.rfile.read(length)
        try:
            return json.loads(raw), None
        except json.JSONDecodeError:
            return None, "Request body is not valid JSON"

    # GET /transactions, GET /transactions/<id>
    def do_GET(self):
        path = urlparse(self.path).path

        if path == LIST_PATH:
            self._send_json(200, TRANSACTIONS)
            return

        match = ID_PATH_RE.match(path)
        if match:
            tx_id = int(match.group(1))
            transaction = TRANSACTIONS_BY_ID.get(tx_id)
            if transaction is None:
                self._send_json(404, {"error": f"Transaction {tx_id} not found"})
            else:
                self._send_json(200, transaction)
            return

        self._send_json(404, {"error": f"Unknown endpoint: GET {path}"})

    # POST /transactions
    def do_POST(self):
        global NEXT_ID
        path = urlparse(self.path).path

        if path != LIST_PATH:
            self._send_json(404, {"error": f"Unknown endpoint: POST {path}"})
            return

        data, err = self._read_json_body()
        if err:
            self._send_json(400, {"error": err})
            return
        if not isinstance(data, dict):
            self._send_json(400, {"error": "Request body must be a JSON object"})
            return

        new_transaction = dict(data)
        new_transaction["id"] = NEXT_ID
        TRANSACTIONS.append(new_transaction)
        TRANSACTIONS_BY_ID[NEXT_ID] = new_transaction
        NEXT_ID += 1
        save_transactions()

        self._send_json(201, new_transaction)

    # PUT /transactions/<id>
    def do_PUT(self):
        path = urlparse(self.path).path
        match = ID_PATH_RE.match(path)
        if not match:
            self._send_json(404, {"error": f"Unknown endpoint: PUT {path}"})
            return

        tx_id = int(match.group(1))
        if tx_id not in TRANSACTIONS_BY_ID:
            self._send_json(404, {"error": f"Transaction {tx_id} not found"})
            return

        data, err = self._read_json_body()
        if err:
            self._send_json(400, {"error": err})
            return
        if not isinstance(data, dict):
            self._send_json(400, {"error": "Request body must be a JSON object"})
            return

        transaction = TRANSACTIONS_BY_ID[tx_id]
        transaction.update(data)
        transaction["id"] = tx_id  # the id in the URL always wins over the body
        save_transactions()

        self._send_json(200, transaction)

    # DELETE /transactions/<id>
    def do_DELETE(self):
        path = urlparse(self.path).path
        match = ID_PATH_RE.match(path)
        if not match:
            self._send_json(404, {"error": f"Unknown endpoint: DELETE {path}"})
            return

        tx_id = int(match.group(1))
        if tx_id not in TRANSACTIONS_BY_ID:
            self._send_json(404, {"error": f"Transaction {tx_id} not found"})
            return

        transaction = TRANSACTIONS_BY_ID.pop(tx_id)
        TRANSACTIONS.remove(transaction)
        save_transactions()

        self._send_json(200, {"message": f"Transaction {tx_id} deleted"})


def run(port=8000):
    server = HTTPServer(("0.0.0.0", port), TransactionHandler)
    print(f"Serving on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run()

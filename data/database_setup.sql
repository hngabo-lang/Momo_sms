-- Active: 1789244491841@@127.0.0.1@3306
-- CREATE DATABASE IF NOT EXISTS momo_sms_db;
-- USE momo_sms_db;

CREATE TABLE IF NOT EXISTS Users (
    user_id VARCHAR(36) PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role TEXT NOT NULL DEFAULT 'both',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    sender_id VARCHAR(36) NOT NULL,
    receiver_id VARCHAR(36) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_date DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    raw_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tx_sender FOREIGN KEY (sender_id) REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tx_receiver FOREIGN KEY (receiver_id) REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_tx_amount CHECK (amount > 0)
);

CREATE TABLE IF NOT EXISTS Transaction_Categories (
    category_id VARCHAR(36) PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Transaction_Category_Mapping (
    transaction_id VARCHAR(36) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    tagged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, category_id),
    CONSTRAINT fk_map_tx FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_map_cat FOREIGN KEY (category_id) REFERENCES Transaction_Categories(category_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS System_Logs (
    log_id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36),
    log_level TEXT NOT NULL DEFAULT 'INFO',
    source_stage VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_tx FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_users_phone ON Users(phone_number);
CREATE INDEX idx_tx_date ON Transactions(transaction_date);
CREATE INDEX idx_tx_status ON Transactions(status);
CREATE INDEX idx_logs_level ON System_Logs(log_level);

INSERT INTO Users (user_id, phone_number, full_name, role) VALUES
('u001-uuid-0000-0001', '+250788000001', 'Alice Umutoni', 'sender'),
('u002-uuid-0000-0002', '+250788000002', 'Bob Mugisha', 'receiver'),
('u003-uuid-0000-0003', '+250788000003', 'Charlie Keza', 'both'),
('u004-uuid-0000-0004', '+250788000004', 'David Niyomugabo', 'both'),
('u005-uuid-0000-0005', '+250788000005', 'Eva Iradukunda', 'receiver');

INSERT INTO Transaction_Categories (category_id, category_name, description) VALUES
('c001-uuid-0000-0001', 'P2P Transfer', 'Person-to-person money transfer'),
('c002-uuid-0000-0002', 'Airtime Purchase', 'Airtime recharge via Mobile Money'),
('c003-uuid-0000-0003', 'Merchant Payment', 'Retail shop or service payment'),
('c004-uuid-0000-0004', 'Utility Bill', 'Electricity or water bill settlement'),
('c005-uuid-0000-0005', 'Bank Deposit', 'Transfer from mobile wallet to bank account');

INSERT INTO Transactions (transaction_id, sender_id, receiver_id, amount, transaction_date, status, raw_message) VALUES
('t001-uuid-0000-0001', 'u001-uuid-0000-0001', 'u002-uuid-0000-0002', 5000.00, '2026-03-01 10:15:00', 'completed', 'TxId: 101, Sent 5000 RWF to Bob'),
('t002-uuid-0000-0002', 'u003-uuid-0000-0003', 'u004-uuid-0000-0004', 12500.50, '2026-03-01 11:20:00', 'completed', 'TxId: 102, Sent 12500.5 RWF to David'),
('t003-uuid-0000-0003', 'u001-uuid-0000-0001', 'u005-uuid-0000-0005', 2000.00, '2026-03-02 08:05:00', 'failed', 'TxId: 103, Failed transfer to Eva'),
('t004-uuid-0000-0004', 'u004-uuid-0000-0004', 'u002-uuid-0000-0002', 45000.00, '2026-03-02 09:45:00', 'completed', 'TxId: 104, Payment to Bob'),
('t005-uuid-0000-0005', 'u003-uuid-0000-0003', 'u001-uuid-0000-0001', 1000.00, '2026-03-02 14:10:00', 'pending', 'TxId: 105, Airtime top-up pending');

INSERT INTO Transaction_Category_Mapping (transaction_id, category_id) VALUES
('t001-uuid-0000-0001', 'c001-uuid-0000-0001'),
('t002-uuid-0000-0002', 'c001-uuid-0000-0001'),
('t003-uuid-0000-0003', 'c001-uuid-0000-0001'),
('t004-uuid-0000-0004', 'c003-uuid-0000-0003'),
('t005-uuid-0000-0005', 'c002-uuid-0000-0002');

INSERT INTO System_Logs (log_id, transaction_id, log_level, source_stage, message) VALUES
('l001-uuid-0000-0001', 't001-uuid-0000-0001', 'INFO', 'XML_PARSER', 'Successfully parsed MoMo SMS XML'),
('l002-uuid-0000-0002', 't002-uuid-0000-0002', 'INFO', 'DB_INGESTION', 'Transaction record committed'),
('l003-uuid-0000-0003', 't003-uuid-0000-0003', 'ERROR', 'PAYMENT_GATEWAY', 'Insufficient balance on sender wallet'),
('l004-uuid-0000-0004', 't004-uuid-0000-0004', 'INFO', 'DB_INGESTION', 'Merchant payment logged'),
('l005-uuid-0000-0005', 't005-uuid-0000-0005', 'WARNING', 'NETWORK_HANDLER', 'Timeout waiting for gateway callback');

INSERT INTO Users (user_id, phone_number, full_name, role) 
VALUES ('u006-uuid-0000-0006', '+250788000006', 'Frank Habimana', 'sender');

SELECT 
    t.transaction_id,
    s.full_name AS sender,
    r.full_name AS receiver,
    t.amount,
    t.status,
    t.transaction_date
FROM Transactions t
JOIN Users s ON t.sender_id = s.user_id
JOIN Users r ON t.receiver_id = r.user_id;

UPDATE Transactions 
SET status = 'completed' 
WHERE transaction_id = 't005-uuid-0000-0005';

DELETE FROM System_Logs 
WHERE log_id = 'l005-uuid-0000-0005';
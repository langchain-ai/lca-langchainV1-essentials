#!/usr/bin/env python3
"""Generate a synthetic BankingDemo.db suitable for the LangChain demo.
Creates tables: branch, customer, account, transaction, card, loan
Produces 12 customers, 4 branches, ~30-40 accounts, and transaction history.
"""
import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join('python', 'BankingDemo.db')
random.seed(42)

def iso(d):
    return d.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    # Create tables
    cur.executescript('''
    CREATE TABLE branch (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        state TEXT,
        opened_date TEXT
    );

    CREATE TABLE customer (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE account (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_number TEXT NOT NULL UNIQUE,
        customer_id INTEGER NOT NULL,
        branch_id INTEGER,
        account_type TEXT NOT NULL,
        currency TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 0.0,
        opened_date TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY(branch_id) REFERENCES branch(branch_id)
    );

    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        txn_type TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        txn_date TEXT NOT NULL,
        description TEXT,
        balance_after REAL,
        FOREIGN KEY(account_id) REFERENCES account(account_id)
    );

    CREATE TABLE card (
        card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_number_mask TEXT NOT NULL,
        customer_id INTEGER NOT NULL,
        account_id INTEGER,
        card_type TEXT NOT NULL,
        expiry TEXT,
        FOREIGN KEY(customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY(account_id) REFERENCES account(account_id)
    );

    CREATE TABLE loan (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        loan_type TEXT NOT NULL,
        principal REAL NOT NULL,
        balance REAL NOT NULL,
        opened_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
    );
    ''')

    # Insert branches
    branches = [
        ('Downtown Branch', 'Metropolis', 'NY', datetime.now() - timedelta(days=3650)),
        ('Uptown Branch', 'Metropolis', 'NY', datetime.now() - timedelta(days=2000)),
        ('Suburban Branch', 'Springfield', 'IL', datetime.now() - timedelta(days=1500)),
        ('Airport Branch', 'Gateway', 'CA', datetime.now() - timedelta(days=800)),
    ]
    for name, city, state, opened in branches:
        cur.execute('INSERT INTO branch (name, city, state, opened_date) VALUES (?, ?, ?, ?)',
                    (name, city, state, iso(opened)))

    # Customers (12)
    customers = [
        ('Alice','Johnson'),('Bob','Smith'),('Carol','Davis'),('David','Miller'),
        ('Eve','Wilson'),('Frank','Brown'),('Grace','Moore'),('Hank','Taylor'),
        ('Ivy','Anderson'),('Jack','Thomas'),('Kara','Jackson'),('Liam','White')
    ]
    now = datetime.now()
    for fn, ln in customers:
        created = now - timedelta(days=random.randint(30, 2000))
        email = f"{fn.lower()}.{ln.lower()}@example.com"
        phone = f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
        cur.execute('INSERT INTO customer (first_name,last_name,email,phone,created_at) VALUES (?,?,?,?,?)',
                    (fn, ln, email, phone, iso(created)))

    # Create accounts for each customer (1-3 accounts)
    cur.execute('SELECT customer_id FROM customer')
    customer_ids = [r[0] for r in cur.fetchall()]
    account_seq = 10000000
    account_rows = []
    for cid in customer_ids:
        num_accounts = random.randint(1,3)
        for _ in range(num_accounts):
            account_seq += 1
            acc_num = f'AC{account_seq}'
            branch_id = random.choice([1,2,3,4])
            a_type = random.choice(['checking','savings'])
            opened = now - timedelta(days=random.randint(10, 2000))
            balance = round(random.uniform(50.0, 20000.0),2)
            cur.execute('INSERT INTO account (account_number, customer_id, branch_id, account_type, currency, balance, opened_date) VALUES (?,?,?,?,?,?,?)',
                        (acc_num, cid, branch_id, a_type, 'USD', balance, iso(opened)))
            account_rows.append((cur.lastrowid, balance))

    # Transactions per account
    descriptions = ['ATM withdrawal','Direct deposit','POS purchase','Bill payment','ACH transfer','Fee']
    for account_id, starting_balance in account_rows:
        # create a baseline: 30-80 transactions
        txn_count = random.randint(30,80)
        # create transactions backwards in time then sort ascending
        txns = []
        base_date = now - timedelta(days=random.randint(10, 1000))
        balance = starting_balance
        for i in range(txn_count):
            # each txn 0-30 days apart
            base_date += timedelta(days=random.randint(0,10))
            txn_type = random.choices(['credit','debit','fee'], weights=[0.35,0.6,0.05])[0]
            amount = round(random.uniform(1.0, 2000.0),2)
            if txn_type == 'debit' or txn_type == 'fee':
                balance_after = round(balance - amount,2)
            else:
                balance_after = round(balance + amount,2)
            desc = random.choice(descriptions)
            txns.append((account_id, txn_type, amount, 'USD', iso(base_date), desc, balance_after))
            balance = balance_after
        # insert txns
        cur.executemany('INSERT INTO transactions (account_id, txn_type, amount, currency, txn_date, description, balance_after) VALUES (?,?,?,?,?,?,?)', txns)

    # Create cards for some customers
    card_count = 0
    for cid in customer_ids:
        if random.random() < 0.7:  # 70% customers have at least one card
            num_cards = random.choice([1,1,2])
            for _ in range(num_cards):
                card_count += 1
                last4 = random.randint(1000,9999)
                mask = f'XXXX-XXXX-XXXX-{last4}'
                # link to a random account of the customer if exists
                cur.execute('SELECT account_id FROM account WHERE customer_id = ? LIMIT 1', (cid,))
                row = cur.fetchone()
                acc_id = row[0] if row else None
                expiry = (now + timedelta(days=random.randint(365,365*5))).strftime('%m/%y')
                cur.execute('INSERT INTO card (card_number_mask, customer_id, account_id, card_type, expiry) VALUES (?,?,?,?,?)',
                            (mask, cid, acc_id, random.choice(['debit','credit']), expiry))

    # Create a few loans
    loan_types = ['personal','auto','mortgage']
    for _ in range(6):
        cid = random.choice(customer_ids)
        ltype = random.choice(loan_types)
        principal = round(random.uniform(5000,250000),2)
        balance = round(principal * random.uniform(0.1,0.9),2)
        opened = now - timedelta(days=random.randint(100,3000))
        status = random.choice(['active','closed'])
        cur.execute('INSERT INTO loan (customer_id, loan_type, principal, balance, opened_date, status) VALUES (?,?,?,?,?,?)',
                    (cid, ltype, principal, balance, iso(opened), status))

    conn.commit()
    # Create some indexes to improve demo queries
    cur.executescript('''
    CREATE INDEX IF NOT EXISTS idx_account_customer ON account(customer_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_account_number ON account(account_number);
    CREATE INDEX IF NOT EXISTS idx_account_branch ON account(branch_id);
    CREATE INDEX IF NOT EXISTS idx_txn_account_date ON transactions(account_id, txn_date);
    CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(txn_date);
    CREATE INDEX IF NOT EXISTS idx_card_customer ON card(customer_id);
    CREATE INDEX IF NOT EXISTS idx_loan_customer ON loan(customer_id);
    ''')
    conn.commit()

    # Print summary
    for table in ['branch','customer','account','transactions','card','loan']:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        print(f"{table}:", cur.fetchone()[0])

    conn.close()
    print('\nCreated DB at', DB_PATH)

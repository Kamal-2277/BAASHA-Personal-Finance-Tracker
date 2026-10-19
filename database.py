"""
BAASHA Personal Finance Tracker - Database Module
Handles SQLite schema, migrations, CRUD operations, and intelligent demo data seeding.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'baasha_finance.db')

DEFAULT_CATEGORIES = {
    'income': [
        'Salary',
        'Freelance / Consulting',
        'Investments & Dividends',
        'Business Revenue',
        'Scholarship / Stipend',
        'Gifts / Allowance',
        'Other Income'
    ],
    'expense': [
        'Food & Dining',
        'Rent & Housing',
        'Groceries',
        'Transportation / Fuel',
        'Utilities & Bills',
        'Entertainment & Outing',
        'Shopping & Lifestyle',
        'Health & Medical',
        'Education & Courses',
        'Subscriptions',
        'Miscellaneous'
    ]
}

PAYMENT_METHODS = ['UPI / GPay / PhonePe', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash']

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                name TEXT,
                dob TEXT,
                monthly_salary REAL DEFAULT 0,
                has_business INTEGER DEFAULT 0,
                business_name TEXT,
                business_income REAL DEFAULT 0,
                total_monthly_income REAL DEFAULT 0,
                annual_income_lpa REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Transactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'UPI / GPay / PhonePe',
                description TEXT,
                is_recurring INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Category Budgets Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                budget_amount REAL NOT NULL
            )
        ''')
        
        # Check & migrate user_id column in transactions if missing
        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN user_id INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass
        
        # Savings Goals Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date TEXT,
                category TEXT DEFAULT 'General'
            )
        ''')
        
        # Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Default Settings
        default_settings = [
            ('currency_symbol', '₹'),
            ('currency_code', 'INR'),
            ('monthly_budget', '45000'),
            ('emergency_fund_target', '150000'),
            ('user_name', 'BAASHA User')
        ]
        
        for key, val in default_settings:
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, val))
            
        conn.commit()

    # Seed sample data if transactions table is empty
    check_and_seed()

def check_and_seed():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM transactions')
        count = cursor.fetchone()[0]
        if count == 0:
            seed_sample_data()

def seed_sample_data():
    """Generates a rich, realistic history of transactions spanning past 10 months and current week."""
    today = date.today()
    sample_records = []
    
    # Generate incomes for previous 6-8 months (Salary on 1st of each month)
    for m in range(7, -1, -1):
        # Calculate approximate month date
        month_date = (today.replace(day=1) - timedelta(days=m * 30)).replace(day=1)
        month_str = month_date.strftime('%Y-%m-%d')
        sample_records.append((
            'income', 'Salary', 58000.0, month_str, 'Net Banking', 'Monthly Professional Salary', 1
        ))
        if m % 2 == 0:
            sample_records.append((
                'income', 'Freelance / Consulting', random.choice([7500.0, 12000.0, 9500.0]),
                (month_date + timedelta(days=14)).strftime('%Y-%m-%d'), 'UPI / GPay / PhonePe', 'Web Development Client Project', 0
            ))
        if m % 3 == 0:
            sample_records.append((
                'income', 'Investments & Dividends', random.choice([1500.0, 3200.0, 2400.0]),
                (month_date + timedelta(days=22)).strftime('%Y-%m-%d'), 'Net Banking', 'Mutual Fund & Stock Dividends', 0
            ))
            
    # Regular monthly expenses for past 6 months
    for m in range(6, 0, -1):
        m_base = (today.replace(day=1) - timedelta(days=m * 30)).replace(day=1)
        # Rent
        sample_records.append((
            'expense', 'Rent & Housing', 14000.0, (m_base + timedelta(days=3)).strftime('%Y-%m-%d'),
            'Net Banking', 'Monthly Apartment Rent', 1
        ))
        # Utilities
        sample_records.append((
            'expense', 'Utilities & Bills', random.choice([2400.0, 2900.0, 3100.0]), (m_base + timedelta(days=5)).strftime('%Y-%m-%d'),
            'UPI / GPay / PhonePe', 'Electricity, Gas & WiFi Bill', 1
        ))
        # Groceries
        for w in [7, 14, 21]:
            sample_records.append((
                'expense', 'Groceries', random.choice([2800.0, 3400.0, 3900.0]), (m_base + timedelta(days=w)).strftime('%Y-%m-%d'),
                'Debit Card', 'Supermarket & Weekly Vegetables', 0
            ))
        # Food & Dining
        for d in [9, 16, 23, 27]:
            sample_records.append((
                'expense', 'Food & Dining', random.choice([650.0, 1100.0, 850.0, 1450.0]), (m_base + timedelta(days=d)).strftime('%Y-%m-%d'),
                'UPI / GPay / PhonePe', 'Dinner outing & Swiggy/Zomato', 0
            ))
        # Fuel / Transportation
        for d in [8, 19]:
            sample_records.append((
                'expense', 'Transportation / Fuel', random.choice([1200.0, 1500.0]), (m_base + timedelta(days=d)).strftime('%Y-%m-%d'),
                'Credit Card', 'Petrol & Metro Smart Card Recharge', 0
            ))
        # Subscriptions
        sample_records.append((
            'expense', 'Subscriptions', 1199.0, (m_base + timedelta(days=10)).strftime('%Y-%m-%d'),
            'Credit Card', 'Netflix & Spotify Premium', 1
        ))
        
    # Current Month Rich Data (Days 1 to today)
    curr_first = today.replace(day=1)
    sample_records.append((
        'income', 'Salary', 60000.0, curr_first.strftime('%Y-%m-%d'), 'Net Banking', 'Monthly Salary Deposit', 1
    ))
    sample_records.append((
        'income', 'Freelance / Consulting', 14500.0, (curr_first + timedelta(days=4)).strftime('%Y-%m-%d'), 'UPI / GPay / PhonePe', 'College Project Consulting Fee', 0
    ))
    sample_records.append((
        'expense', 'Rent & Housing', 14000.0, (curr_first + timedelta(days=2)).strftime('%Y-%m-%d'), 'Net Banking', 'Monthly Flat Rent', 1
    ))
    sample_records.append((
        'expense', 'Utilities & Bills', 2850.0, (curr_first + timedelta(days=4)).strftime('%Y-%m-%d'), 'UPI / GPay / PhonePe', 'Electricity & High-speed Fiber Internet', 1
    ))
    sample_records.append((
        'expense', 'Subscriptions', 1199.0, (curr_first + timedelta(days=6)).strftime('%Y-%m-%d'), 'Credit Card', 'Netflix, Spotify & Cloud Storage', 1
    ))

    # Dense week data leading up to today (Weekly graph showcase)
    recent_events = [
        (6, 'expense', 'Food & Dining', 750.0, 'UPI / GPay / PhonePe', 'Weekend Lunch with Friends'),
        (5, 'expense', 'Groceries', 2650.0, 'Debit Card', 'Weekly Essentials & Fruits'),
        (4, 'expense', 'Transportation / Fuel', 1200.0, 'Credit Card', 'Bike / Car Petrol Fill-up'),
        (3, 'expense', 'Shopping & Lifestyle', 3499.0, 'Credit Card', 'New Running Shoes & T-Shirt'),
        (2, 'expense', 'Food & Dining', 620.0, 'UPI / GPay / PhonePe', 'Evening Snacks & Cafe Latte'),
        (1, 'expense', 'Health & Medical', 850.0, 'UPI / GPay / PhonePe', 'Multivitamins & Medical Consultation'),
        (0, 'expense', 'Food & Dining', 420.0, 'UPI / GPay / PhonePe', 'Quick Lunch with Colleagues'),
    ]
    
    for days_ago, t_type, cat, amt, p_method, desc in recent_events:
        t_date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        sample_records.append((t_type, cat, amt, t_date, p_method, desc, 0))

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO transactions (type, category, amount, date, payment_method, description, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_records)
        
        # Sample Savings Goals
        cursor.execute('DELETE FROM savings_goals')
        goals = [
            ('Emergency Fund Reserve', 150000.0, 92000.0, (today + timedelta(days=180)).strftime('%Y-%m-%d'), 'Emergency'),
            ('Tech Upgrade / Laptop', 85000.0, 55000.0, (today + timedelta(days=90)).strftime('%Y-%m-%d'), 'Gadgets'),
            ('Goa Roadtrip with Friends', 25000.0, 18500.0, (today + timedelta(days=45)).strftime('%Y-%m-%d'), 'Travel')
        ]
        cursor.executemany('''
            INSERT INTO savings_goals (title, target_amount, current_amount, target_date, category)
            VALUES (?, ?, ?, ?, ?)
        ''', goals)
        
        # Default Category Budgets
        cursor.execute('DELETE FROM category_budgets')
        cat_budgets = [
            ('Food & Dining', 8000.0),
            ('Rent & Housing', 15000.0),
            ('Groceries', 10000.0),
            ('Transportation / Fuel', 4000.0),
            ('Utilities & Bills', 4000.0),
            ('Entertainment & Outing', 4000.0),
            ('Shopping & Lifestyle', 6000.0),
        ]
        cursor.executemany('''
            INSERT INTO category_budgets (category, budget_amount)
            VALUES (?, ?)
        ''', cat_budgets)
        
        conn.commit()

def reset_to_sample():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        cursor.execute('DELETE FROM savings_goals')
        cursor.execute('DELETE FROM category_budgets')
        conn.commit()
    seed_sample_data()

def clear_all():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()

def add_transaction(t_type, category, amount, date_str, payment_method, description, is_recurring=0):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (type, category, amount, date, payment_method, description, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (t_type, category, float(amount), date_str, payment_method, description, 1 if is_recurring else 0))
        conn.commit()
        return cursor.lastrowid

def update_transaction(t_id, t_type, category, amount, date_str, payment_method, description, is_recurring=0):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET type = ?, category = ?, amount = ?, date = ?, payment_method = ?, description = ?, is_recurring = ?
            WHERE id = ?
        ''', (t_type, category, float(amount), date_str, payment_method, description, 1 if is_recurring else 0, t_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_transaction(t_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE id = ?', (t_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_transaction(t_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (t_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_filtered_transactions(t_type=None, category=None, start_date=None, end_date=None, search=None, sort='date_desc', limit=None, offset=None):
    query = 'SELECT * FROM transactions WHERE 1=1'
    params = []
    
    if t_type and t_type != 'all':
        query += ' AND type = ?'
        params.append(t_type)
        
    if category and category != 'all':
        query += ' AND category = ?'
        params.append(category)
        
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
        
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
        
    if search:
        query += ' AND (description LIKE ? OR category LIKE ? OR payment_method LIKE ?)'
        like_str = f'%{search}%'
        params.extend([like_str, like_str, like_str])
        
    if sort == 'date_asc':
        query += ' ORDER BY date ASC, id ASC'
    elif sort == 'amount_desc':
        query += ' ORDER BY amount DESC'
    elif sort == 'amount_asc':
        query += ' ORDER BY amount ASC'
    else:
        query += ' ORDER BY date DESC, id DESC'
        
    if limit is not None:
        query += ' LIMIT ?'
        params.append(limit)
        if offset is not None:
            query += ' OFFSET ?'
            params.append(offset)
            
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_setting(key, default=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else default

def update_setting(key, value):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
        conn.commit()

def get_savings_goals():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM savings_goals ORDER BY target_date ASC')
        return [dict(r) for r in cursor.fetchall()]

def add_savings_goal(title, target_amount, current_amount, target_date, category='General'):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO savings_goals (title, target_amount, current_amount, target_date, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, float(target_amount), float(current_amount), target_date, category))
        conn.commit()

def update_goal_progress(goal_id, current_amount):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE savings_goals SET current_amount = ? WHERE id = ?', (float(current_amount), goal_id))
        conn.commit()

def delete_savings_goal(goal_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM savings_goals WHERE id = ?', (goal_id,))
        conn.commit()

# ----------------- USER PROFILE OPERATIONS ----------------- #

def get_user_by_phone(phone):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_latest_user():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        return dict(row) if row else None

def create_or_update_user(phone, name, dob, monthly_salary, has_business=0, business_name='', business_income=0.0, reset_spending=True):
    """
    Creates or updates a user profile.
    Calculates total monthly income and converts to LPA (Lakhs Per Annum).
    If reset_spending is True, clears previous demo expenses and inserts fresh monthly incomes.
    """
    salary = float(monthly_salary or 0)
    biz_income = float(business_income or 0) if has_business else 0.0
    total_monthly = salary + biz_income
    
    # Calculate LPA: (Monthly Income * 12) / 1,00,000
    annual_income_lpa = round((total_monthly * 12) / 100000.0, 2)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (phone, name, dob, monthly_salary, has_business, business_name, business_income, total_monthly_income, annual_income_lpa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET
                name=excluded.name,
                dob=excluded.dob,
                monthly_salary=excluded.monthly_salary,
                has_business=excluded.has_business,
                business_name=excluded.business_name,
                business_income=excluded.business_income,
                total_monthly_income=excluded.total_monthly_income,
                annual_income_lpa=excluded.annual_income_lpa
        ''', (phone, name, dob, salary, 1 if has_business else 0, business_name, biz_income, total_monthly, annual_income_lpa))
        conn.commit()
        
        cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
        user_row = cursor.fetchone()
        user_id = user_row[0] if user_row else 1

    # Update default user_name setting
    update_setting('user_name', name)
    update_setting('annual_income_lpa', str(annual_income_lpa))

    if reset_spending:
        # User requested: "spending should be as there is no new transcation set"
        # Clear transactions and insert initial clean income transactions
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions')
            
            today_str = date.today().strftime('%Y-%m-%d')
            # Add Primary Salary
            if salary > 0:
                cursor.execute('''
                    INSERT INTO transactions (user_id, type, category, amount, date, payment_method, description, is_recurring)
                    VALUES (?, 'income', 'Salary', ?, ?, 'Net Banking', 'Primary Monthly Salary', 1)
                ''', (user_id, salary, today_str))
            
            # Add Business Revenue if added
            if has_business and biz_income > 0:
                desc = f'Business Revenue ({business_name})' if business_name else 'Secondary Business Income'
                cursor.execute('''
                    INSERT INTO transactions (user_id, type, category, amount, date, payment_method, description, is_recurring)
                    VALUES (?, 'income', 'Business Revenue', ?, ?, 'Net Banking', ?, 1)
                ''', (user_id, biz_income, today_str, desc))
                
            conn.commit()

    return user_id

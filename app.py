"""
BAASHA Personal Finance Tracker - Main Web Application
Flask backend server with API endpoints, template rendering, and CSV exports.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response, session
import io
import csv
import random
from datetime import datetime, date
import database
import analytics

app = Flask(__name__)
app.secret_key = 'baasha-finance-tracker-secret-key-2026'

# Initialize database schema and initial data
database.init_db()

# Register zip in Jinja environment
app.jinja_env.globals.update(zip=zip)
app.jinja_env.filters['zip'] = zip

@app.before_request
def check_authentication():
    """Ensure user enters their details on the login page before accessing financial pages."""
    public_endpoints = {
        'login', 'login_post_route', 
        'logout_route', 'static', 'about'
    }
    if request.endpoint and request.endpoint in public_endpoints:
        return None
        
    if not session.get('user_id'):
        return redirect(url_for('login'))

@app.context_processor
def inject_global_data():
    """Make currency, current date, and active user profile available to all templates."""
    currency_symbol = database.get_setting('currency_symbol', '₹')
    today_str = date.today().strftime('%Y-%m-%d')
    current_year = date.today().year
    current_month = date.today().month
    
    current_user = None
    if session.get('user_id'):
        current_user = database.get_user_by_id(session['user_id'])
    elif session.get('phone'):
        current_user = database.get_user_by_phone(session['phone'])
        
    return {
        'currency': currency_symbol,
        'today': today_str,
        'current_year': current_year,
        'current_month': current_month,
        'categories': database.DEFAULT_CATEGORIES,
        'payment_methods': database.PAYMENT_METHODS,
        'current_user': current_user
    }

# ----------------- AUTHENTICATION ROUTES ----------------- #

@app.route('/login', methods=['GET'])
def login():
    """Direct entry login page asking for Name, DOB, Monthly Salary, and Business."""
    session['logged_out'] = False
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post_route():
    """Direct profile setup: saves user, calculates LPA, resets spending slate."""
    name = request.form.get('name', '').strip()
    dob = request.form.get('dob', '').strip()
    monthly_salary = float(request.form.get('monthly_salary', 0) or 0)
    has_business = 1 if request.form.get('has_business') else 0
    business_name = request.form.get('business_name', '').strip()
    business_income = float(request.form.get('business_income', 0) or 0)

    if not name:
        flash('Please enter your name.', 'error')
        return redirect(url_for('login'))

    user_key = name.strip().lower().replace(' ', '_')
    user_id = database.create_or_update_user(
        phone=user_key,
        name=name,
        dob=dob,
        monthly_salary=monthly_salary,
        has_business=has_business,
        business_name=business_name,
        business_income=business_income,
        reset_spending=True
    )

    session['user_id'] = user_id
    session['user_name'] = name
    session['phone'] = user_key
    session['logged_out'] = False

    user = database.get_user_by_id(user_id)
    lpa_str = f"{user['annual_income_lpa']} LPA" if user else "Calculated"
    flash(f'Welcome, {name}! Annual Income: {lpa_str}. Spending slate is ready with 0 new transactions.', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout_route():
    """Signs out current user session."""
    session.clear()
    session['logged_out'] = True
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('login'))

# ----------------- PAGE ROUTES ----------------- #

@app.route('/')
def index():
    """Dashboard homepage."""
    summary = analytics.get_overall_summary()
    recent_transactions = database.get_filtered_transactions(limit=6)
    insights = analytics.get_insights_and_suggestions()
    habits = analytics.get_spending_habits()
    weekly_data = analytics.get_weekly_expense_data()
    savings_goals = database.get_savings_goals()
    
    return render_template(
        'index.html',
        summary=summary,
        recent_transactions=recent_transactions,
        insights=insights,
        habits=habits,
        weekly_data=weekly_data,
        savings_goals=savings_goals
    )

@app.route('/transactions')
def transactions():
    """Transaction management page with filters, search, and pagination."""
    t_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'date_desc')
    
    tx_list = database.get_filtered_transactions(
        t_type=t_type,
        category=category,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        search=search if search else None,
        sort=sort
    )
    
    # Calculate filtered stats
    total_in = sum(t['amount'] for t in tx_list if t['type'] == 'income')
    total_ex = sum(t['amount'] for t in tx_list if t['type'] == 'expense')
    
    return render_template(
        'transactions.html',
        transactions=tx_list,
        current_type=t_type,
        current_category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort=sort,
        filtered_income=round(total_in, 2),
        filtered_expense=round(total_ex, 2)
    )

@app.route('/analytics')
def analytics_page():
    """Expense graphs and analysis page (Weekly, Monthly, Yearly)."""
    selected_year = request.args.get('year', date.today().year, type=int)
    selected_month = request.args.get('month', date.today().month, type=int)
    
    weekly = analytics.get_weekly_expense_data()
    monthly = analytics.get_monthly_expense_data(selected_year, selected_month)
    yearly = analytics.get_yearly_expense_data(selected_year)
    habits = analytics.get_spending_habits()
    
    # Generate list of years for filter dropdown
    available_years = [date.today().year - i for i in range(4)]
    
    return render_template(
        'analytics.html',
        weekly=weekly,
        monthly=monthly,
        yearly=yearly,
        habits=habits,
        selected_year=selected_year,
        selected_month=selected_month,
        available_years=available_years
    )

@app.route('/insights')
def insights_page():
    """Spending habits, 50/30/20 rule, financial health, and savings suggestions."""
    insights = analytics.get_insights_and_suggestions()
    habits = analytics.get_spending_habits()
    summary = analytics.get_overall_summary()
    goals = database.get_savings_goals()
    
    return render_template(
        'insights.html',
        insights=insights,
        habits=habits,
        summary=summary,
        goals=goals
    )

@app.route('/about')
def about():
    """About us page describing the team (Kamallesh, Janardhanan, Suriya) and project."""
    return render_template('about.html')

# ----------------- TRANSACTION ACTIONS ----------------- #

@app.route('/transaction/add', methods=['POST'])
def add_transaction_route():
    try:
        t_type = request.form.get('type')
        category = request.form.get('category')
        amount = float(request.form.get('amount', 0))
        tx_date = request.form.get('date', date.today().strftime('%Y-%m-%d'))
        payment_method = request.form.get('payment_method', 'UPI / GPay / PhonePe')
        description = request.form.get('description', '')
        is_recurring = 1 if request.form.get('is_recurring') else 0

        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return redirect(request.referrer or url_for('index'))

        database.add_transaction(t_type, category, amount, tx_date, payment_method, description, is_recurring)
        flash(f'Successfully recorded {t_type.capitalize()} of ₹{amount:,.2f} under {category}.', 'success')
    except Exception as e:
        flash(f'Failed to add transaction: {str(e)}', 'error')

    return redirect(request.referrer or url_for('index'))

@app.route('/transaction/edit/<int:t_id>', methods=['POST'])
def edit_transaction_route(t_id):
    try:
        t_type = request.form.get('type')
        category = request.form.get('category')
        amount = float(request.form.get('amount', 0))
        tx_date = request.form.get('date')
        payment_method = request.form.get('payment_method')
        description = request.form.get('description', '')
        is_recurring = 1 if request.form.get('is_recurring') else 0

        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return redirect(request.referrer or url_for('transactions'))

        database.update_transaction(t_id, t_type, category, amount, tx_date, payment_method, description, is_recurring)
        flash('Transaction updated successfully.', 'success')
    except Exception as e:
        flash(f'Failed to update transaction: {str(e)}', 'error')

    return redirect(request.referrer or url_for('transactions'))

@app.route('/transaction/delete/<int:t_id>', methods=['POST'])
def delete_transaction_route(t_id):
    try:
        database.delete_transaction(t_id)
        flash('Transaction deleted successfully.', 'info')
    except Exception as e:
        flash(f'Failed to delete transaction: {str(e)}', 'error')
    return redirect(request.referrer or url_for('transactions'))

# ----------------- SAVINGS GOALS ----------------- #

@app.route('/goal/add', methods=['POST'])
def add_goal_route():
    try:
        title = request.form.get('title')
        target_amount = float(request.form.get('target_amount', 0))
        current_amount = float(request.form.get('current_amount', 0))
        target_date = request.form.get('target_date', '')
        category = request.form.get('category', 'General')

        if target_amount <= 0:
            flash('Target amount must be greater than zero.', 'error')
            return redirect(url_for('insights_page'))

        database.add_savings_goal(title, target_amount, current_amount, target_date, category)
        flash(f'New Savings Goal "{title}" created!', 'success')
    except Exception as e:
        flash(f'Error creating goal: {str(e)}', 'error')
    return redirect(url_for('insights_page'))

@app.route('/goal/update/<int:goal_id>', methods=['POST'])
def update_goal_progress_route(goal_id):
    try:
        new_amt = float(request.form.get('current_amount', 0))
        database.update_goal_progress(goal_id, new_amt)
        flash('Goal progress updated!', 'success')
    except Exception as e:
        flash(f'Error updating goal: {str(e)}', 'error')
    return redirect(url_for('insights_page'))

@app.route('/goal/delete/<int:goal_id>', methods=['POST'])
def delete_goal_route(goal_id):
    try:
        database.delete_savings_goal(goal_id)
        flash('Goal removed.', 'info')
    except Exception as e:
        flash(f'Error deleting goal: {str(e)}', 'error')
    return redirect(url_for('insights_page'))

# ----------------- SETTINGS & DATA CONTROLS ----------------- #

@app.route('/settings/update', methods=['POST'])
def update_settings_route():
    try:
        monthly_budget = request.form.get('monthly_budget')
        currency_symbol = request.form.get('currency_symbol', '₹')
        if monthly_budget:
            database.update_setting('monthly_budget', float(monthly_budget))
        if currency_symbol:
            database.update_setting('currency_symbol', currency_symbol)
        flash('Settings saved successfully.', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    return redirect(request.referrer or url_for('index'))

@app.route('/data/reset', methods=['POST'])
def reset_data_route():
    database.reset_to_sample()
    flash('Database restored to rich demo dataset with multi-month transactions and goals.', 'info')
    return redirect(url_for('index'))

@app.route('/data/clear', methods=['POST'])
def clear_data_route():
    database.clear_all()
    flash('All transactions cleared. You now have a clean slate to enter your own transactions.', 'warning')
    return redirect(url_for('transactions'))

@app.route('/export/csv')
def export_csv():
    """Exports all transactions as a CSV spreadsheet."""
    all_tx = database.get_filtered_transactions(sort='date_desc')
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount (INR)', 'Payment Method', 'Description', 'Recurring'])
    
    for t in all_tx:
        writer.writerow([
            t['id'],
            t['date'],
            t['type'].capitalize(),
            t['category'],
            t['amount'],
            t['payment_method'],
            t['description'],
            'Yes' if t['is_recurring'] else 'No'
        ])
        
    output.seek(0)
    filename = f"BAASHA_Transactions_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

# ----------------- JSON APIS FOR CHARTS ----------------- #

@app.route('/api/analytics/weekly')
def api_weekly():
    target_date = request.args.get('date', None)
    data = analytics.get_weekly_expense_data(target_date)
    return jsonify(data)

@app.route('/api/analytics/monthly')
def api_monthly():
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    data = analytics.get_monthly_expense_data(year, month)
    return jsonify(data)

@app.route('/api/analytics/yearly')
def api_yearly():
    year = request.args.get('year', date.today().year, type=int)
    data = analytics.get_yearly_expense_data(year)
    return jsonify(data)

if __name__ == '__main__':
    print("=" * 60)
    print("  BAASHA - Master Your Money")
    print("  Team: Kamallesh, Janardhanan, Suriya (SRMIST)")
    print("  Web Server URLs:")
    print("  --> http://www.baasha.com:5000")
    print("  --> http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, port=5000, host='0.0.0.0')

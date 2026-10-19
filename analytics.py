"""
BAASHA Personal Finance Tracker - Analytics Engine
Computes weekly, monthly, yearly expense metrics, spending habits,
50/30/20 budget framework analysis, and smart savings suggestions.
"""

from datetime import datetime, date, timedelta
import calendar
from database import get_db, get_setting

# Classification of categories for the 50/30/20 rule
NEEDS_CATEGORIES = {
    'Rent & Housing', 'Groceries', 'Utilities & Bills', 
    'Health & Medical', 'Transportation / Fuel', 'Education & Courses'
}

WANTS_CATEGORIES = {
    'Food & Dining', 'Entertainment & Outing', 'Shopping & Lifestyle', 
    'Subscriptions', 'Miscellaneous'
}

def get_overall_summary():
    """Calculates overall lifetime and current month financial summary."""
    today = date.today()
    first_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # All time
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
        total_income = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
        total_expense = cursor.fetchone()[0] or 0.0
        
        # Current month
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type = 'income' AND date >= ? AND date <= ?
        """, (first_of_month, today_str))
        curr_month_income = cursor.fetchone()[0] or 0.0
        
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type = 'expense' AND date >= ? AND date <= ?
        """, (first_of_month, today_str))
        curr_month_expense = cursor.fetchone()[0] or 0.0
        
        # Count transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0] or 0

    net_balance = total_income - total_expense
    curr_month_net = curr_month_income - curr_month_expense
    
    savings_rate = 0.0
    if curr_month_income > 0:
        savings_rate = max(0.0, ((curr_month_income - curr_month_expense) / curr_month_income) * 100)
    elif total_income > 0:
        savings_rate = max(0.0, ((total_income - total_expense) / total_income) * 100)
        
    monthly_budget = float(get_setting('monthly_budget', 45000))
    budget_used_pct = round((curr_month_expense / monthly_budget) * 100, 1) if monthly_budget > 0 else 0
    budget_remaining = max(0.0, monthly_budget - curr_month_expense)

    # Compute Annual Income in LPA (Lakhs Per Annum)
    # 1 Lakh = 1,00,000 INR
    saved_lpa = get_setting('annual_income_lpa', None)
    if saved_lpa:
        annual_income_lpa = round(float(saved_lpa), 2)
    elif curr_month_income > 0:
        annual_income_lpa = round((curr_month_income * 12) / 100000.0, 2)
    elif total_income > 0:
        annual_income_lpa = round((total_income) / 100000.0, 2)
    else:
        annual_income_lpa = 0.0

    return {
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'net_balance': round(net_balance, 2),
        'curr_month_income': round(curr_month_income, 2),
        'curr_month_expense': round(curr_month_expense, 2),
        'curr_month_net': round(curr_month_net, 2),
        'savings_rate': round(savings_rate, 1),
        'monthly_budget': round(monthly_budget, 2),
        'budget_used_pct': budget_used_pct,
        'budget_remaining': round(budget_remaining, 2),
        'total_transactions': total_transactions,
        'annual_income_lpa': annual_income_lpa
    }

def get_weekly_expense_data(target_date=None):
    """
    Returns day-by-day expense data for the 7 days of the specified week (Monday to Sunday)
    and compares it to the previous 7 days.
    """
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    # Start of current week (Monday)
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Previous week
    prev_start_of_week = start_of_week - timedelta(days=7)
    prev_end_of_week = start_of_week - timedelta(days=1)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Current week transactions
        cursor.execute("""
            SELECT date, category, amount, description FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
            ORDER BY date ASC
        """, (start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')))
        curr_week_rows = cursor.fetchall()
        
        # Previous week transactions
        cursor.execute("""
            SELECT date, amount FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
        """, (prev_start_of_week.strftime('%Y-%m-%d'), prev_end_of_week.strftime('%Y-%m-%d')))
        prev_week_rows = cursor.fetchall()

    # Prepare 7 days of current week
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    full_dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    display_dates = [(start_of_week + timedelta(days=i)).strftime('%b %d') for i in range(7)]
    
    curr_daily_totals = {d: 0.0 for d in full_dates}
    category_totals = {}
    
    for row in curr_week_rows:
        d = row['date']
        amt = float(row['amount'])
        cat = row['category']
        if d in curr_daily_totals:
            curr_daily_totals[d] += amt
        category_totals[cat] = category_totals.get(cat, 0.0) + amt

    # Previous week daily totals
    prev_dates = [(prev_start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    prev_daily_totals = {d: 0.0 for d in prev_dates}
    for row in prev_week_rows:
        d = row['date']
        amt = float(row['amount'])
        if d in prev_daily_totals:
            prev_daily_totals[d] += amt

    curr_total = sum(curr_daily_totals.values())
    prev_total = sum(prev_daily_totals.values())
    
    growth_pct = 0.0
    if prev_total > 0:
        growth_pct = round(((curr_total - prev_total) / prev_total) * 100, 1)

    # Find highest spend day
    daily_amounts = [round(curr_daily_totals[d], 2) for d in full_dates]
    max_amt = max(daily_amounts) if daily_amounts else 0.0
    peak_day = "None"
    if max_amt > 0:
        peak_idx = daily_amounts.index(max_amt)
        peak_day = f"{day_labels[peak_idx]} ({display_dates[peak_idx]})"

    return {
        'week_range': f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b %Y')}",
        'labels': [f"{day_labels[i]} ({display_dates[i]})" for i in range(7)],
        'short_labels': day_labels,
        'current_week_data': daily_amounts,
        'prev_week_data': [round(prev_daily_totals[d], 2) for d in prev_dates],
        'total_expense': round(curr_total, 2),
        'prev_total_expense': round(prev_total, 2),
        'growth_pct': growth_pct,
        'peak_day': peak_day,
        'categories': list(category_totals.keys()),
        'category_amounts': [round(v, 2) for v in category_totals.values()]
    }

def get_monthly_expense_data(year=None, month=None):
    """
    Returns day-by-day expenses, weekly breakdown, and category breakdown for a selected month.
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    num_days = calendar.monthrange(year, month)[1]
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{num_days:02d}"

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Monthly expenses
        cursor.execute("""
            SELECT date, category, amount FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
            ORDER BY date ASC
        """, (start_date, end_date))
        expense_rows = cursor.fetchall()
        
        # Monthly incomes
        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE type = 'income' AND date >= ? AND date <= ?
        """, (start_date, end_date))
        total_income = cursor.fetchone()[0] or 0.0

    # Build day map
    daily_totals = {d: 0.0 for d in range(1, num_days + 1)}
    cumulative_totals = []
    category_totals = {}
    
    # 4 Weeks grouping: Days 1-7, 8-14, 15-21, 22-end
    week_groups = {'Week 1 (Days 1-7)': 0.0, 'Week 2 (Days 8-14)': 0.0, 'Week 3 (Days 15-21)': 0.0, 'Week 4+ (Days 22+)': 0.0}

    for row in expense_rows:
        d_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
        day_num = d_obj.day
        amt = float(row['amount'])
        cat = row['category']
        
        daily_totals[day_num] += amt
        category_totals[cat] = category_totals.get(cat, 0.0) + amt
        
        if day_num <= 7:
            week_groups['Week 1 (Days 1-7)'] += amt
        elif day_num <= 14:
            week_groups['Week 2 (Days 8-14)'] += amt
        elif day_num <= 21:
            week_groups['Week 3 (Days 15-21)'] += amt
        else:
            week_groups['Week 4+ (Days 22+)'] += amt

    # Cumulative calculations
    running_sum = 0.0
    for day in range(1, num_days + 1):
        running_sum += daily_totals[day]
        cumulative_totals.append(round(running_sum, 2))

    total_expense = sum(daily_totals.values())
    avg_daily_spend = round(total_expense / num_days, 2) if num_days > 0 else 0.0
    
    # Sort categories descending
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    month_name = calendar.month_name[month]

    return {
        'year': year,
        'month': month,
        'month_name': f"{month_name} {year}",
        'days': [f"Day {d}" for d in range(1, num_days + 1)],
        'daily_expenses': [round(daily_totals[d], 2) for d in range(1, num_days + 1)],
        'cumulative_expenses': cumulative_totals,
        'week_group_labels': list(week_groups.keys()),
        'week_group_amounts': [round(v, 2) for v in week_groups.values()],
        'categories': [item[0] for item in sorted_categories],
        'category_amounts': [round(item[1], 2) for item in sorted_categories],
        'total_expense': round(total_expense, 2),
        'total_income': round(total_income, 2),
        'net_savings': round(total_income - total_expense, 2),
        'avg_daily_spend': avg_daily_spend
    }

def get_yearly_expense_data(year=None):
    """
    Returns month-by-month expenses, incomes, and yearly category breakdown for a selected year.
    """
    if year is None:
        year = date.today().year

    start_date = f"{year:04d}-01-01"
    end_date = f"{year:04d}-12-31"

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Expenses
        cursor.execute("""
            SELECT date, category, amount FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
            ORDER BY date ASC
        """, (start_date, end_date))
        expenses = cursor.fetchall()
        
        # Incomes
        cursor.execute("""
            SELECT date, amount FROM transactions
            WHERE type = 'income' AND date >= ? AND date <= ?
            ORDER BY date ASC
        """, (start_date, end_date))
        incomes = cursor.fetchall()

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_expenses = [0.0] * 12
    monthly_incomes = [0.0] * 12
    category_totals = {}

    for row in expenses:
        m = datetime.strptime(row['date'], '%Y-%m-%d').month - 1
        amt = float(row['amount'])
        monthly_expenses[m] += amt
        cat = row['category']
        category_totals[cat] = category_totals.get(cat, 0.0) + amt

    for row in incomes:
        m = datetime.strptime(row['date'], '%Y-%m-%d').month - 1
        amt = float(row['amount'])
        monthly_incomes[m] += amt

    yearly_total_expense = sum(monthly_expenses)
    yearly_total_income = sum(monthly_incomes)
    yearly_net_savings = yearly_total_income - yearly_total_expense
    
    # Calculate savings by month
    monthly_net = [round(inc - exp, 2) for inc, exp in zip(monthly_incomes, monthly_expenses)]

    # Peak expense month
    max_expense = max(monthly_expenses) if monthly_expenses else 0.0
    peak_month = "N/A"
    if max_expense > 0:
        peak_idx = monthly_expenses.index(max_expense)
        peak_month = f"{month_names[peak_idx]} (₹{max_expense:,.0f})"

    # Lowest non-zero expense month
    non_zero = [(m, amt) for m, amt in enumerate(monthly_expenses) if amt > 0]
    lowest_month = "N/A"
    if non_zero:
        min_idx, min_amt = min(non_zero, key=lambda x: x[1])
        lowest_month = f"{month_names[min_idx]} (₹{min_amt:,.0f})"

    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    return {
        'year': year,
        'months': month_names,
        'monthly_expenses': [round(x, 2) for x in monthly_expenses],
        'monthly_incomes': [round(x, 2) for x in monthly_incomes],
        'monthly_net_savings': monthly_net,
        'categories': [item[0] for item in sorted_categories],
        'category_amounts': [round(item[1], 2) for item in sorted_categories],
        'total_expense': round(yearly_total_expense, 2),
        'total_income': round(yearly_total_income, 2),
        'total_income_lpa': round(yearly_total_income / 100000.0, 2),
        'annual_income_lpa': float(get_setting('annual_income_lpa', round(yearly_total_income / 100000.0, 2))),
        'net_savings': round(yearly_net_savings, 2),
        'peak_month': peak_month,
        'lowest_month': lowest_month,
        'avg_monthly_expense': round(yearly_total_expense / 12, 2)
    }

def get_spending_habits():
    """
    Analyzes transaction patterns:
    - Weekend vs Weekday spending
    - Payment method distribution
    - Top spending categories
    - Average transaction size
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, amount, category, payment_method FROM transactions WHERE type = 'expense'")
        expenses = cursor.fetchall()

    if not expenses:
        return {
            'weekend_pct': 0, 'weekday_pct': 0,
            'weekend_total': 0, 'weekday_total': 0,
            'payment_methods': {},
            'top_categories': [],
            'avg_expense_amount': 0,
            'total_expenses_count': 0
        }

    weekday_total = 0.0
    weekend_total = 0.0
    payment_methods = {}
    category_counts = {}
    category_amounts = {}
    total_amount = 0.0

    for row in expenses:
        d = datetime.strptime(row['date'], '%Y-%m-%d').date()
        amt = float(row['amount'])
        pm = row['payment_method'] or 'UPI / GPay / PhonePe'
        cat = row['category']
        
        total_amount += amt
        
        # Monday is 0 and Sunday is 6
        if d.weekday() in (5, 6): # Sat, Sun
            weekend_total += amt
        else:
            weekday_total += amt
            
        payment_methods[pm] = payment_methods.get(pm, 0.0) + amt
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_amounts[cat] = category_amounts.get(cat, 0.0) + amt

    total_sum = weekend_total + weekday_total
    weekend_pct = round((weekend_total / total_sum) * 100, 1) if total_sum > 0 else 0
    weekday_pct = round((weekday_total / total_sum) * 100, 1) if total_sum > 0 else 0
    avg_expense = round(total_amount / len(expenses), 2) if expenses else 0

    sorted_categories = sorted(category_amounts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_categories = [
        {'name': cat, 'amount': round(amt, 2), 'pct': round((amt / total_amount) * 100, 1) if total_amount > 0 else 0}
        for cat, amt in sorted_categories
    ]

    return {
        'weekend_pct': weekend_pct,
        'weekday_pct': weekday_pct,
        'weekend_total': round(weekend_total, 2),
        'weekday_total': round(weekday_total, 2),
        'payment_methods': {k: round(v, 2) for k, v in payment_methods.items()},
        'top_categories': top_categories,
        'avg_expense_amount': avg_expense,
        'total_expenses_count': len(expenses)
    }

def get_insights_and_suggestions():
    """
    Computes 50/30/20 rule breakdown, Financial Health Score,
    and tailored smart savings recommendations.
    """
    summary = get_overall_summary()
    habits = get_spending_habits()
    
    # 50/30/20 Breakdown on Current Month (or All Time if current month empty)
    today = date.today()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, amount FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
        """, (start_date, end_date))
        expenses = cursor.fetchall()

    if not expenses:
        # Fallback to last 90 days for richer presentation
        cutoff = (today - timedelta(days=90)).strftime('%Y-%m-%d')
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, amount FROM transactions
                WHERE type = 'expense' AND date >= ?
            """, (cutoff,))
            expenses = cursor.fetchall()

    needs_total = 0.0
    wants_total = 0.0
    
    for row in expenses:
        cat = row['category']
        amt = float(row['amount'])
        if cat in NEEDS_CATEGORIES:
            needs_total += amt
        else:
            wants_total += amt

    ref_income = summary['curr_month_income'] if summary['curr_month_income'] > 0 else summary['total_income']
    if ref_income <= 0:
        ref_income = needs_total + wants_total + 1000.0

    actual_savings = max(0.0, ref_income - (needs_total + wants_total))
    
    needs_pct = round((needs_total / ref_income) * 100, 1)
    wants_pct = round((wants_total / ref_income) * 100, 1)
    savings_pct = round((actual_savings / ref_income) * 100, 1)

    # 50/30/20 Ideal Targets
    rule_50_30_20 = {
        'needs': {
            'actual_amt': round(needs_total, 2),
            'actual_pct': needs_pct,
            'target_pct': 50.0,
            'target_amt': round(ref_income * 0.50, 2),
            'status': 'Good' if needs_pct <= 50 else 'High'
        },
        'wants': {
            'actual_amt': round(wants_total, 2),
            'actual_pct': wants_pct,
            'target_pct': 30.0,
            'target_amt': round(ref_income * 0.30, 2),
            'status': 'Good' if wants_pct <= 30 else 'Excessive'
        },
        'savings': {
            'actual_amt': round(actual_savings, 2),
            'actual_pct': savings_pct,
            'target_pct': 20.0,
            'target_amt': round(ref_income * 0.20, 2),
            'status': 'On Track' if savings_pct >= 20 else 'Below Target'
        }
    }

    # Financial Health Score (0 - 100)
    score = 40 # Base
    if savings_pct >= 20:
        score += 30
    elif savings_pct >= 10:
        score += 15
    else:
        score += 5

    if wants_pct <= 30:
        score += 20
    elif wants_pct <= 40:
        score += 10

    if needs_pct <= 55:
        score += 10

    score = min(100, max(10, score))
    
    grade = 'Critical'
    grade_color = 'red'
    if score >= 80:
        grade = 'Excellent'
        grade_color = 'emerald'
    elif score >= 65:
        grade = 'Good'
        grade_color = 'blue'
    elif score >= 50:
        grade = 'Fair'
        grade_color = 'amber'

    # Actionable Smart Suggestions
    suggestions = []
    
    # Check top category
    if habits['top_categories']:
        top_cat = habits['top_categories'][0]
        if top_cat['name'] in ['Food & Dining', 'Entertainment & Outing', 'Shopping & Lifestyle']:
            cut_potential = round(top_cat['amount'] * 0.20, 0)
            suggestions.append({
                'title': f'Optimize {top_cat["name"]} Spending',
                'description': f'"{top_cat["name"]}" is your #1 spending drain ({top_cat["pct"]}% of expenses). Reducing this category by 20% through home cooking or mindful purchases could save you ₹{cut_potential:,.0f} every cycle.',
                'potential_saving': cut_potential,
                'category': 'Expense Optimization',
                'badge': 'High Impact',
                'icon': 'fa-utensils' if 'Food' in top_cat['name'] else 'fa-bag-shopping'
            })
            
    # Weekend spending check
    if habits['weekend_pct'] > 35:
        weekend_excess = round(habits['weekend_total'] * 0.25, 0)
        suggestions.append({
            'title': 'Weekend Splurge Warning',
            'description': f'You are spending {habits["weekend_pct"]}% of your total budget on Saturdays and Sundays alone! Setting a dedicated weekend cash cap can prevent sudden end-of-month budget crunches.',
            'potential_saving': weekend_excess,
            'category': 'Behavioral Habit',
            'badge': 'Habit Alert',
            'icon': 'fa-calendar-week'
        })
        
    # Emergency Fund suggestion
    monthly_burn = summary['curr_month_expense'] if summary['curr_month_expense'] > 0 else (summary['total_expense'] / 6)
    suggested_emergency_fund = round(monthly_burn * 3, 0)
    suggestions.append({
        'title': 'Emergency Runway Building',
        'description': f'Based on your monthly burn rate of approximately ₹{monthly_burn:,.0f}, a 3-month safety buffer of ₹{suggested_emergency_fund:,.0f} is recommended in liquid savings or fixed deposits.',
        'potential_saving': 0,
        'category': 'Safety & Resilience',
        'badge': 'Long Term',
        'icon': 'fa-shield-halved'
    })

    # Subscriptions audit
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE category = 'Subscriptions'")
        sub_total = cursor.fetchone()[0] or 0.0
        
    if sub_total > 0:
        suggestions.append({
            'title': 'Audit Recurring Subscriptions',
            'description': f'You have logged ₹{sub_total:,.0f} in recurring subscriptions. Review OTT platforms, memberships, and app subscriptions to cancel unused services.',
            'potential_saving': round(sub_total * 0.35, 0),
            'category': 'Subscriptions',
            'badge': 'Quick Win',
            'icon': 'fa-repeat'
        })

    # Savings rule reminder
    if savings_pct < 20:
        gap = round((ref_income * 0.20) - actual_savings, 0)
        suggestions.append({
            'title': 'Bridge the 20% Savings Gap',
            'description': f'You are currently saving {savings_pct}%, which is below the recommended 20% benchmark. Automating a deposit of ₹{gap:,.0f} at the start of each month will lock in financial independence.',
            'potential_saving': gap,
            'category': 'Wealth Building',
            'badge': 'Priority Goal',
            'icon': 'fa-piggy-bank'
        })

    return {
        'rule_50_30_20': rule_50_30_20,
        'health_score': score,
        'health_grade': grade,
        'health_color': grade_color,
        'suggestions': suggestions,
        'emergency_fund_target': suggested_emergency_fund,
        'monthly_burn': round(monthly_burn, 2)
    }

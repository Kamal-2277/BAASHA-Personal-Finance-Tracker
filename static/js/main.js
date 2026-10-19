/**
 * BAASHA Personal Finance Tracker - Main Client-Side Logic
 * Manages modal toggles, category synchronization, edit transaction pre-filling, and UI interactions.
 */

const CATEGORY_MAP = {
    income: [
        'Salary',
        'Freelance / Consulting',
        'Investments & Dividends',
        'Business Revenue',
        'Scholarship / Stipend',
        'Gifts / Allowance',
        'Other Income'
    ],
    expense: [
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
};

// Update category select dropdown based on selected Type (income or expense)
function updateCategoryDropdown(typeSelectId, categorySelectId, selectedValue = '') {
    const typeEl = document.getElementById(typeSelectId);
    const catEl = document.getElementById(categorySelectId);
    if (!typeEl || !catEl) return;

    const tType = typeEl.value;
    const cats = CATEGORY_MAP[tType] || CATEGORY_MAP['expense'];

    catEl.innerHTML = '';
    cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        if (c === selectedValue) opt.selected = true;
        catEl.appendChild(opt);
    });
}

// Modal open/close helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
    }
}

// Open Edit Transaction Modal and populate existing values
function openEditTransactionModal(data) {
    document.getElementById('edit-tx-form').action = `/transaction/edit/${data.id}`;
    document.getElementById('edit-type').value = data.type;
    updateCategoryDropdown('edit-type', 'edit-category', data.category);
    document.getElementById('edit-amount').value = data.amount;
    document.getElementById('edit-date').value = data.date;
    document.getElementById('edit-payment-method').value = data.payment_method;
    document.getElementById('edit-description').value = data.description || '';
    document.getElementById('edit-recurring').checked = data.is_recurring == 1;

    openModal('editTransactionModal');
}

// Auto-dismiss alert badges after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    // Dismiss alerts
    setTimeout(() => {
        const alerts = document.querySelectorAll('.flash-alert');
        alerts.forEach(a => {
            a.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            a.style.opacity = '0';
            a.style.transform = 'translateY(-10px)';
            setTimeout(() => a.remove(), 600);
        });
    }, 4500);

    // Close modals on clicking outside of dialog container
    const modals = document.querySelectorAll('.modal-backdrop');
    modals.forEach(m => {
        m.addEventListener('click', (e) => {
            if (e.target === m) {
                closeModal(m.id);
            }
        });
    });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-backdrop:not(.hidden)').forEach(m => closeModal(m.id));
        }
    });
});

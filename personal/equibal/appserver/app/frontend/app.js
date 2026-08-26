document.addEventListener('DOMContentLoaded', () => {
  // Navigation & Drawer State
  const drawer = document.getElementById('drawer');
  const pageContainer = document.querySelector('.q-page-container');
  const btnToggleDrawer = document.getElementById('btn-toggle-drawer');

  btnToggleDrawer.addEventListener('click', () => {
    drawer.classList.toggle('is-closed');
    pageContainer.classList.toggle('drawer-closed');
  });

  // Default summary count numbers
  const defaultCounts = {
    roles: 4,
    users: 3,
    accounts: 2,
    banks: 1
  };

  // Mock data fallbacks for all entities in the banking system
  const mockData = {
    dashboard: [
      { id: 1, entity: 'Role: SYSTEM_ADMIN', type: 'Security Role', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 2, entity: 'User: System Admin', type: 'Administrator Account', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 3, entity: 'User: Staff Member', type: 'Branch Staff', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 4, entity: 'User: Customer User', type: 'Client User', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 5, entity: 'Account: #4821', type: 'Checking Account', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 6, entity: 'Account: #1094', type: 'Savings Account', status: 'ACTIVE', updated: '2026-08-26' },
      { id: 7, entity: 'Bank: Central Bank Hub', type: 'Registered Bank', status: 'ACTIVE', updated: '2026-08-26' }
    ],
    roles: [
      { id: 1, role_code: 'SYSTEM_ADMIN', role_name: 'System Admin', description: 'Full system administration privileges' },
      { id: 2, role_code: 'BRANCH_MANAGER', role_name: 'Branch Manager', description: 'Branch management and approvals' },
      { id: 3, role_code: 'TELLER', role_name: 'Bank Teller', description: 'Counter transactions and customer service' },
      { id: 4, role_code: 'CUSTOMER', role_name: 'Customer', description: 'Online banking client portal access' }
    ],
    account_types: [
      { id: 1, type_code: 'CHK', type_name: 'Checking Account', min_balance: '$100.00', interest_rate: '0.05%' },
      { id: 2, type_code: 'SAV', type_name: 'Savings Account', min_balance: '$500.00', interest_rate: '1.25%' },
      { id: 3, type_code: 'BUS', type_name: 'Business Account', min_balance: '$1,000.00', interest_rate: '0.10%' }
    ],
    banks: [
      { id: 1, bank_code: 'CB001', bank_name: 'Central Bank Hub', swift_code: 'CBHUBPHM1', status: 'ACTIVE' }
    ],
    fee_types: [
      { id: 1, fee_code: 'OVERDRAFT', fee_name: 'Overdraft Fee', amount: '$25.00', status: 'ACTIVE' },
      { id: 2, fee_code: 'TRANSFER_INT', fee_name: 'Interbank Transfer Fee', amount: '$5.00', status: 'ACTIVE' }
    ],
    users: [
      { id: 1, username: 'admin', name: 'System Admin', email: 'admin@minibank.com', role: 'System Admin', status: 'ACTIVE' },
      { id: 2, username: 'jordan_staff', name: 'Jordan Staff', email: 'jordan@minibank.com', role: 'Bank Teller', status: 'ACTIVE' },
      { id: 3, username: 'maya_customer', name: 'Maya Chen', email: 'maya@example.com', role: 'Customer', status: 'ACTIVE' }
    ],
    audit_logs: [
      { id: 101, timestamp: '2026-08-26 10:15', user: 'admin', action: 'USER_LOGIN', details: 'Successful authentication' },
      { id: 102, timestamp: '2026-08-26 10:30', user: 'admin', action: 'CREATE_ROLE', details: 'Role CUSTOMER configured' },
      { id: 103, timestamp: '2026-08-26 11:05', user: 'jordan_staff', action: 'DEPOSIT', details: 'Processed deposit for account #4821' }
    ],
    accounts: [
      { id: 1, account_number: '4821', customer: 'Maya Chen', type: 'Checking', balance: '$12,480.00', status: 'ACTIVE' },
      { id: 2, account_number: '1094', customer: 'Noah Williams', type: 'Savings', balance: '$28,950.40', status: 'ACTIVE' }
    ],
    withdrawal_limits: [
      { id: 1, limit_type: 'DAILY_ATM', max_amount: '$1,000.00', currency: 'PHP', status: 'ACTIVE' },
      { id: 2, limit_type: 'DAILY_ONLINE', max_amount: '$5,000.00', currency: 'PHP', status: 'ACTIVE' }
    ],
    interest_policies: [
      { id: 1, policy_code: 'SAV_STANDARD', rate: '1.25%', frequency: 'Monthly', status: 'ACTIVE' }
    ],
    reports: [
      { id: 1, report_name: 'Monthly Ledger Summary', generated: '2026-08-01', format: 'PDF/CSV' },
      { id: 2, report_name: 'Daily Transaction Audit', generated: '2026-08-26', format: 'PDF/CSV' }
    ]
  };

  // Table Column definitions
  const columns = {
    dashboard: ['ID', 'System Entity', 'Type', 'Status', 'Last Updated'],
    roles: ['ID', 'Role Code', 'Role Name', 'Description'],
    account_types: ['ID', 'Code', 'Account Type', 'Min Balance', 'Interest Rate'],
    banks: ['ID', 'Bank Code', 'Bank Name', 'SWIFT Code', 'Status'],
    fee_types: ['ID', 'Fee Code', 'Fee Name', 'Amount', 'Status'],
    users: ['ID', 'Username', 'Full Name', 'Email', 'Role', 'Status'],
    audit_logs: ['Log ID', 'Timestamp', 'User', 'Action', 'Details'],
    accounts: ['ID', 'Account #', 'Customer Name', 'Account Type', 'Available Balance', 'Status'],
    withdrawal_limits: ['ID', 'Limit Type', 'Max Amount', 'Currency', 'Status'],
    interest_policies: ['ID', 'Policy Code', 'Annual Rate', 'Compounding', 'Status'],
    reports: ['ID', 'Report Name', 'Generated Date', 'Export Format']
  };

  let currentNav = 'dashboard';
  let currentRole = 'admin'; // 'admin', 'staff', 'customer'

  // Role permissions definitions
  const rolePermissions = {
    admin: {
      title: 'Welcome, System Admin',
      badge: 'System Admin (Full Privileges)',
      allowedNav: ['dashboard', 'roles', 'account_types', 'banks', 'fee_types', 'users', 'audit_logs', 'accounts', 'withdrawal_limits', 'interest_policies', 'reports'],
      canAdd: true
    },
    staff: {
      title: 'Welcome, Jordan Staff (Bank Teller)',
      badge: 'Branch Staff / Teller',
      allowedNav: ['dashboard', 'accounts', 'banks', 'withdrawal_limits', 'interest_policies', 'reports'],
      restrictedNav: ['roles', 'account_types', 'fee_types', 'users', 'audit_logs'],
      canAdd: false,
      reason: '403 FORBIDDEN: Staff members cannot modify System Configuration or view Audit Logs.'
    },
    customer: {
      title: 'Welcome, Maya Chen (Customer Portal)',
      badge: 'Customer Client User',
      allowedNav: ['dashboard', 'accounts', 'withdrawal_limits'],
      restrictedNav: ['roles', 'account_types', 'banks', 'fee_types', 'users', 'audit_logs', 'interest_policies', 'reports'],
      canAdd: false,
      reason: '403 FORBIDDEN: Customer role has view-only access to personal accounts. Admin configuration is restricted.'
    }
  };

  // Fetch count stats from API backend with fallback
  async function fetchCounts() {
    try {
      const [rolesRes, usersRes, accsRes, banksRes] = await Promise.allSettled([
        fetch('/roles/').then(r => r.ok ? r.json() : null),
        fetch('/users/').then(r => r.ok ? r.json() : null),
        fetch('/accounts/').then(r => r.ok ? r.json() : null),
        fetch('/banks/').then(r => r.ok ? r.json() : null)
      ]);

      const rolesCount = (rolesRes.status === 'fulfilled' && Array.isArray(rolesRes.value) && rolesRes.value.length > 0) ? rolesRes.value.length : defaultCounts.roles;
      const usersCount = (usersRes.status === 'fulfilled' && Array.isArray(usersRes.value) && usersRes.value.length > 0) ? usersRes.value.length : defaultCounts.users;
      const accsCount = (accsRes.status === 'fulfilled' && Array.isArray(accsRes.value) && accsRes.value.length > 0) ? accsRes.value.length : defaultCounts.accounts;
      const banksCount = (banksRes.status === 'fulfilled' && Array.isArray(banksRes.value) && banksRes.value.length > 0) ? banksRes.value.length : defaultCounts.banks;

      document.getElementById('stat-roles-val').textContent = rolesCount;
      document.getElementById('stat-users-val').textContent = usersCount;
      document.getElementById('stat-accounts-val').textContent = accsCount;
      document.getElementById('stat-banks-val').textContent = banksCount;
    } catch (e) {
      console.log('Using default summary counts');
    }
  }

  // Update UI when role changes
  function updateRoleView() {
    const roleSelect = document.getElementById('role-select');
    currentRole = roleSelect ? roleSelect.value : 'admin';
    const perm = rolePermissions[currentRole];

    // Update Welcome Title
    document.getElementById('welcome-title').textContent = perm.title;

    // Update nav item visuals
    document.querySelectorAll('[data-nav]').forEach(item => {
      const navKey = item.getAttribute('data-nav');
      if (perm.allowedNav.includes(navKey)) {
        item.style.opacity = '1';
        item.style.pointerEvents = 'auto';
        item.title = '';
      } else {
        item.style.opacity = '0.45';
        item.title = perm.reason || 'Access Restricted';
      }
    });

    // If current navigation is restricted under new role, default back to dashboard
    if (!perm.allowedNav.includes(currentNav)) {
      currentNav = 'dashboard';
      document.querySelectorAll('[data-nav]').forEach(n => n.classList.remove('q-item--active', 'text-primary', 'bg-blue-1'));
      const dashItem = document.querySelector('[data-nav="dashboard"]');
      if (dashItem) dashItem.classList.add('q-item--active', 'text-primary', 'bg-blue-1');
    }

    renderTable(currentNav);
  }

  // Render Table content
  function renderTable(navKey, filterText = '') {
    const headEl = document.getElementById('table-head');
    const bodyEl = document.getElementById('table-body');
    const titleEl = document.getElementById('view-title');
    const btnAdd = document.getElementById('btn-add-entity');

    const perm = rolePermissions[currentRole];

    // Check if navigation key is allowed for current role
    if (!perm.allowedNav.includes(navKey)) {
      titleEl.innerHTML = `<span style="color: #d32f2f;">Access Restricted - ${navKey.replace('_', ' ').toUpperCase()}</span>`;
      headEl.innerHTML = `<tr><th>Security Check</th></tr>`;
      bodyEl.innerHTML = `
        <tr>
          <td style="text-align: center; padding: 32px; background: #fff5f5; color: #c62828;">
            <div style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">⛔ ${perm.reason}</div>
            <div style="font-size: 13px; color: #555;">Switch back to <b>Administrator</b> in the top navbar to access this module.</div>
          </td>
        </tr>`;
      btnAdd.style.display = 'none';
      return;
    }

    btnAdd.style.display = perm.canAdd ? 'inline-block' : 'none';

    let colList = columns[navKey] || columns.dashboard;
    let rowsData = mockData[navKey] || mockData.dashboard;

    // Filter customer-specific view
    if (currentRole === 'customer') {
      if (navKey === 'accounts') {
        rowsData = rowsData.filter(acc => acc.customer === 'Maya Chen');
      } else if (navKey === 'dashboard') {
        rowsData = [
          { id: 1, entity: 'Account: #4821 (Checking)', type: 'Primary Checking', status: 'ACTIVE', updated: '2026-08-26' },
          { id: 2, entity: 'Recent Transfer: #9042', type: 'Internal Transfer', status: 'ACTIVE', updated: '2026-08-26' }
        ];
      }
    }

    // Header title formatted
    const titleText = navKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    titleEl.textContent = navKey === 'dashboard' ? 'Overview & System Operations' : `${titleText} Management`;

    // Render <thead>
    headEl.innerHTML = `<tr>${colList.map(c => `<th>${c}</th>`).join('')}</tr>`;

    // Filter rows
    const filtered = rowsData.filter(row => {
      if (!filterText) return true;
      return Object.values(row).some(val => String(val).toLowerCase().includes(filterText.toLowerCase()));
    });

    if (filtered.length === 0) {
      bodyEl.innerHTML = `<tr><td colspan="${colList.length}" style="text-align:center; padding: 24px; color: #888;">No matching records found</td></tr>`;
      return;
    }

    // Render <tbody>
    bodyEl.innerHTML = filtered.map(row => {
      const keys = Object.keys(row);
      const cells = keys.map(k => {
        let val = row[k];
        if (k === 'status') {
          const badgeClass = val === 'ACTIVE' ? 'badge-success' : val === 'PENDING' ? 'badge-warning' : 'badge-danger';
          return `<td><span class="badge ${badgeClass}">${val}</span></td>`;
        }
        return `<td>${val}</td>`;
      }).join('');
      return `<tr>${cells}</tr>`;
    }).join('');
  }

  // Role selector event handler
  const roleSelect = document.getElementById('role-select');
  if (roleSelect) {
    roleSelect.addEventListener('change', () => {
      updateRoleView();
    });
  }

  // Handle Sidebar Navigation Click
  const navItems = document.querySelectorAll('[data-nav]');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetNav = item.getAttribute('data-nav');
      const perm = rolePermissions[currentRole];

      if (!perm.allowedNav.includes(targetNav)) {
        alert(perm.reason);
      }

      navItems.forEach(n => n.classList.remove('q-item--active', 'text-primary', 'bg-blue-1'));
      item.classList.add('q-item--active', 'text-primary', 'bg-blue-1');
      currentNav = targetNav;
      renderTable(currentNav);
    });
  });

  // Handle Stat Card Click
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach(card => {
    card.addEventListener('click', () => {
      const targetNav = card.getAttribute('data-stat');
      const targetNavItem = document.querySelector(`[data-nav="${targetNav}"]`);
      if (targetNavItem) {
        targetNavItem.click();
      }
    });
  });

  // Search Filter Handler
  const searchInput = document.getElementById('search-input');
  searchInput.addEventListener('input', (e) => {
    renderTable(currentNav, e.target.value);
  });

  // Add New Entity Button Handler
  document.getElementById('btn-add-entity').addEventListener('click', () => {
    alert(`Add new ${currentNav.replace('_', ' ')} functionality active.`);
  });

  // Logout Handler
  document.getElementById('btn-logout').addEventListener('click', () => {
    alert('Logged out from Mini Banking System session.');
  });

  // Initial Load
  fetchCounts();
  updateRoleView();
});
# Define available permissions for each app
APP_PERMISSIONS = {
    'accounts': ['view', 'add', 'change', 'delete'],
    'certificates': ['view', 'add', 'change', 'delete'],
    'clients': ['view', 'add', 'change', 'delete'],
    'contacts': ['view', 'add', 'change', 'delete'],
    'insertions': ['view', 'add', 'change', 'delete'],
    'IT_Return': ['view', 'add', 'change', 'delete'],
    'judgments': ['view', 'add', 'change', 'delete'],
    'other_forms': ['view', 'add', 'change', 'delete'],
    'proceedings': ['view', 'add', 'change', 'delete'],
    'reports': ['view', 'add', 'change', 'delete'],
    'tds': ['view', 'add', 'change', 'delete'],
    'timesheet': ['view', 'add', 'change', 'delete'],
}

# Define role-based permissions
ROLE_PERMISSIONS = {
    'Super Admin': {
        'apps': {
            'accounts': ['view', 'add', 'change', 'delete'],
            'certificates': ['view', 'add', 'change', 'delete'],
            'clients': ['view', 'add', 'change', 'delete'],
            'contacts': ['view', 'add', 'change', 'delete'],
            'insertions': ['view', 'add', 'change', 'delete'],
            'IT_Return': ['view', 'add', 'change', 'delete'],
            'judgments': ['view', 'add', 'change', 'delete'],
            'other_forms': ['view', 'add', 'change', 'delete'],
            'proceedings': ['view', 'add', 'change', 'delete'],
            'reports': ['view', 'add', 'change', 'delete'],
            'tds': ['view', 'add', 'change', 'delete'],
            'timesheet': ['view', 'add', 'change', 'delete']
        }
    },
    'Super Group Head': {
        'apps': {
            'accounts': ['view'],  # Read-only access to accounts
            'certificates': ['view', 'add', 'change', 'delete'],
            'clients': ['view', 'add', 'change', 'delete'],
            'contacts': ['view', 'add', 'change', 'delete'],
            'insertions': ['view', 'add', 'change', 'delete'],
            'IT_Return': ['view', 'add', 'change', 'delete'],
            'judgments': ['view', 'add', 'change', 'delete'],
            'other_forms': ['view', 'add', 'change', 'delete'],
            'proceedings': ['view', 'add', 'change', 'delete'],
            'reports': ['view', 'add', 'change', 'delete'],
            'tds': ['view', 'add', 'change', 'delete'],
            'timesheet': ['view', 'add', 'change', 'delete']
        }
    },
    'Group Head': {
        'apps': {
            'accounts': ['view'],  # Read-only access to accounts
            'certificates': ['view', 'add', 'change', 'delete'],
            'clients': ['view', 'add', 'change', 'delete'],
            'contacts': ['view', 'add', 'change', 'delete'],
            'insertions': ['view', 'add', 'change', 'delete'],
            'IT_Return': ['view', 'add', 'change', 'delete'],
            'judgments': ['view', 'add', 'change', 'delete'],
            'other_forms': ['view', 'add', 'change', 'delete'],
            'proceedings': ['view', 'add', 'change', 'delete'],
            'reports': ['view', 'add', 'change', 'delete'],
            'tds': ['view', 'add', 'change', 'delete'],
            'timesheet': ['view', 'add', 'change', 'delete']
        }
    },
    'Senior Staff': {
        'apps': {
            'certificates': ['view', 'add', 'change', 'delete'],
            'clients': ['view', 'add', 'change', 'delete'],
            'contacts': ['view', 'add', 'change', 'delete'],
            'insertions': ['view', 'add', 'change', 'delete'],
            'IT_Return': ['view', 'add', 'change', 'delete'],
            'judgments': ['view', 'add', 'change', 'delete'],
            'other_forms': ['view', 'add', 'change', 'delete'],
            'proceedings': ['view', 'add', 'change', 'delete'],
            'reports': ['view', 'add', 'change', 'delete'],
            'tds': ['view', 'add', 'change', 'delete'],
            'timesheet': ['view', 'add', 'change', 'delete']
        }
    },
    'Trainee': {
        'apps': {
            'certificates': ['view', 'add'],
            'clients': ['view', 'add'],
            'contacts': ['view', 'add'],
            'insertions': ['view', 'add'],
            'IT_Return': ['view', 'add'],
            'judgments': ['view', 'add'],
            'other_forms': ['view', 'add'],
            'proceedings': ['view', 'add'],
            'tds': ['view', 'add'],
            'timesheet': ['view', 'add']
            # Note: No access to reports and accounts
        }
    }
} 
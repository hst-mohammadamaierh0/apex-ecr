{
    'name': 'HR Social Security Report',
    'version': '1.0',
    'summary': 'Add Social Security records per employee and generate PDF reports',
    'category': 'Human Resources',
    'author': 'HST mohammad amaierh',
    'depends': ['base', 'hr', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/social_security_record_views.xml',
        'views/employee_form_view.xml',
        'wizard/social_security_report_wizard_view.xml',
        'report/social_security_action.xml',
        'report/social_security_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
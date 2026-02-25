{
    'name': 'Custom Helpdesk Management',
    'version': '1.0',
    'category': 'Services/Helpdesk',
    'summary': 'Department-based Ticket Management and Automated Workload Distribution',
    'description': """
        This module enhances the Helpdesk system by:
        - Linking tickets to specific HR Departments.
        - Defining Helpdesk members and Team Leads per department.
        - Automating ticket assignment based on the 'Least Busy' member algorithm.
        - Customizing the Website Portal form with smart department filtering.
        - Restricting ticket visibility based on department ownership.
    """,
    'author': 'HST-Mohammad Amaierh',
    'depends': [
        'hr', 
        'helpdesk', 
        'website_helpdesk'
    ],
    'data': [
        'security/helpdesk_security.xml', 
        'security/ir.model.access.csv',   
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_portal_templates.xml',
        'views/hr_department_views.xml',
          
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
{
    'name': 'Apex ECR Integration',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Integrate Odoo POS with Apex ECR terminals',
    'author': 'HST - Mohammad Amayreh',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_view.xml',
        'views/pos_payment_method_view.xml',
    ],
    'assets': {
        
        'point_of_sale._assets_pos': [
            'apex_ecr_integration/static/src/js/apex_ecr_button.js',
            'apex_ecr_integration/static/src/xml/apex_ecr_payment_button.xml',
        ],
    },
    'installable': True,
    'application': False,
}

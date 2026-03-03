{
    'name': 'CRM BPO Customization',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Tailored Pipeline for BPO & Outsourcing, ISHBEK, and CS Technologies',
    'description': """
        Custom CRM workflows for:
        1. BPO & Outsourcing
        2. ISHBEK (POS & Restaurant)
        3. CS Technologies (DID/SIP)
    """,
    'author': 'Mohammad Amaierh',
    'depends': [
        'crm', 
        'project', 
        'documents', 
        'contacts',
        'mail', 
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/bpo_master_data.xml',  
        'data/crm_stage_data.xml',
        'data/ishbek_master_data.xml',
        'data/ishbek_stage_data.xml',
        'data/did_stage_data.xml',
        'data/ir_sequence_data.xml',
        'views/bpo_config_views.xml',
        'views/crm_lead_views.xml',
        'views/service_change_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
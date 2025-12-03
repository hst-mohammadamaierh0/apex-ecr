{
    'name': 'Lot Price in POS',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Automatically apply Lot/Serial Number price in POS',
    'author': 'Mohammad Amayreh',
    'license': 'LGPL-3',

    'depends': [
        'point_of_sale',
        'stock',
    ],

    'data': [
        'views/lot_price_views.xml',
        'views/pos_config_view.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'lot_price_in_pos/static/src/components/lot_price/auto_lot_price.js',
        ],
    },

    'installable': True,
    'application': False,
}

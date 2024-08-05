# -*- coding: utf-8 -*-
{
    'name': "Inventory Movement Report",

    'summary': """
        This custom Odoo module
    """,

    'description': """
        This custom Odoo module
    """,

    'author': "Doodex",
    'company': "Doodex",
    'website': "https://www.doodex.net/",

    'category': 'Warehouse',
    'version': '16.0.1.0.0',

    'depends': ['base', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/stock_history_view.xml',
        'views/views.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',

}

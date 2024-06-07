# -*- coding: utf-8 -*-
{
    'name': "Document Preview(Binary)",

    'summary': """
        Document Preview allows users to preview a document without downloading it that leads to saving
         time and storage of users.
        """,

    'description': """
         Odoo Document Preview 
        
    """,

    'author': "",

    'license': 'LGPL-3',

    'website': "",

    'category': 'Tools',

    'currency': 'EUR',

    'price': '0.0',

    'support': '',

    'images': ['static/description/banners/banner1.gif'],

    'version': '17.0.1.0.2',

    'depends': ['base', 'web', 'mail'],

    'data': [
        'views/preview_templates.xml',
        'views/user.xml',
    ],
    'qweb': ['static/src/xml/binary_preview.xml',
    ],
}

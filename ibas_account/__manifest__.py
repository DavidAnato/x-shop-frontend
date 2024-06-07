# -*- coding: utf-8 -*-
{
    'name': "ibas_account",

    'summary': """
        Customizations for accounting - IBAS - NEXTASIA""",

    'description': """
        Long description of module's purpose
    """,

    'author': "RVCS",
    'website': "https://github.com/rvcsdev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ibas_security.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'wizard/bill_approval_wizard_views.xml',
        
    ],
     
}

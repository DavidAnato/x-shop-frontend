# -*- coding: utf-8 -*-
{
    'name': "ibas_realestate",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale_management', 'hr', 'contacts', 'account_accountant', 'account_reports',

                ],

    # always loaded
    'data': [
        'security/ibas_realestate_security.xml',
        'security/ir.model.access.csv',
        'data/sale_downpayment_rate.xml',
        'data/billing_permission_menus.xml',
        'wizard/update_sale_price_wiz_views.xml',
        # 'reports/client_information_report.xml',
        'reports/report_formats.xml',
        'reports/report_invoice.xml',
        'reports/report_payment.xml',
        'reports/report_sale.xml',
        'reports/sample_computation_report.xml',
        'reports/vendor_bill_journal_items.xml',
        'reports/report_journal_entry.xml',
        'views/views.xml',
        'views/sale.xml',
        'views/client_requirement.xml',
        'views/res_partner.xml',
        'views/account.xml',
        'views/account_payment_views.xml',
        'views/templates.xml',
        'views/property_class_views.xml',
        'views/property_model_views.xml',
        'views/property_lot_views.xml',
        'views/property_finishing_views.xml',
        'views/group_views.xml',
        'views/ir_ui_menu.xml',
        'views/sale_network_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'css': ['static/src/css/nextasia.css'],
    'license': 'LGPL-3',
}

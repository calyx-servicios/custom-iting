# -*- coding: utf-8 -*-
{
    'name': "Sale Viatics",
    'summary': """
        Sales Viatics """,

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Sales',
    'version': '11.0.1.0.0',
    'depends' : ['sale','sale_margin'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/sale_viatic_wizard.xml',
        'wizard/sale_viatic_calc_wizard.xml',
        'views/sale_order_view.xml',
        'views/product_view.xml',
        'views/sale_viatic_view.xml',
        'views/menu.xml',
        'views/sale_commission_view.xml',
        'views/res_config_settings_views.xml',
    ],
}
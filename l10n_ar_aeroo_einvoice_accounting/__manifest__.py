{
    'name': 'Argentinian Like invoice Aroe Report',
    'version': '11.0.1.0.0',
    'category': 'Localization/Argentina',
    'sequence': 14,
    'author': 'Calyx Servicios S.A., Odoo Community Association (OCA)',
    'website': 'http://odoo.calyx-cloud.com.ar/',
    'license': 'AGPL-3',
    'summary': 'modify the due date format',
    'depends': [
        'l10n_ar_afipws_fe',
        # suponemos que si instalas este queres el comun tmb
        'l10n_ar_aeroo_invoice',
        # 'report_extended_account',
        # 'l10n_ar_aeroo_base',
    ],
    'external_dependencies': {
    },
    'data': [
        'report/report_configuration_defaults_data.xml',
        'report/invoice_report.xml',
        'report/invoice_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

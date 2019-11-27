##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Custom Report Iting SA',
    'version': '11.0.1.3.0',
    'category': 'Localization/Argentina',
    'sequence': 14,
    'author': 'Calyx',
    'website': '',
    'license': 'AGPL-3',
    'summary': '',
    'depends': [
        #'base',
        'web',
        'sale',
        'report_extended_stock',
        'l10n_ar_aeroo_base',
        'l10n_ar_account',
        'l10n_ar_aeroo_purchase',
        'l10n_ar_aeroo_payment_group',
        'l10n_ar_aeroo_sale',
        'account_payment_group_report_extend'
    ],
    'external_dependencies': {
    },
    'data': [
        'report.xml',
        'report/report_templates.xml',
        'report/sale_report.xml',
        'report/purchase_report.xml',
        #'report/account_invoice_report_view.xml',
        #'report/account_report.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

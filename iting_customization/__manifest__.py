##############################################################################
#
#    Copyright (C) 2019  Calyx  (http://www.calyxservicios.com.ar)
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
    'name': 'Iting Customization',
    'version': '11.0.3',
    'category': 'Tools',
    'author': "Calyx",
    'website': 'www.calyxservicios.com.ar',
    'license': 'AGPL-3',
    'summary': '''...''',
    'depends': [
        'base',
        'l10n_ar_account',
        'manual_currency_exchange_rate',
        'sale',
        'purchase',
        'purchase_on_demand',
    ],
    'external_dependencies': {
    },
    'data': [
        'view/account_invoice.xml',
        'view/users.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

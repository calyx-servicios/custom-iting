# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    viatic_ok = fields.Boolean(string='Can be used as a Viatic',default=False,
        help="Specify if the product can be selected in a sales viatic line.")
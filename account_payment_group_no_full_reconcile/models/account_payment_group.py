from odoo import models, _
from odoo.exceptions import ValidationError


class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    def post(self):
        create_from_website = self._context.get('create_from_website', False)
        create_from_statement = self._context.get('create_from_statement', False)
        create_from_expense = self._context.get('create_from_expense', False)
        self = self.with_context({})
        for rec in self:
            if not rec.payment_ids:
                raise ValidationError(_(
                    'You can not confirm a payment group without payment '
                    'lines!'))
            if (rec.payment_subtype == 'double_validation' and
                    rec.payment_difference and (not create_from_statement and
                                                not create_from_expense)):
                raise ValidationError(_(
                    'To Pay Amount and Payment Amount must be equal!'))

            # Odoo already posts payment lines when created from website or expenses.
            if not create_from_website and not create_from_expense:
                rec.payment_ids.filtered(lambda x: x.state == 'draft').post()

            counterpart_aml = rec.payment_ids.mapped('move_line_ids').filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in (
                    'payable', 'receivable'))

            if counterpart_aml and rec.to_pay_move_line_ids:
                aml_set = counterpart_aml + rec.to_pay_move_line_ids
                aml_set.with_context(skip_full_reconcile_check=True).reconcile()
                if all(aml_set.mapped('reconciled')):
                    # Create exchange difference only when the whole set is reconciled.
                    aml_set.force_full_reconcile()

            rec.state = 'posted'
        return True

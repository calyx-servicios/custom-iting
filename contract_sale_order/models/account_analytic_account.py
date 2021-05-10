# Copyright 2020 Calyx Servicios S.A
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    recurring_quotations = fields.Boolean(
        string="Generate recurring quotations automatically",
    )

    account_analytic_account_id = fields.Many2one(
        string="Account Analytic",
        comodel_name="account.analytic.account",
    )

    @api.onchange("recurring_quotations")
    def _onchange_recurring_quotations(self):
        for rec in self:
            if rec.recurring_quotations:
                rec.recurring_invoices = False

    @api.onchange("recurring_invoices")
    def _onchange_recurring_invoices(self):
        for rec in self:
            if rec.recurring_invoices:
                rec.recurring_quotations = False

    @api.multi
    def _prepare_quotation_line(self, line, quotation_id):
        quotation_line = self.env["sale.order.line"].new(
            {
                "order_id": quotation_id,
                "product_id": line.product_id.id,
                "product_uom_qty": line.quantity,
                "price_unit": line.price_unit,
                "purchase_price": line.purchase_price,
            }
        )
        quotation_line.product_id_change()
        quotation_line_vals = quotation_line._convert_to_write(
            quotation_line._cache
        )
        quotation_line_vals.update(
            {
                "price_unit": line.price_unit,
                "name": line.name,
            }
        )
        return quotation_line_vals

    @api.multi
    def _prepare_quotations(self):
        self.ensure_one()

        quotation = self.env["sale.order"].new(
            {
                "partner_id": self.partner_id.id,
                "origin": self.name,
                "contract_id": self.id,
                "analytic_account_id": self.account_analytic_account_id.id,
                "pricelist_id": self.pricelist_id.id,
            }
        )
        quotation.onchange_partner_id()
        quotation.onchange_partner_shipping_id()
        quotation.update(
            {
                "pricelist_id": self.pricelist_id.id,
            }
        )
        return quotation._convert_to_write(quotation._cache)

    @api.multi
    def _create_quotation(self):
        """
        :return: sale_order created
        """
        quotation = self.env["sale.order"].create(
            self._prepare_quotations()
        )

        for line in self.recurring_invoice_line_ids:
            quotation_line_vals = self._prepare_quotation_line(
                line, quotation.id
            )
            if quotation_line_vals:
                self.env["sale.order.line"].create(quotation_line_vals)
        return quotation

    @api.multi
    def recurring_create_quotations(self, limit=None):
        """Create quotations from contracts"""
        quotations = self.env["sale.order"]
        for contract in self:
            ref_date = (
                contract.recurring_next_date or fields.Date.today()
            )
            if (
                contract.date_start > ref_date
                or contract.date_end
                and contract.date_end < ref_date
            ):
                if self.env.context.get("cron"):
                    continue  # Don't fail on cron jobs
                raise ValidationError(
                    _("You must review start and end dates!\n%s")
                    % contract.name
                )

            old_date = fields.Date.from_string(ref_date)
            new_date = old_date + contract.get_relative_delta(
                contract.recurring_rule_type,
                contract.recurring_interval,
            )

            ctx = self.env.context.copy()
            ctx.update(
                {
                    "old_date": old_date,
                    "next_date": new_date,
                    "force_company": contract.company_id.id,
                }
            )

            quotations |= contract.with_context(ctx)._create_quotation()
            contract.write(
                {"recurring_next_date": fields.Date.to_string(new_date)}
            )

        if self.env.context.get("cron"):
            return quotations
        else:
            return self.show_recurring_quotations()

    @api.multi
    def show_recurring_quotations(self):
        self.ensure_one()
        action = self.env.ref(
            "contract_sale_order.act_recurring_quotations"
        )
        return action.read()[0]

    @api.model
    def cron_recurring_create_quotations(self, limit=None):
        today = fields.Date.today()
        contracts = self.with_context(cron=True).search(
            [
                ("recurring_quotations", "=", True),
                ("recurring_next_date", "<=", today),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", today),
            ]
        )
        return contracts.recurring_create_quotations(limit=limit)

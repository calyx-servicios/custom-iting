from odoo import models
from datetime import date


class AccountPadronRetentionPerceptionType(models.Model):
    _inherit = "account.padron.retention.perception.type"

    def create_perception_lines(self):
        today_date = date.today().replace(day=1)
        lines = self.padron_line_ids.filtered(lambda line: not line.arba_alicuot_id and line.date_from == today_date)
        for line in lines:
            line.create_arba_perception_line()


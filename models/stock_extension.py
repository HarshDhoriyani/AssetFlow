from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class StockQuantInherit(models.Model):
    _inherit = "stock.quant"

    avg_monthly_consumption = fields.Float(
        string="Avg Monthly Consumption",
        compute="_compute_avg_monthly_consumption",
        store=True,
    )
    predicted_reorder_date = fields.Date(
        string="Predicted Reorder Date",
        compute="_compute_predicted_reorder_date",
        store=True,
    )
    needs_reorder = fields.Boolean(
        string="Needs Reorder",
        compute="_compute_needs_reorder",
        store=True,
    )
    monthly_consumption = fields.Float(
        string="Last 30 Days Consumption",
        compute="_compute_monthly_consumption",
        store=True,
    )

    @api.constrains("avg_monthly_consumption", "monthly_consumption")
    def _check_consumption_not_negative(self):
        for quant in self:
            if quant.avg_monthly_consumption < 0:
                raise ValidationError("Average monthly consumption cannot be negative.")
            if quant.monthly_consumption < 0:
                raise ValidationError("Monthly consumption cannot be negative.")

    @api.depends("product_id")
    def _compute_avg_monthly_consumption(self):
        for quant in self:
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("state", "=", "done"),
                    ("date", ">=", fields.Date.today() - timedelta(days=180)),
                    ("location_dest_id.usage", "=", "internal"),
                ]
            )
            if moves:
                months = max(1, len(set(m.date.strftime("%Y-%m") for m in moves)))
                quant.avg_monthly_consumption = (
                    sum(m.product_uom_qty for m in moves) / months
                )
            else:
                quant.avg_monthly_consumption = 0.0

    @api.depends("product_id")
    def _compute_monthly_consumption(self):
        for quant in self:
            thirty_days_ago = fields.Date.today() - timedelta(days=30)
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("state", "=", "done"),
                    ("date", ">=", thirty_days_ago),
                    ("location_dest_id.usage", "=", "internal"),
                ]
            )
            quant.monthly_consumption = sum(m.product_uom_qty for m in moves)

    @api.depends("avg_monthly_consumption", "product_id")
    def _compute_predicted_reorder_date(self):
        for quant in self:
            if quant.avg_monthly_consumption > 0 and quant.product_id:
                daily_consumption = quant.avg_monthly_consumption / 30
                if daily_consumption > 0:
                    days_until_reorder = quant.quantity_available / daily_consumption
                    quant.predicted_reorder_date = fields.Date.today() + timedelta(
                        days=int(days_until_reorder)
                    )
                else:
                    quant.predicted_reorder_date = False
            else:
                quant.predicted_reorder_date = False

    @api.depends("predicted_reorder_date")
    def _compute_needs_reorder(self):
        today = fields.Date.today()
        threshold = today + timedelta(days=30)
        for quant in self:
            if (
                quant.predicted_reorder_date
                and quant.predicted_reorder_date <= threshold
            ):
                quant.needs_reorder = True
            else:
                quant.needs_reorder = False

    def action_recalculate_predictions(self):
        for quant in self:
            quant._compute_avg_monthly_consumption()
            quant._compute_monthly_consumption()
            quant._compute_predicted_reorder_date()
            quant._compute_needs_reorder()
        return True

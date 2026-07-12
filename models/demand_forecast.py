from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class DemandForecast(models.Model):
    _name = "demand.forecast"
    _description = "Demand Forecast"
    _order = "forecast_date desc"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade"
    )
    forecast_date = fields.Date(string="Forecast Date", required=True)
    predicted_qty = fields.Float(string="Predicted Quantity")
    actual_qty = fields.Float(string="Actual Quantity")
    accuracy = fields.Float(
        string="Accuracy (%)", compute="_compute_accuracy", store=True
    )
    method = fields.Selection(
        [
            ("sma", "Simple Moving Average"),
            ("ewma", "Exponential Weighted Moving Average"),
        ],
        string="Method",
        default="sma",
    )
    period = fields.Selection(
        [
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
        ],
        string="Period",
        default="monthly",
    )
    reorder_suggested = fields.Boolean(
        string="Reorder Suggested", compute="_compute_reorder_suggested", store=True
    )
    created_at = fields.Datetime(string="Created", default=fields.Datetime.now)

    @api.constrains("predicted_qty")
    def _check_predicted_qty(self):
        for forecast in self:
            if forecast.predicted_qty < 0:
                raise ValidationError("Predicted quantity cannot be negative.")

    @api.constrains("actual_qty")
    def _check_actual_qty(self):
        for forecast in self:
            if forecast.actual_qty < 0:
                raise ValidationError("Actual quantity cannot be negative.")

    @api.constrains("accuracy")
    def _check_accuracy(self):
        for forecast in self:
            if forecast.accuracy < 0 or forecast.accuracy > 100:
                raise ValidationError("Accuracy must be between 0 and 100.")

    @api.depends("predicted_qty", "actual_qty")
    def _compute_accuracy(self):
        for forecast in self:
            if forecast.actual_qty and forecast.actual_qty > 0:
                forecast.accuracy = round(
                    (
                        1
                        - abs(forecast.predicted_qty - forecast.actual_qty)
                        / forecast.actual_qty
                    )
                    * 100,
                    2,
                )
            else:
                forecast.accuracy = 0.0

    @api.depends("predicted_qty", "product_id")
    def _compute_reorder_suggested(self):
        for forecast in self:
            if forecast.product_id:
                current_stock = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", forecast.product_id.id),
                        ("location_id.usage", "=", "internal"),
                    ]
                )
                total_stock = sum(q.quantity_available for q in current_stock)
                forecast.reorder_suggested = forecast.predicted_qty * 1.1 > total_stock
            else:
                forecast.reorder_suggested = False

    def _get_monthly_consumption(self, product_id, months=12):
        consumption = []
        for i in range(months):
            start_date = fields.Date.today() - timedelta(days=30 * (i + 1))
            end_date = fields.Date.today() - timedelta(days=30 * i)
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", product_id),
                    ("state", "=", "done"),
                    ("date", ">=", start_date),
                    ("date", "<=", end_date),
                    ("location_dest_id.usage", "=", "internal"),
                ]
            )
            qty = sum(m.product_uom_qty for m in moves)
            consumption.append(qty)
        return list(reversed(consumption))

    def _forecast_sma(self, product_id, n_months=6):
        history = self._get_monthly_consumption(product_id, n_months)
        return sum(history) / len(history) if history else 0

    def _forecast_ewma(self, product_id, alpha=0.3):
        history = self._get_monthly_consumption(product_id, 12)
        if not history:
            return 0
        forecast = history[0]
        for actual in history[1:]:
            forecast = alpha * actual + (1 - alpha) * forecast
        return forecast

    def _generate_forecast_for_product(self, product_id, method="sma"):
        if method == "sma":
            predicted = self._forecast_sma(product_id)
        else:
            predicted = self._forecast_ewma(product_id)
        return self.create(
            {
                "product_id": product_id,
                "forecast_date": fields.Date.today(),
                "predicted_qty": round(predicted, 2),
                "method": method,
                "period": "monthly",
            }
        )

    def _generate_all_forecasts(self):
        products = self.env["product.product"].search([("type", "=", "product")])
        for product in products:
            self._generate_forecast_for_product(product.id, "sma")
            self._generate_forecast_for_product(product.id, "ewma")

    @api.model
    def _cron_refresh_forecasts(self):
        self._generate_all_forecasts()

    def action_recalculate_forecast(self):
        for forecast in self:
            if forecast.product_id:
                forecast._compute_accuracy()
                forecast._compute_reorder_suggested()
        return True

from odoo import models, fields, api
from datetime import date, timedelta


class MaintenancePrediction(models.Model):
    _name = "maintenance.prediction"
    _description = "Maintenance Prediction"
    _order = "prediction_date desc"

    asset_id = fields.Many2one(
        "account.asset", string="Asset", required=True, ondelete="cascade"
    )
    health_score = fields.Float(
        string="Health Score", related="asset_id.health_score", store=True
    )
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Level",
        compute="_compute_risk_level",
        store=True,
    )
    predicted_failure_date = fields.Date(
        string="Predicted Failure Date",
        compute="_compute_predicted_failure",
        store=True,
    )
    confidence = fields.Float(
        string="Confidence (%)", compute="_compute_confidence", store=True
    )
    factors = fields.Text(
        string="Prediction Factors", compute="_compute_factors", store=True
    )
    status = fields.Selection(
        [
            ("active", "Active"),
            ("confirmed", "Confirmed"),
            ("overridden", "Overridden"),
            ("maintenance_created", "Maintenance Created"),
        ],
        string="Status",
        default="active",
    )
    linked_request_id = fields.Many2one("maintenance.request", string="Linked Request")
    prediction_date = fields.Datetime(
        string="Prediction Date", default=fields.Datetime.now
    )

    @api.depends("health_score")
    def _compute_risk_level(self):
        for pred in self:
            score = pred.health_score
            if score >= 70:
                pred.risk_level = "low"
            elif score >= 50:
                pred.risk_level = "medium"
            elif score >= 30:
                pred.risk_level = "high"
            else:
                pred.risk_level = "critical"

    @api.depends("health_score")
    def _compute_predicted_failure(self):
        for pred in self:
            days_to_failure = int(pred.health_score * (365 / 100))
            pred.predicted_failure_date = date.today() + timedelta(
                days=max(7, days_to_failure)
            )

    @api.depends("asset_id")
    def _compute_confidence(self):
        for pred in self:
            asset = pred.asset_id
            confidence = 50
            if asset.usage_hours > 0:
                confidence += 10
            maintenance_count = self.env["maintenance.request"].search_count(
                [
                    ("asset_id", "=", asset.id),
                ]
            )
            if maintenance_count > 3:
                confidence += 15
            if asset.date and (date.today() - asset.date).days > 365:
                confidence += 15
            pred.confidence = min(confidence, 95)

    @api.depends("asset_id")
    def _compute_factors(self):
        for pred in self:
            asset = pred.asset_id
            factors = []
            if asset.date:
                age_years = (date.today() - asset.date).days / 365
                if age_years > 2:
                    factors.append(f"Asset age: {age_years:.1f} years")
            if asset.usage_hours > 10000:
                factors.append(f"High usage: {asset.usage_hours:.0f} hours")
            maintenance_requests = self.env["maintenance.request"].search(
                [
                    ("asset_id", "=", asset.id),
                ]
            )
            if maintenance_requests:
                last_maint = maintenance_requests[-1]
                if last_maint.date:
                    days_since = (date.today() - last_maint.date).days
                    if days_since > 180:
                        factors.append(f"No maintenance for {days_since} days")
            maint_count = len(maintenance_requests)
            if maint_count > 5:
                factors.append(f"Frequent repairs: {maint_count} times")
            pred.factors = (
                "\n".join(factors) if factors else "No significant risk factors"
            )

    def _generate_prediction_for_asset(self, asset):
        existing = self.search(
            [
                ("asset_id", "=", asset.id),
                ("status", "=", "active"),
            ],
            limit=1,
        )
        vals = {"asset_id": asset.id}
        if existing:
            existing.write(vals)
            return existing
        return self.create(vals)

    def _generate_all_predictions(self):
        assets = self.env["account.asset"].search(
            [("state", "=", "posted"), ("value", ">", 0)]
        )
        for asset in assets:
            self._generate_prediction_for_asset(asset)

    @api.model
    def _cron_update_predictions(self):
        self._generate_all_predictions()

    def action_create_maintenance_request(self):
        self.ensure_one()
        request = self.env["maintenance.request"].create(
            {
                "name": f"Predictive: {self.asset_id.name}",
                "asset_id": self.asset_id.id,
                "maintenance_type": "corrective",
                "priority": "3" if self.risk_level in ["high", "critical"] else "2",
                "state": "new",
                "description": f"AI Prediction: Health {self.health_score}/100. Risk: {self.risk_level}\n\n{self.factors}",
                "date": self.predicted_failure_date,
            }
        )
        self.write({"status": "maintenance_created", "linked_request_id": request.id})
        return {
            "type": "ir.actions.act_window",
            "res_model": "maintenance.request",
            "res_id": request.id,
            "view_mode": "form",
            "target": "current",
        }

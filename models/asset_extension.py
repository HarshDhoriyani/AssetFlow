from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class AssetExtension(models.Model):
    _inherit = "account.asset"

    health_score = fields.Float(
        string="Health Score", compute="_compute_health_score", store=True
    )
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Level",
        compute="_compute_health_score",
        store=True,
    )
    predicted_failure_date = fields.Date(
        string="Predicted Failure Date", compute="_compute_health_score", store=True
    )
    usage_hours = fields.Float(string="Usage Hours", default=0)
    asset_code = fields.Char(
        string="Asset Code", required=True, copy=False, default="AST-0001"
    )
    asset_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("under_maintenance", "Under Maintenance"),
            ("retired", "Retired"),
        ],
        string="Asset Status",
        default="draft",
    )
    current_location = fields.Char(string="Current Location")
    assigned_employee = fields.Many2one("hr.employee", string="Assigned To")
    warranty_expiry = fields.Date(string="Warranty Expiry")
    expected_life_years = fields.Integer(string="Expected Life (Years)", default=5)
    prediction_ids = fields.One2many(
        "maintenance.prediction", "asset_id", string="Predictions"
    )

    @api.constrains("usage_hours")
    def _check_usage_hours(self):
        for asset in self:
            if asset.usage_hours < 0:
                raise ValidationError("Usage hours cannot be negative.")

    @api.constrains("health_score")
    def _check_health_score(self):
        for asset in self:
            if asset.health_score < 0 or asset.health_score > 100:
                raise ValidationError("Health score must be between 0 and 100.")

    @api.constrains("expected_life_years")
    def _check_expected_life(self):
        for asset in self:
            if asset.expected_life_years < 0:
                raise ValidationError("Expected life years cannot be negative.")

    @api.constrains("date")
    def _check_purchase_date(self):
        for asset in self:
            if asset.date and asset.date > date.today():
                raise ValidationError("Purchase date cannot be in the future.")

    @api.depends("date", "value", "salvage_value", "usage_hours")
    def _compute_health_score(self):
        for asset in self:
            score = 100
            today = date.today()

            if asset.date:
                age_years = (today - asset.date).days / 365
                if age_years > 2:
                    score -= 15
                if age_years > 5:
                    score -= 30

            if asset.usage_hours > 10000:
                score -= 20
            if asset.usage_hours > 25000:
                score -= 35

            maintenance_requests = self.env["maintenance.request"].search(
                [
                    ("asset_id", "=", asset.id),
                    ("state", "=", "done"),
                ]
            )
            if maintenance_requests:
                last_maint_date = max(m.date for m in maintenance_requests if m.date)
                if last_maint_date:
                    days_since = (today - last_maint_date).days
                    if days_since > 180:
                        score -= 25
                    if days_since > 365:
                        score -= 40

            maint_count = len(maintenance_requests)
            if maint_count > 5:
                score -= 10
            if maint_count > 10:
                score -= 20

            score = max(0, score)
            risk = (
                "low"
                if score >= 70
                else "medium"
                if score >= 50
                else "high"
                if score >= 30
                else "critical"
            )
            days_to_failure = int(score * (365 / 100))
            predicted_date = today + timedelta(days=max(7, days_to_failure))

            asset.health_score = score
            asset.risk_level = risk
            asset.predicted_failure_date = predicted_date

    def action_recalculate_health(self):
        for asset in self:
            asset._compute_health_score()
        return True

    @api.model
    def _cron_recalculate_health_scores(self):
        assets = self.search([("state", "=", "posted"), ("value", ">", 0)])
        for asset in assets:
            asset._compute_health_score()

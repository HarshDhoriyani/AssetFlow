from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class AssetExtension(models.Model):
    _inherit = "assetflow.asset"

    usage_hours = fields.Float(string="Usage Hours", default=0)
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
    prediction_ids = fields.One2many(
        "assetflow.maintenance.prediction", "asset_id", string="Predictions"
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

    @api.constrains("purchase_date")
    def _check_purchase_date(self):
        for asset in self:
            if asset.purchase_date and asset.purchase_date > date.today():
                raise ValidationError("Purchase date cannot be in the future.")

    @api.depends("purchase_date", "usage_hours", "state")
    def _compute_health_score(self):
        for asset in self:
            score = 100
            today = date.today()

            if asset.purchase_date:
                age_years = (today - asset.purchase_date).days / 365
                if age_years > 2:
                    score -= 15
                if age_years > 5:
                    score -= 30

            if asset.usage_hours > 10000:
                score -= 20
            if asset.usage_hours > 25000:
                score -= 35

            maint_requests = self.env["assetflow.maintenance.request"].search(
                [
                    ("asset_id", "=", asset.id),
                    ("status", "=", "done"),
                ]
            )
            if maint_requests:
                completed = maint_requests.filtered(lambda r: r.completion_date)
                if completed:
                    last_maint_date = max(completed.mapped("completion_date"))
                    days_since = (today - last_maint_date).days
                    if days_since > 180:
                        score -= 25
                    if days_since > 365:
                        score -= 40

            maint_count = len(maint_requests)
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
        assets = self.search([("state", "in", ["active", "allocated", "maintenance"])])
        for asset in assets:
            asset._compute_health_score()

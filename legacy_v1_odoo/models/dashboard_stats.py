from odoo import models, fields, api
from datetime import date, timedelta


class DashboardStats(models.Model):
    _name = "assetflow.dashboard.stats"
    _description = "Dashboard Statistics"

    name = fields.Char(string="Name", default="Dashboard Stats")
    
    total_active_assets = fields.Integer(compute="_compute_dashboard_kpis")
    pending_maintenance_count = fields.Integer(compute="_compute_dashboard_kpis")
    critical_risk_count = fields.Integer(compute="_compute_dashboard_kpis")
    budget_leakage = fields.Monetary(compute="_compute_dashboard_kpis", currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    def _compute_dashboard_kpis(self):
        for rec in self:
            asset_metrics = rec.get_asset_metrics()
            maint_metrics = rec.get_maintenance_metrics()
            rec.total_active_assets = asset_metrics.get("active", 0)
            rec.critical_risk_count = asset_metrics.get("critical_risk_count", 0)
            rec.pending_maintenance_count = maint_metrics.get("open_maintenance", 0)
            # Budget leakage isn't currently calculated in metrics, returning 0 for now
            rec.budget_leakage = 0.0

    def get_asset_metrics(self):
        assets = self.env["assetflow.asset"].search([])
        active = self.env["assetflow.asset"].search_count([("state", "=", "active")])
        allocated = self.env["assetflow.asset"].search_count(
            [("state", "=", "allocated")]
        )
        under_maintenance = self.env["assetflow.asset"].search_count(
            [("state", "=", "maintenance")]
        )
        retired = self.env["assetflow.asset"].search_count([("state", "=", "retired")])
        avg_health = sum(a.health_score for a in assets if a.health_score) / max(
            len(assets), 1
        )
        critical_count = self.env["assetflow.asset"].search_count(
            [("risk_level", "=", "critical")]
        )
        upcoming_failures = self.env["assetflow.asset"].search_count(
            [
                ("predicted_failure_date", ">=", date.today()),
                ("predicted_failure_date", "<=", date.today() + timedelta(days=30)),
                ("state", "in", ["active", "allocated"]),
            ]
        )
        return {
            "total_assets": len(assets),
            "active": active,
            "allocated": allocated,
            "under_maintenance": under_maintenance,
            "retired": retired,
            "avg_health_score": round(avg_health, 1),
            "critical_risk_count": critical_count,
            "upcoming_failures_30d": upcoming_failures,
        }

    def get_inventory_metrics(self):
        quants = self.env["stock.quant"].search(
            [
                ("location_id.usage", "=", "internal"),
            ]
        )
        needs_reorder = self.env["stock.quant"].search_count(
            [
                ("needs_reorder", "=", True),
                ("location_id.usage", "=", "internal"),
            ]
        )
        total_value = sum(
            q.quantity_available * q.product_id.standard_price for q in quants
        )
        forecasts = self.env["assetflow.demand.forecast"].search([])
        avg_accuracy = sum(f.accuracy for f in forecasts if f.accuracy) / max(
            len(forecasts), 1
        )
        return {
            "items_need_reorder": needs_reorder,
            "total_inventory_value": round(total_value, 2),
            "forecast_accuracy": round(avg_accuracy, 1),
        }

    def get_maintenance_metrics(self):
        open_requests = self.env["assetflow.maintenance.request"].search_count(
            [
                ("status", "not in", ["completed", "verified"]),
            ]
        )
        overdue = self.env["assetflow.maintenance.request"].search_count(
            [
                ("status", "not in", ["completed", "verified"]),
                ("scheduled_date", "<", date.today()),
            ]
        )
        completed = self.env["assetflow.maintenance.request"].search_count(
            [
                ("status", "in", ["completed", "verified"]),
            ]
        )
        total = self.env["assetflow.maintenance.request"].search_count([])
        completion_rate = (completed / max(total, 1)) * 100
        return {
            "open_maintenance": open_requests,
            "overdue_maintenance": overdue,
            "completion_rate": round(completion_rate, 1),
        }

    def get_health_distribution(self):
        return {
            "low": self.env["assetflow.asset"].search_count(
                [("risk_level", "=", "low")]
            ),
            "medium": self.env["assetflow.asset"].search_count(
                [("risk_level", "=", "medium")]
            ),
            "high": self.env["assetflow.asset"].search_count(
                [("risk_level", "=", "high")]
            ),
            "critical": self.env["assetflow.asset"].search_count(
                [("risk_level", "=", "critical")]
            ),
        }

    def get_all_metrics(self):
        return {
            "assets": self.get_asset_metrics(),
            "inventory": self.get_inventory_metrics(),
            "maintenance": self.get_maintenance_metrics(),
            "health_distribution": self.get_health_distribution(),
        }

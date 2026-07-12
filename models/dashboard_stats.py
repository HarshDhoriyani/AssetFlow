# models/dashboard_stats.py

from odoo import models, fields


class DashboardStats(models.Model):
    _name = 'assetflow.dashboard.stats'
    _description = 'Dashboard Stats'

    name = fields.Char(string='Name')

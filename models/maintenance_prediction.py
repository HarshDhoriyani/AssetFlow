# models/maintenance_prediction.py

from odoo import models, fields


class MaintenancePrediction(models.Model):
    _name = 'assetflow.maintenance.prediction'
    _description = 'Maintenance Prediction'

    name = fields.Char(string='Name')

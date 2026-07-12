# models/demand_forecast.py

from odoo import models, fields


class DemandForecast(models.Model):
    _name = 'assetflow.demand.forecast'
    _description = 'Demand Forecast'

    name = fields.Char(string='Name')

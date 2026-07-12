# models/stock_extension.py

from odoo import models, fields


class StockExtension(models.Model):
    _name = 'assetflow.stock.extension'
    _description = 'Stock Extension'

    name = fields.Char(string='Reference')

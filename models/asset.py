# models/asset.py

from odoo import models, fields


class Asset(models.Model):
    _name = 'assetflow.asset'
    _description = 'Asset'

    name = fields.Char(string='Name')

# models/asset_category.py

from odoo import models, fields


class AssetCategory(models.Model):
    _name = 'assetflow.asset.category'
    _description = 'Asset Category'

    name = fields.Char(string='Name')

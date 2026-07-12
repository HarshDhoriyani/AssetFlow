# -*- coding: utf-8 -*-
from odoo import fields, models

class AssetflowAssetTag(models.Model):
    _name = 'assetflow.asset.tag'
    _description = 'Asset Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

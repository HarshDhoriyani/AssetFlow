# -*- coding: utf-8 -*-
from odoo import fields, models

class AssetflowLocation(models.Model):
    _name = 'assetflow.location'
    _description = 'Asset Location'
    _order = 'name'

    name = fields.Char(string='Location Name', required=True)
    parent_id = fields.Many2one('assetflow.location', string='Parent Location', index=True)
    child_ids = fields.One2many('assetflow.location', 'parent_id', string='Sub Locations')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

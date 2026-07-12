# -*- coding: utf-8 -*-
from odoo import fields, models


class AssetflowAssetCategory(models.Model):
    _name = 'assetflow.asset.category'
    _description = 'AssetFlow Asset Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    default_maintenance_interval_months = fields.Integer(
        string='Default Maintenance Interval (months)', default=12,
        help='Used as the default interval between scheduled maintenance '
             'for assets in this category.')
    default_warranty_months = fields.Integer(
        string='Default Warranty (months)', default=12)
    expected_lifespan_years = fields.Integer(
        string='Expected Lifespan (years)', default=5)
    asset_ids = fields.One2many(
        'assetflow.asset', 'category_id', string='Assets')
    asset_count = fields.Integer(
        string='Asset Count', compute='_compute_asset_count')

    def _compute_asset_count(self):
        for category in self:
            category.asset_count = len(category.asset_ids)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A category with this name already exists.'),
    ]

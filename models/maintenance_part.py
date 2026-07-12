# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AssetflowMaintenancePart(models.Model):
    _name = 'assetflow.maintenance.part'
    _description = 'AssetFlow Maintenance Part Line'

    request_id = fields.Many2one(
        'assetflow.maintenance.request', string='Maintenance Request',
        required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', string='Part / Product', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_cost = fields.Monetary(string='Unit Cost')
    currency_id = fields.Many2one(
        'res.currency', related='request_id.currency_id', store=True)
    subtotal = fields.Monetary(
        string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_cost')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_cost

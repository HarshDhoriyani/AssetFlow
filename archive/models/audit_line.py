# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AssetflowAuditLine(models.Model):
    _name = 'assetflow.audit.line'
    _description = 'AssetFlow Audit Line'
    _order = 'id'

    cycle_id = fields.Many2one(
        'assetflow.audit.cycle', string='Audit Cycle',
        required=True, ondelete='cascade')
    asset_id = fields.Many2one(
        'assetflow.asset', string='Asset', required=True)
    auditor_id = fields.Many2one('res.users', string='Auditor')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('discrepancy', 'Discrepancy'),
    ], string='Status', default='pending', required=True)
    actual_location = fields.Many2one(
        'assetflow.location', string='Actual Location Found')
    condition_notes = fields.Text(string='Condition Notes')
    image = fields.Image(string='Photo Evidence', max_width=1024, max_height=1024)
    discrepancy_type = fields.Selection([
        ('missing', 'Missing'),
        ('damaged', 'Damaged'),
        ('wrong_location', 'Wrong Location'),
        ('other', 'Other'),
    ], string='Discrepancy Type')
    resolution_notes = fields.Text(string='Resolution Notes')

    def action_mark_verified(self):
        for line in self:
            line.write({'status': 'verified'})

    def action_mark_discrepancy(self):
        for line in self:
            if not line.discrepancy_type:
                line.discrepancy_type = 'other'
            line.write({'status': 'discrepancy'})

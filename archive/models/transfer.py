# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AssetflowTransfer(models.Model):
    _name = 'assetflow.transfer'
    _description = 'AssetFlow Asset Transfer'
    _inherit = ['mail.thread']
    _order = 'request_date desc'

    asset_id = fields.Many2one(
        'assetflow.asset', string='Asset', required=True,
        ondelete='cascade', tracking=True)
    from_location = fields.Many2one(
        'assetflow.location', string='From Location', tracking=True)
    to_location = fields.Many2one(
        'assetflow.location', string='To Location', required=True, tracking=True)
    requested_by = fields.Many2one(
        'res.users', string='Requested By',
        default=lambda self: self.env.user, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)
    request_date = fields.Date(
        string='Request Date', default=fields.Date.context_today)
    approval_date = fields.Date(string='Approval Date')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True, tracking=True,
        copy=False)
    reason = fields.Text(string='Reason for Transfer')

    @api.onchange('asset_id')
    def _onchange_asset_id(self):
        if self.asset_id:
            self.from_location = self.asset_id.current_location_id

    # ------------------------------------------------------------------
    # Validation rules
    # ------------------------------------------------------------------
    @api.constrains('asset_id', 'status')
    def _check_asset_transferable(self):
        for record in self:
            if record.status in ('rejected', 'draft'):
                continue
            if record.asset_id.state == 'retired':
                raise ValidationError(_(
                    "Retired asset '%s' cannot be transferred."
                ) % record.asset_id.name)
            if record.asset_id.state == 'maintenance':
                raise ValidationError(_(
                    "Asset '%s' is under maintenance and cannot be transferred."
                ) % record.asset_id.name)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def action_request(self):
        for record in self:
            record.write({'status': 'requested'})

    def action_approve(self):
        for record in self:
            record.write({
                'status': 'approved',
                'approved_by': self.env.user.id,
                'approval_date': fields.Date.context_today(self),
            })

    def action_reject(self):
        for record in self:
            record.write({'status': 'rejected'})

    def action_start_transit(self):
        for record in self:
            if record.status != 'approved':
                raise UserError(_("Only approved transfers can start transit."))
            record.write({'status': 'in_transit'})

    def action_complete(self):
        for record in self:
            if record.status != 'in_transit':
                raise UserError(_("Only transfers in transit can be completed."))
            record.write({'status': 'completed'})
            record.asset_id.write({'current_location_id': record.to_location.id})
            record.asset_id.message_post(body=_(
                "Transferred from %(from_loc)s to %(to_loc)s.") % {
                'from_loc': record.from_location.name or _('Unknown'),
                'to_loc': record.to_location.name,
            })

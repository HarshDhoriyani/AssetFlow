# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssetflowAllocation(models.Model):
    _name = 'assetflow.allocation'
    _description = 'AssetFlow Asset Allocation'
    _inherit = ['mail.thread']
    _order = 'allocation_date desc'

    asset_id = fields.Many2one(
        'assetflow.asset', string='Asset', required=True,
        ondelete='cascade', tracking=True)
    allocated_to = fields.Many2one(
        'hr.employee', string='Allocated To', required=True, tracking=True)
    department_id = fields.Many2one(
        'hr.department', string='Department',
        related='allocated_to.department_id', store=True, readonly=True)
    allocation_date = fields.Date(
        string='Allocation Date', required=True,
        default=fields.Date.context_today, tracking=True)
    return_date = fields.Date(string='Return Date', tracking=True)
    status = fields.Selection([
        ('allocated', 'Allocated'),
        ('returned', 'Returned'),
    ], string='Status', default='allocated', required=True, tracking=True,
        copy=False)
    allocated_by = fields.Many2one(
        'res.users', string='Allocated By',
        default=lambda self: self.env.user)
    notes = fields.Text(string='Notes')

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains('asset_id', 'status')
    def _check_no_double_allocation(self):
        for record in self:
            if record.status != 'allocated':
                continue
            other = self.search([
                ('asset_id', '=', record.asset_id.id),
                ('status', '=', 'allocated'),
                ('id', '!=', record.id),
            ], limit=1)
            if other:
                raise ValidationError(_(
                    "Asset '%s' is already allocated to another employee. "
                    "Return the current allocation before creating a new one."
                ) % record.asset_id.name)

    @api.constrains('asset_id')
    def _check_asset_state(self):
        for record in self:
            if record.asset_id.state == 'retired':
                raise ValidationError(_(
                    "Retired asset '%s' cannot be allocated."
                ) % record.asset_id.name)
            if record.asset_id.state == 'maintenance':
                raise ValidationError(_(
                    "Asset '%s' is under maintenance and cannot be allocated."
                ) % record.asset_id.name)

    # ------------------------------------------------------------------
    # CRUD hooks - keep asset.state in sync
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        allocations = super().create(vals_list)
        for allocation in allocations:
            if allocation.status == 'allocated':
                allocation.asset_id.write({'state': 'allocated'})
                allocation.asset_id.message_post(body=_(
                    "Allocated to %s.") % allocation.allocated_to.name)
        return allocations

    def action_return(self):
        for allocation in self:
            if allocation.status != 'allocated':
                continue
            allocation.write({
                'status': 'returned',
                'return_date': fields.Date.context_today(self),
            })
            allocation.asset_id.write({'state': 'active'})
            allocation.asset_id.message_post(body=_(
                "Returned by %s.") % allocation.allocated_to.name)

# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetflowMaintenanceRequest(models.Model):
    _name = 'assetflow.maintenance.request'
    _description = 'AssetFlow Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    STATE_TRANSITIONS = {
        'draft': ('submitted',),
        'submitted': ('approved', 'draft'),
        'approved': ('assigned',),
        'assigned': ('in_progress',),
        'in_progress': ('completed',),
        'completed': ('verified',),
        'verified': (),
    }

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'))
    asset_id = fields.Many2one(
        'assetflow.asset', string='Asset', required=True, tracking=True)
    request_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'AI Predictive'),
    ], string='Request Type', default='corrective', required=True, tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1', tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
    ], string='Status', default='draft', required=True, tracking=True, copy=False)

    requested_by = fields.Many2one(
        'res.users', string='Requested By',
        default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')
    assigned_to = fields.Many2one('hr.employee', string='Assigned Technician')

    description = fields.Text(string='Description')
    estimated_cost = fields.Monetary(string='Estimated Cost')
    actual_cost = fields.Monetary(
        string='Actual Cost', compute='_compute_actual_cost', store=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)

    scheduled_date = fields.Date(string='Scheduled Date')
    completion_date = fields.Date(string='Completion Date')
    maintenance_notes = fields.Text(string='Maintenance Notes')

    parts_needed = fields.One2many(
        'assetflow.maintenance.part', 'request_id', string='Parts Needed')

    # Cross-team integration point: populated by Member 2's AI layer when a
    # request is auto-generated from a predictive maintenance alert.
    source_prediction_id = fields.Many2one(
        'assetflow.maintenance.prediction', string='Source Prediction',
        help='Set automatically when this request is raised by the '
             'predictive maintenance engine (Member 2).')

    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)

    @api.depends('parts_needed.subtotal')
    def _compute_actual_cost(self):
        for record in self:
            record.actual_cost = sum(record.parts_needed.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'assetflow.maintenance.request') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'status' in vals:
            for record in self:
                record._check_state_transition(vals['status'])
        return super().write(vals)

    def _check_state_transition(self, new_status):
        self.ensure_one()
        if new_status == self.status:
            return
        allowed = self.STATE_TRANSITIONS.get(self.status, ())
        if new_status not in allowed:
            raise UserError(_(
                "Invalid maintenance status change from '%(from)s' to '%(to)s'."
            ) % {'from': self.status, 'to': new_status})

    # ------------------------------------------------------------------
    # Workflow actions
    # ------------------------------------------------------------------
    def action_submit(self):
        for record in self:
            record.write({'status': 'submitted'})

    def action_approve(self):
        for record in self:
            record.write({'status': 'approved', 'approved_by': self.env.user.id})

    def action_assign(self):
        for record in self:
            if not record.assigned_to:
                raise UserError(_("Please select a technician before assigning."))
            record.write({'status': 'assigned'})

    def action_start(self):
        for record in self:
            record.write({'status': 'in_progress'})
            record.asset_id.action_send_to_maintenance()
            record.message_post(body=_("Maintenance work started."))

    def action_complete(self):
        for record in self:
            record.write({
                'status': 'completed',
                'completion_date': fields.Date.context_today(self),
            })
            record.message_post(body=_(
                "Maintenance work completed. Actual cost: %s") % record.actual_cost)

    def action_verify(self):
        for record in self:
            record.write({'status': 'verified'})
            record.asset_id.action_return_from_maintenance()
            record.message_post(body=_("Maintenance verified and closed."))

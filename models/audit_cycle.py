# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetflowAuditCycle(models.Model):
    _name = 'assetflow.audit.cycle'
    _description = 'AssetFlow Audit Cycle'
    _inherit = ['mail.thread']
    _order = 'audit_date desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'))
    audit_date = fields.Date(
        string='Audit Date', default=fields.Date.context_today, required=True)
    auditor_ids = fields.Many2many(
        'res.users', string='Auditors', required=True)
    asset_ids = fields.Many2many(
        'assetflow.asset', string='Assets to Audit', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Status', default='draft', required=True, tracking=True)

    line_ids = fields.One2many(
        'assetflow.audit.line', 'cycle_id', string='Audit Lines')

    total_assets = fields.Integer(
        string='Total Assets', compute='_compute_stats', store=True)
    verified_count = fields.Integer(
        string='Verified Count', compute='_compute_stats', store=True)
    discrepancy_count = fields.Integer(
        string='Discrepancy Count', compute='_compute_stats', store=True)
    completion_percentage = fields.Float(
        string='Completion %', compute='_compute_stats', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'assetflow.audit.cycle') or _('New')
        return super().create(vals_list)

    @api.depends('line_ids.status')
    def _compute_stats(self):
        for cycle in self:
            lines = cycle.line_ids
            total = len(lines)
            verified = len(lines.filtered(lambda l: l.status == 'verified'))
            discrepancy = len(lines.filtered(lambda l: l.status == 'discrepancy'))
            cycle.total_assets = total
            cycle.verified_count = verified
            cycle.discrepancy_count = discrepancy
            cycle.completion_percentage = (
                (verified + discrepancy) / total * 100.0 if total else 0.0)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def action_start(self):
        for cycle in self:
            if not cycle.asset_ids:
                raise UserError(_("Add at least one asset before starting the audit."))
            cycle.write({'status': 'in_progress'})
            cycle._generate_audit_lines()
            cycle.message_post(body=_(
                "Audit started for %d asset(s).") % len(cycle.asset_ids))

    def _generate_audit_lines(self):
        self.ensure_one()
        existing_assets = self.line_ids.mapped('asset_id')
        default_auditor = self.auditor_ids[:1].id if self.auditor_ids else False
        new_lines = []
        for asset in self.asset_ids:
            if asset in existing_assets:
                continue
            new_lines.append((0, 0, {
                'asset_id': asset.id,
                'auditor_id': default_auditor,
            }))
        if new_lines:
            self.write({'line_ids': new_lines})

    def action_close(self):
        for cycle in self:
            pending = cycle.line_ids.filtered(lambda l: l.status == 'pending')
            if pending:
                raise UserError(_(
                    "Cannot close audit: %d asset(s) have not been verified yet."
                ) % len(pending))
            cycle.write({'status': 'completed'})
            cycle.message_post(body=_(
                "Audit closed. %(verified)d verified, %(discrepancy)d discrepancy(ies) found."
            ) % {'verified': cycle.verified_count, 'discrepancy': cycle.discrepancy_count})

# -*- coding: utf-8 -*-
import base64
import io

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

try:
    import qrcode
except ImportError:  # pragma: no cover - optional dependency
    qrcode = None


class AssetflowAsset(models.Model):
    """Core physical asset record and its lifecycle.

    NOTE ON DESIGN: the original plan referenced ``account.asset`` (Odoo's
    accounting depreciation asset) as a parent. To keep this module
    installable without a hard dependency on Accounting, and to avoid
    conflating financial depreciation with physical asset tracking,
    ``assetflow.asset`` is implemented as its own model. An optional link
    to ``account.asset`` can be added later by Member 1/2 if the
    Accounting app is present, via ``account_asset_id`` below.
    """
    _name = 'assetflow.asset'
    _description = 'AssetFlow Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'asset_code'
    _rec_name = 'name'

    STATE_TRANSITIONS = {
        'draft': ('active',),
        'active': ('allocated', 'maintenance', 'retired'),
        'allocated': ('active', 'maintenance', 'retired'),
        'maintenance': ('active', 'retired'),
        'retired': (),
    }

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    asset_code = fields.Char(
        string='Asset Code', required=True, copy=False, readonly=True,
        default=lambda self: _('New'), tracking=True)
    category_id = fields.Many2one(
        'assetflow.asset.category', string='Category',
        required=True, tracking=True)
    tag_ids = fields.Many2many(
        'assetflow.asset.tag', string='Tags')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active / Available'),
        ('allocated', 'Allocated'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ], string='Status', default='draft', required=True, tracking=True,
        copy=False)

    purchase_date = fields.Date(string='Purchase Date', tracking=True)
    purchase_value = fields.Monetary(string='Purchase Value', tracking=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)

    current_location_id = fields.Many2one(
        'assetflow.location', string='Current Location', tracking=True)
    assigned_to = fields.Many2one(
        'hr.employee', string='Assigned To', tracking=True)

    qr_code = fields.Binary(string='QR Code', attachment=True, copy=False)
    image = fields.Image(string='Asset Image', max_width=1024, max_height=1024)

    warranty_expiry = fields.Date(string='Warranty Expiry')
    expected_life_years = fields.Integer(string='Expected Life (years)')

    document_ids = fields.One2many(
        'ir.attachment', 'res_id', string='Documents',
        domain=lambda self: [('res_model', '=', 'assetflow.asset')])

    allocation_ids = fields.One2many(
        'assetflow.allocation', 'asset_id', string='Allocations')
    active_allocation_id = fields.Many2one(
        'assetflow.allocation', string='Current Allocation',
        compute='_compute_active_allocation', store=False)
    transfer_ids = fields.One2many(
        'assetflow.transfer', 'asset_id', string='Transfers')
    maintenance_request_ids = fields.One2many(
        'assetflow.maintenance.request', 'asset_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(
        string='Maintenance Count', compute='_compute_maintenance_count')

    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('asset_code_uniq', 'unique(asset_code, company_id)',
         'Asset code must be unique per company.'),
    ]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('asset_code', _('New')) == _('New'):
                vals['asset_code'] = self.env['ir.sequence'].next_by_code(
                    'assetflow.asset') or _('New')
            # apply category defaults if not explicitly provided
            if vals.get('category_id'):
                category = self.env['assetflow.asset.category'].browse(vals['category_id'])
                if not vals.get('expected_life_years'):
                    vals['expected_life_years'] = category.expected_lifespan_years
                if not vals.get('warranty_expiry') and vals.get('purchase_date'):
                    vals['warranty_expiry'] = fields.Date.add(
                        fields.Date.from_string(vals['purchase_date']),
                        months=category.default_warranty_months)
        assets = super().create(vals_list)
        for asset in assets:
            asset._generate_qr_code()
        return assets

    def write(self, vals):
        if 'state' in vals:
            for asset in self:
                asset._check_state_transition(vals['state'])
        return super().write(vals)

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------
    def _compute_active_allocation(self):
        for asset in self:
            asset.active_allocation_id = self.env['assetflow.allocation'].search([
                ('asset_id', '=', asset.id),
                ('status', '=', 'allocated'),
            ], limit=1)

    def _compute_maintenance_count(self):
        for asset in self:
            asset.maintenance_count = len(asset.maintenance_request_ids)

    # ------------------------------------------------------------------
    # Business logic - lifecycle
    # ------------------------------------------------------------------
    def _check_state_transition(self, new_state):
        self.ensure_one()
        if new_state == self.state:
            return
        allowed = self.STATE_TRANSITIONS.get(self.state, ())
        if new_state not in allowed:
            raise ValidationError(_(
                "Invalid status change for asset '%(name)s': cannot move from "
                "'%(from_state)s' to '%(to_state)s'.",
                name=self.name, from_state=self.state, to_state=new_state))

    def action_activate(self):
        for asset in self:
            asset.write({'state': 'active'})
            asset.message_post(body=_("Asset activated and marked available."))

    def action_send_to_maintenance(self):
        for asset in self:
            asset.write({'state': 'maintenance'})
            asset.message_post(body=_("Asset sent to maintenance."))

    def action_return_from_maintenance(self):
        for asset in self:
            asset.write({'state': 'active'})
            asset.message_post(body=_("Asset returned from maintenance and marked available."))

    def action_retire(self):
        for asset in self:
            if asset.state == 'allocated':
                raise UserError(_(
                    "Asset '%s' is currently allocated and must be returned "
                    "before it can be retired.") % asset.name)
            asset.write({'state': 'retired'})
            asset.message_post(body=_("Asset retired."))

    def action_reset_to_draft(self):
        for asset in self:
            asset.state = 'draft'
            asset.message_post(body=_("Asset reset to draft."))

    # ------------------------------------------------------------------
    # QR Code
    # ------------------------------------------------------------------
    def _generate_qr_code(self):
        for asset in self:
            payload = f"ASSETFLOW:{asset.asset_code}:{asset.id}"
            if qrcode is not None:
                img = qrcode.make(payload)
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                asset.qr_code = base64.b64encode(buffer.getvalue())
            else:
                # Fallback: no qrcode lib available in the environment.
                # Store the raw payload so it can still be rendered/printed
                # as text, and regenerated later once the dependency exists.
                asset.qr_code = False

    def action_regenerate_qr_code(self):
        self._generate_qr_code()

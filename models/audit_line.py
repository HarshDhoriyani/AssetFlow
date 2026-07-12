# models/audit_line.py

from odoo import models, fields


class AuditLine(models.Model):
    _name = 'assetflow.audit.line'
    _description = 'Audit Line'

    name = fields.Char(string='Reference')

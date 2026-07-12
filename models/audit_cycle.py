# models/audit_cycle.py

from odoo import models, fields


class AuditCycle(models.Model):
    _name = 'assetflow.audit.cycle'
    _description = 'Audit Cycle'

    name = fields.Char(string='Name')

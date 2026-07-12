# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class AssetflowController(http.Controller):
    """Lightweight public endpoint so a scanned asset QR code can resolve
    to a basic status page without needing backend login.

    Member 3 (Frontend) may build a richer page/template on top of this
    route; this controller only supplies the data lookup.
    """

    @http.route('/assetflow/asset/<string:asset_code>', type='http',
                 auth='user', website=False)
    def asset_lookup(self, asset_code, **kwargs):
        asset = request.env['assetflow.asset'].search(
            [('asset_code', '=', asset_code)], limit=1)
        if not asset:
            return request.not_found()
        return request.redirect(
            f'/odoo/action-assetflow.action_assetflow_asset/{asset.id}')

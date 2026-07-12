from odoo import http


class AssetFlowController(http.Controller):
    @http.route('/assetflow/ping', type='http', auth='public')
    def ping(self):
        return 'pong'

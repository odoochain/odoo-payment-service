# -*- coding: utf-8 -*-
import re
from datetime import date
from urllib.parse import urlparse
from odoo.http import request, route
from odoo.addons.payment_jetcheckout_system.controllers.main import PayloxSystemController as Controller


class PayloxAgreementController(Controller):

    def _get_agreement_path(self):
        if request.httprequest.method == 'POST':
            address = urlparse(request.httprequest.referrer).path
        else:
            address = urlparse(request.httprequest.url).path
        return re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-[0-9a-f]+', '', address)

    def _prepare_agreements(self, agreements):
        path = self._get_agreement_path()
        page = request.env['payment.page'].sudo().search([('path', 'like', '%s%%' % path)], limit=1)
        return [(0, 0, {
            'agreement_id': aid,
            'page_id': page.id,
        }) for aid in agreements]

    def _get_agreements(self, agreement_id=False):
        if not request.env.company.system_agreement:
            return []

        path = self._get_agreement_path()
        domain = [
            ('active', '=', True),
            ('page_ids.path', 'like', '%s%%' % path),
            ('company_id', '=', request.env.company.id),
        ]
        if agreement_id:
            domain += [('id', '=', agreement_id)]
        else:
            today = date.today()
            domain += [
                '|', ('date_start', '=', False), ('date_start', '<=', today),
                '|', ('date_end', '=', False), ('date_end', '>=', today),
            ]
        return request.env['payment.agreement'].sudo().search(domain)

    def _get_tx_vals(self, **kwargs):
        vals = super()._get_tx_vals(**kwargs)
        agreements = kwargs.get('agreements', [])
        if agreements:
            vals.update({'paylox_agreement_ids': self._prepare_agreements(agreements)})
        return vals

    def _prepare(self, **kwargs):
        res = super()._prepare(**kwargs)
        res['agreements'] = self._get_agreements()
        return res

    def _prepare_system(self, *args, **kwargs):
        res = super()._prepare_system(*args, **kwargs)
        res['agreements'] = self._get_agreements()
        return res

    @route(['/my/agreement'], type='json', auth='public', website=True, csrf=False)
    def page_system_agreement(self, agreement_id, partner_id, currency_id, amount):
        agreement = self._get_agreements(agreement_id)
        if not agreement:
            return False

        partner = request.env['res.partner'].sudo().browse(partner_id)
        currency = request.env['res.currency'].sudo().browse(currency_id)
        return {
            'id': agreement.id,
            'name': agreement.name,
            'body': agreement._render_agreement({
                'partner': partner,
                'amount': amount,
                'currency': currency,
            })
        }

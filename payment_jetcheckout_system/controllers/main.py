# -*- coding: utf-8 -*-
import werkzeug
import json
import requests
import uuid
import base64
import hashlib
from datetime import datetime
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.tools.misc import formatLang, get_lang
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError
from ..models.partner import PRIMEFACTOR
from odoo.addons.payment_jetcheckout.controllers.main import JetcheckoutController as JetController


class JetcheckoutSystemController(JetController):

    def _jetcheckout_get_parent(self, datas):
        try:
            data = datas.rsplit('-', 1)
            token = data[0]
            id = int(int(data[1], 16) / PRIMEFACTOR)
            return request.env['res.partner'].sudo().search([('id', '=', id), ('access_token', '=', token)], limit=1)
        except:
            return False

    def _jetcheckout_tx_vals(self, **kwargs):
        vals = super()._jetcheckout_tx_vals(**kwargs)
        ids = kwargs.get('payment_ids',[])
        if ids:
            vals.update({'jetcheckout_item_ids': [(6, 0, ids)]})
        return vals

    def _jetcheckout_process(self, **kwargs):
        url, tx = super()._jetcheckout_tx_vals(**kwargs)
        if tx.state == 'done':
            tx.jetcheckout_item_ids.write({'paid': True, 'paid_date': datetime.now(), 'installment_count': tx.jetcheckout_installment_count})
            url = '%s?=%s' % (tx.partner_id._get_share_url(), kwargs.get('order_id'))
        return url, tx

    def _jetcheckout_system_page_values(self, company, system, parent, transaction):
        currency = company.currency_id
        lang = get_lang(request.env)
        acquirer = self._jetcheckout_get_acquirer(providers=['jetcheckout'], limit=1)
        card_family = self._jetcheckout_get_card_family(acquirer)
        return {
            'parent': parent,
            'company': company,
            'website': request.website,
            'footer': request.website.payment_footer,
            'currency': currency,
            'currency_separator' : lang.decimal_point,
            'currency_thousand' : lang.thousands_sep,
            'acquirer': acquirer,
            'card_family': card_family,
            'footer': '',
            'success_url': '/payment/card/success',
            'fail_url': '/payment/card/fail',
            'tx': transaction,
            'system': system,
        }

    @http.route('/p/<int:parent_id>/<string:access_token>', type='http', auth='public', methods=['GET'], csrf=False, sitemap=False, website=True)
    def jetcheckout_system_payment_page_legacy(self, parent_id, access_token, **kwargs):
        parent = request.env['res.partner'].sudo().browse(parent_id)
        if not parent or not parent.access_token == access_token:
            return werkzeug.utils.redirect('/404')
        token = parent._get_token()
        return self.jetcheckout_system_payment_page(token)

    @http.route('/p/<token>', type='http', auth='public', methods=['GET'], csrf=False, sitemap=False, website=True)
    def jetcheckout_system_payment_page(self, token, **kwargs):
        parent = self._jetcheckout_get_parent(token)
        if not parent:
            return werkzeug.utils.redirect('/404')

        transaction = None
        if '' in kwargs:
            transaction = request.env['payment.transaction'].sudo().search([('jetcheckout_order_id','=',kwargs[''])], limit=1)
            if not transaction:
                return werkzeug.utils.redirect('/404')

        company = parent.company_id or request.env.company
        system = company.system
        values = self._jetcheckout_system_page_values(company, system, parent, transaction)
        return request.render('payment_%s.payment_page' % system, values)

    @http.route(['/p/privacy'], type='json', auth='public', website=True, csrf=False)
    def jetcheckout_privacy_policy(self):
        return request.website.payment_privacy_policy

    @http.route(['/p/agreement'], type='json', auth='public', website=True, csrf=False)
    def jetcheckout_sale_agreement(self):
        return request.website.payment_sale_agreement

    @http.route(['/p/membership'], type='json', auth='public', website=True, csrf=False)
    def jetcheckout_membership_agreement(self):
        return request.website.payment_membership_agreement

    @http.route(['/p/contact'], type='json', auth='public', website=True, csrf=False)
    def jetcheckout_contact_page(self):
        return request.website.payment_contact_page
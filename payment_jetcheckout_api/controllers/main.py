# -*- coding: utf-8 -*-
import werkzeug
import requests
from werkzeug.exceptions import NotFound
from urllib.parse import unquote

from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.payment_jetcheckout.controllers.main import PayloxController as Controller


class PayloxApiController(Controller):

    def _confirm_bank_webhook(self, tx):
        try:
            url = tx.jetcheckout_api_bank_webhook_url
            data = {'id': tx.jetcheckout_api_id}
            response = requests.post(url, data=data)
            if response.status_code == 200:
                tx.write({
                    'state': 'pending',
                    'last_state_change': fields.Datetime.now(),
                })
            else:
                raise ValidationError('%s (Error Code: %s)' % (response.reason, response.status_code))
        except Exception as e:
            raise ValidationError(e)
        except:
            raise ValidationError('%s (Error Code: %s)' % ('Server Error', '-1'))

    def _set_hash(self, raise_exception=True, **kwargs):
        if '' in kwargs:
            hash = unquote(kwargs[''])
            self._set('hash', hash)
        elif 'hash' in kwargs:
            hash = unquote(kwargs['hash'])
            self._set('hash', hash)

        if not hash:
            if raise_exception:
                raise NotFound()
            return False
        return hash

    def _get_transaction(self):
        hash = self._get('hash')
        if not hash:
            return False

        tx = request.env['payment.transaction'].sudo().search([
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
            ('state', '=', 'draft')
        ], limit=1)
        if not tx:
            raise ValidationError(_('An error occured. Please restart your payment transaction.'))
        return tx

    def _prepare(self, transaction=None, partner=None, **kwargs):
        values = super()._prepare(transaction=transaction, partner=partner, **kwargs)
        if transaction and transaction.jetcheckout_api_ok:
            values.update({
                'partner_name': transaction.partner_name,
            })
        return values

    def _process(self, **kwargs):
        url, tx, status = super()._process(**kwargs)
        if not status and tx.jetcheckout_api_hash:
            status = True
            self._del('hash')
            url = tx.jetcheckout_api_card_return_url
        return url, tx, status

    @http.route(['/payment'], type='http', methods=['GET', 'POST'], auth='public', csrf=False, sitemap=False, website=True)
    def page_api(self, **kwargs):
        hash = self._set_hash(raise_exception=False, **kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
            ('state', 'in', ('draft', 'cancel', 'expired'))
        ], limit=1)
        if not tx:
            raise NotFound()

        if tx.jetcheckout_api_method:
            return werkzeug.utils.redirect('/payment/%s' % tx.jetcheckout_api_method)

        acquirers = Controller._get_acquirer()
        order = request.env['payment.transaction'].sudo().search([
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '!=', hash),
            ('state', '=', 'pending'),
            ('jetcheckout_api_order', '=', tx.jetcheckout_api_order)
        ], limit=1)
        values = {
            'acquirers': acquirers,
            'tx': tx,
            'order': order,
        }
        return request.render('payment_jetcheckout_api.payment_page', values, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    @http.route(['/payment/card'], type='http', methods=['GET'], auth='public', csrf=False, sitemap=False, website=True)
    def page_api_card(self, **kwargs):
        hash = self._set_hash(raise_exception=False, **kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
            ('state', 'in', ('draft', 'cancel', 'expired'))
        ], limit=1)
        if not tx:
            raise NotFound()
        elif tx.jetcheckout_api_method and tx.jetcheckout_api_method != 'card':
            raise NotFound()

        acquirer = request.env['payment.acquirer']._get_acquirer(
            company=tx.company_id,
            website=request.website,
            providers=['jetcheckout'],
            limit=1,
        )
        values = self._prepare(
            acquirer=acquirer,
            company=tx.company_id,
            balance=False
        )
        values = self._prepare(acquirer=acquirer, company=tx.company_id, transaction=tx, balance=False)
        values.update({'tx': tx})
        return request.render('payment_jetcheckout_api.page_card', values, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    @http.route(['/payment/bank'], type='http', methods=['GET'], auth='public', csrf=False, sitemap=False, website=True)
    def page_api_bank(self, **kwargs):
        hash = self._set_hash(**kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('state', '=', 'draft'),
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
        ], limit=1)
        if not tx:
            raise NotFound()
        elif tx.jetcheckout_api_method and tx.jetcheckout_api_method != 'bank':
            raise NotFound()

        order = request.env['payment.transaction'].sudo().search([
            ('state', '=', 'pending'),
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '!=', hash),
            ('jetcheckout_api_order', '=', tx.jetcheckout_api_order),
        ], limit=1)
        if order:
            self._confirm_bank_webhook(tx)
            return werkzeug.utils.redirect('/payment/bank/result')

        acquirer = request.env['payment.acquirer']._get_acquirer(
            company=tx.company_id,
            website=request.website,
            providers=['transfer'],
            limit=1,
        )
        values = self._prepare(
            acquirer=acquirer,
            company=tx.company_id,
            balance=False
        )
        values.update({'tx': tx})
        return request.render('payment_jetcheckout_api.payment_bank_page', values, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    @http.route(['/payment/bank/result'], type='http', methods=['GET'], auth='public', csrf=False, sitemap=False, website=True)
    def page_api_bank_result(self, **kwargs):
        hash = self._set_hash(**kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('state', '=', 'pending'),
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
        ], limit=1)
        if not tx:
            raise NotFound()
        elif tx.jetcheckout_api_method and tx.jetcheckout_api_method != 'bank':
            raise NotFound()

        acquirer = request.env['payment.acquirer']._get_acquirer(
            company=tx.company_id,
            website=request.website,
            providers=['transfer'],
            limit=1,
        )
        values = self._prepare(
            acquirer=acquirer,
            company=tx.company_id,
            balance=False
        )
        values.update({'tx': tx})
        return request.render('payment_jetcheckout_api.payment_bank_page', values, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })

    @http.route(['/payment/bank/confirm'], type='json', auth='public')
    def page_api_confirm(self, **kwargs):
        hash = self._set_hash(raise_exception=False, **kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('state', '=', 'draft'),
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash),
        ], limit=1)
        if not tx:
            return '/404'
        elif tx.jetcheckout_api_method and tx.jetcheckout_api_method != 'bank':
            return '/404'

        self._confirm_bank_webhook(tx)
        return '/payment/bank/result'

    @http.route(['/payment/bank/return'], type='json', auth='public')
    def page_api_return(self, **kwargs):
        hash = self._set_hash(raise_exception=False, **kwargs)
        tx = request.env['payment.transaction'].sudo().search([
            ('jetcheckout_api_hash', '!=', False),
            ('jetcheckout_api_hash', '=', hash)
        ], limit=1)
        if not tx:
            return '/404'
        elif tx.jetcheckout_api_method and tx.jetcheckout_api_method != 'bank':
            return '/404'

        self._del()
        return tx.jetcheckout_api_bank_return_url

# -*- coding: utf-8 -*-
import requests
import logging
import json

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _calc_is_jetcheckout(self):
        for rec in self:
            rec.is_jetcheckout = rec.acquirer_id.provider == 'jetcheckout'

    def _calc_installment_description_long(self):
        for rec in self:
            desc = rec.jetcheckout_installment_description
            desc_long = ''
            try:
                installment = int(desc)
                if installment == 0:
                    desc_long = ''
                elif installment == 1:
                    desc_long = _('Single payment')
                else:
                    desc_long = _('%s installment') % desc
            except:
                desc_long = desc
            rec.jetcheckout_installment_description_long = desc_long

    @api.model
    def _get_default_partner_country_id(self):
        country = self.env.company.country_id
        if not country:
            raise ValidationError(_('Please define a country for this company'))
        return country.id

    partner_vat = fields.Char(string="VAT")
    state = fields.Selection(selection_add=[('expired', 'Expired')], ondelete={'expired': lambda recs: recs.write({'state': 'cancel'})})
    is_jetcheckout = fields.Boolean(compute='_calc_is_jetcheckout')
    jetcheckout_api_ok = fields.Boolean('API Active', readonly=True, copy=False)
    jetcheckout_payment_ok = fields.Boolean('Payment Required', readonly=True, copy=False)
    jetcheckout_campaign_name = fields.Char('Campaign Name', readonly=True, copy=False)
    jetcheckout_card_name = fields.Char('Card Holder Name', readonly=True, copy=False)
    jetcheckout_card_number = fields.Char('Card Number', readonly=True, copy=False)
    jetcheckout_card_type = fields.Char('Card Type', readonly=True, copy=False)
    jetcheckout_card_family = fields.Char('Card Family', readonly=True, copy=False)
    jetcheckout_vpos_name = fields.Char('Virtual PoS', readonly=True, copy=False)
    jetcheckout_vpos_ref = fields.Char('Virtual PoS Reference', readonly=True, copy=False)
    jetcheckout_order_id = fields.Char('Order', readonly=True, copy=False)
    jetcheckout_ip_address = fields.Char('IP Address', readonly=True, copy=False)
    jetcheckout_transaction_id = fields.Char('Transaction', readonly=True, copy=False)
    jetcheckout_payment_amount = fields.Monetary('Payment Amount', readonly=True, copy=False)
    jetcheckout_installment_count = fields.Integer('Installment Count', readonly=True, copy=False)
    jetcheckout_installment_description = fields.Char('Installment Description', readonly=True, copy=False)
    jetcheckout_installment_description_long = fields.Char('Installment Long Description', readonly=True, compute='_calc_installment_description_long')
    jetcheckout_installment_amount = fields.Monetary('Installment Amount', readonly=True, copy=False)
    jetcheckout_commission_rate = fields.Float('Commission Rate', readonly=True, copy=False)
    jetcheckout_commission_amount = fields.Monetary('Commission Amount', readonly=True, copy=False)
    jetcheckout_customer_rate = fields.Float('Customer Commission Rate', readonly=True, copy=False)
    jetcheckout_customer_amount = fields.Monetary('Customer Commission Amount', readonly=True, copy=False)
    jetcheckout_website_id = fields.Many2one('website', 'Website', readonly=True, copy=False)
    jetcheckout_date_expiration = fields.Datetime('Expiration Date', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if 'partner_vat' not in values:
                partner = self.env['res.partner'].browse(values['partner_id'])
                values.update({'partner_vat': partner.vat})

        txs = super().create(values_list)

        for tx in txs:
            partner_phone = tx.partner_id.mobile or tx.partner_id.phone
            if partner_phone:
                tx.write({'partner_phone': partner_phone})
        return txs

    def unlink(self):
        for tx in self:
            if tx.state not in ('draft', 'pending'):
                raise ValidationError(_('Only "Draft" or "Pending" payment transactions can be removed'))
        return super().unlink()

    def _jetcheckout_api_status(self):
        url = '%s/api/v1/payment/status' % self.acquirer_id._get_jetcheckout_api_url()
        data = {
            "application_key": self.acquirer_id.jetcheckout_api_key,
            "order_id": self.jetcheckout_order_id,
            "lang": "tr",
        }

        response = requests.post(url, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            if result['response_code'] == "00200":
                values = {'result': result}
            else:
                values = {'error': _('%s (Error Code: %s)') % (result['message'], result['response_code'])}
        else:
            values = {'error': _('%s (Error Code: %s)') % (response.reason, response.status_code)}
        return values

    def _jetcheckout_payment(self, vals={}):
        if self.payment_id:
            return False

        line = self.env.context.get('journal_line') or self.acquirer_id.sudo()._get_journal_line(self.jetcheckout_vpos_name, self.jetcheckout_vpos_ref)
        if not line:
            self.state_message = _('There is no journal line for %s in %s') % (self.jetcheckout_vpos_name, self.acquirer_id.name)
            return False

        payment_method = self.env.ref('payment_jetcheckout.payment_method_jetcheckout')
        payment_method_line = line.journal_id.inbound_payment_method_line_ids.filtered(lambda x: x.payment_method_id.id == payment_method.id)
        if not payment_method_line:
            self.state_message = _('Jetcheckout payment method has not been set yet on inbound payment methods of journal %s.' % line.journal_id.name)
            return False

        values = {
            'amount': abs(self.amount),
            'partner_id': self.partner_id.commercial_partner_id.id,
            'journal_id': line.journal_id.id,
            'payment_method_line_id': payment_method_line.id,
            'payment_token_id': self.token_id.id,
            'payment_transaction_id': self.id,
            'ref': self.reference
        }
        if vals:
            values.update({**vals})

        payment = self.env['account.payment'].with_context(line=line, skip_account_move_synchronization=True).create(values)

        if not self.env.context.get('post_later'):
            payment.post_with_jetcheckout(line, self.jetcheckout_customer_amount, self.jetcheckout_ip_address)

        self.write({
            'payment_id': payment.id,
            'jetcheckout_payment_ok': True,
        })
        return payment

    def _jetcheckout_refund_postprocess(self, amount=None):
        values = {
            'jetcheckout_card_name': self.jetcheckout_card_name,
            'jetcheckout_card_number': self.jetcheckout_card_number,
            'jetcheckout_card_type': self.jetcheckout_card_type,
            'jetcheckout_card_family': self.jetcheckout_card_family,
            'jetcheckout_vpos_name': self.jetcheckout_vpos_name,
            'is_post_processed': True,
            'state': 'done',
            'state_message': _('Transaction has been refunded successfully.'),
            'last_state_change': fields.Datetime.now(),
        }
        transaction = self._create_refund_transaction(amount_to_refund=amount, **values)
        transaction._log_sent_message()

    def _jetcheckout_api_refund(self, amount=0.0, **kwargs):
        self.ensure_one()
        url = '%s/api/v1/payment/refund' % self.acquirer_id._get_jetcheckout_api_url()
        data = {
            "application_key": self.acquirer_id.jetcheckout_api_key,
            "order_id": self.jetcheckout_order_id,
            "transaction_id": self.jetcheckout_transaction_id,
            "amount": int(amount * 100),
            "currency": self.currency_id.name,
            "language": "tr",
        }

        response = requests.post(url, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            if result['response_code'] == "00":
                values = {'result': result}
            else:
                values = {'error': _('%s (Error Code: %s)') % (result['message'], result['response_code'])}
        else:
            values = {'error': _('%s (Error Code: %s)') % (response.reason, response.status_code)}

        if 'error' in values:
            raise UserError(values['error'])
        self._jetcheckout_refund_postprocess(amount)

    def _jetcheckout_api_cancel(self, **kwargs):
        self.ensure_one()
        if self.state == 'cancel':
            return {}

        url = '%s/api/v1/payment/cancel' % self.acquirer_id._get_jetcheckout_api_url()
        data = {
            "application_key": self.acquirer_id.jetcheckout_api_key,
            "order_id": self.jetcheckout_order_id,
            "transaction_id": self.jetcheckout_transaction_id,
            "language": "tr",
        }

        response = requests.post(url, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            if result['response_code'] in ("00", "01"):
                values = {'result': result}
            else:
                values = {'error': _('%s (Error Code: %s)') % (result['message'], result['response_code'])}
        else:
            values = {'error': _('%s (Error Code: %s)') % (response.reason, response.status_code)}
        return values

    def _jetcheckout_done_postprocess(self):
        if not self.state == 'done':
            self.write({
                'state': 'done',
                'last_state_change': fields.Datetime.now(),
                'state_message': _('Transaction is successful'),
            })
            self.jetcheckout_order_confirm()
            self.jetcheckout_payment()
            self.is_post_processed = True

    def jetcheckout_order_confirm(self):
        self.ensure_one()
        orders = hasattr(self, 'sale_order_ids') and self.sale_order_ids
        if not orders:
            return
        try:
            self.env.cr.commit()
            orders.filtered(lambda x: x.state not in ('sale','done')).with_context(send_email=True).action_confirm()
        except Exception as e:
            self.env.cr.rollback()
            _logger.error('Confirming order for transaction %s is failed\n%s' % (self.reference, e))

    def jetcheckout_payment(self):
        self.ensure_one()
        if not self.jetcheckout_payment_ok:
            return

        try:
            self.env.cr.commit()
            payment = self.sudo()._jetcheckout_payment()
            if payment and self.invoice_ids:
                self.invoice_ids.filtered(lambda inv: inv.state == 'draft').action_post()
                (payment.line_ids + self.invoice_ids.line_ids).filtered(lambda line: line.account_id == payment.destination_account_id and not line.reconciled).reconcile()
            self.write({
                'state_message': _('Transaction is succesful and payment has been validated.'),
            })
        except Exception as e:
            self.env.cr.rollback()
            self.write({
                'state_message': _('Transaction is succesful, but payment could not be validated. Probably one of partner or journal accounts are missing.') + '\n' + str(e),
            })
            _logger.warning('Creating payment for transaction %s is failed\n%s' % (self.reference, e))

    def _jetcheckout_cancel_postprocess(self):
        if not self.state == 'cancel':
            self.write({
                'state': 'cancel',
                'state_message': _('Transaction has been cancelled successfully.'),
                'last_state_change': fields.Datetime.now(),
            })

    def _jetcheckout_cancel(self):
        self.ensure_one()
        if not self.state == 'cancel':
            if not self.state in ('draft', 'pending'):
                values = self._jetcheckout_api_cancel()
                if 'error' in values:
                    raise UserError(values['error'])
            self._jetcheckout_cancel_postprocess()

    def jetcheckout_cancel(self):
        self.ensure_one()
        self._jetcheckout_cancel()

    def _jetcheckout_refund(self, amount):
        self.ensure_one()
        if amount > self.amount:
            raise UserError(_('Refund amount cannot be higher than total amount'))
        self._jetcheckout_api_refund(amount)

    def jetcheckout_refund(self):
        self.ensure_one()
        vals = {
            'transaction_id': self.id,
            'total': self.amount,
            'currency_id': self.currency_id.id,
        }
        refund = self.env['payment.acquirer.jetcheckout.refund'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payment.acquirer.jetcheckout.refund',
            'res_id': refund.id,
            'name': _('Create refund for %s') % self.reference,
            'view_mode': 'form',
            'target': 'new',
        }

    def _jetcheckout_process_query(self, response):
        vpos = response['virtual_pos_name']
        amount = self.jetcheckout_payment_amount
        customer_rate = response['expected_cost_rate']
        customer_amount = amount * customer_rate / 100
        amount_total = float_round(amount + customer_amount, 2)

        commission_amount = response['commission_amount']
        if amount_total:
            commission_rate = float_round(commission_amount * 100 / amount_total, 2)
        else:
            commission_rate = self.jetcheckout_customer_rate

        self.write({
            'amount': amount_total,
            'fees': commission_amount,
            'jetcheckout_vpos_name': vpos,
            'jetcheckout_customer_rate': customer_rate,
            'jetcheckout_customer_amount': customer_amount,
            'jetcheckout_commission_rate': commission_rate,
            'jetcheckout_commission_amount': commission_amount,
        })

        if response['successful']:
            if response['cancelled']:
                self._jetcheckout_cancel_postprocess()
            else:
                self._jetcheckout_done_postprocess()
        else:
            if self.state == 'error' or self.env.context.get('skip_error'):
                return
            else:
                self.write({
                    'state': 'error',
                    'state_message': _('%s (Error Code: %s)') % (response.get('message', '-'), response.get('response_code','')),
                    'last_state_change': fields.Datetime.now(),
                })

    def _jetcheckout_query(self):
        self.ensure_one()
        values = self._jetcheckout_api_status()
        if 'error' in values:
            raise UserError(values['error'])

        response = values['result']
        vals = {
            'date': response['transaction_date'][:19],
            'name': response['virtual_pos_name'],
            'successful': response['successful'],
            'completed': response['completed'],
            'cancelled': response['cancelled'],
            'threed': response['is_3d'],
            'amount': response['amount'],
            'customer_amount': response['commission_amount'],
            'customer_rate': 100 * response['commission_amount'] / response['amount'] if not response['amount'] == 0 else 0,
            'commission_amount': response['amount'] * response['expected_cost_rate'] / 100,
            'commission_rate': response['expected_cost_rate'],
            'auth_code': response['auth_code'],
            'service_ref_id': response['service_ref_id'],
            'currency_id': self.currency_id.id,
        }
        self._jetcheckout_process_query(response)
        return vals

    def jetcheckout_query(self):
        self.ensure_one()
        vals = self._jetcheckout_query()
        status = self.env['payment.acquirer.jetcheckout.status'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payment.acquirer.jetcheckout.status',
            'res_id': status.id,
            'name': _('%s Transaction Status') % self.reference,
            'view_mode': 'form',
            'target': 'new',
        }

    def _jetcheckout_expire(self):
        self.filtered(lambda x: x.state in ('draft', 'pending')).write({
            'state': 'expired',
            'state_message': _('Transaction has expired'),
            'last_state_change': fields.Datetime.now(),
        })

    @api.model
    def jetcheckout_expire(self):
        self.sudo().search([
            ('state', 'in', ('draft', 'pending')),
            ('jetcheckout_date_expiration', '!=', False),
            ('jetcheckout_date_expiration', '<', fields.Datetime.now()),
        ])._jetcheckout_expire()

    @api.model
    def jetcheckout_fix(self, companies=None, states=None):
        """
        Use this function in case of emergency when transaction records are corrupted.
        It requests data from payment service and resync related transactions.
        """
        if not companies or not states:
            return

        txs = self.sudo().search([('company_id', 'in', companies), ('state', 'in', states)])
        for tx in txs:
            try:
                tx._jetcheckout_query()
                self.env.cr.commit()
            except:
                self.cr.rollback()

# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, _
from odoo.tools.misc import formatLang


class PaymentAgreement(models.Model):
    _name = 'payment.agreement'
    _description = 'Payment System Agreement'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char(translate=True)
    text = fields.Char(translate=True)
    body = fields.Html(translate=True, sanitize=False)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    version = fields.Char()
    page_ids = fields.Many2many('payment.page', 'payment_agreement_page_rel', 'agreement_id', 'page_id', string='Pages')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _render_agreement(self, values={}):
        partner = values.get('partner', None)
        partner_name = partner and partner.name or ''
        payment_currency = values.get('currency', self.company_id.currency_id)
        payment_amount = formatLang(self.env, values.get('amount', 0), monetary=True, currency_obj=payment_currency)
        agreement = self.body \
            .replace('${partner_name}', partner_name) \
            .replace('${payment_amount}', payment_amount)
        return agreement

    def action_toggle_active(self):
        self.active = not self.active


class PaymentTransactionAgreement(models.Model):
    _name = 'payment.transaction.agreement'
    _description = 'Payment System Transaction Agreement'
    _order = 'id desc'

    def _compute_name(self):
        for tx in self:
            tx.name = tx.agreement_id.name

    path = fields.Char(readonly=True)
    pdf = fields.Binary(readonly=True)
    active = fields.Boolean(readonly=True)
    name = fields.Char(compute='_compute_name')
    body = fields.Html(sanitize=False, readonly=True)
    ip_address = fields.Char('IP Address', readonly=True)
    page_id = fields.Many2one('payment.page', readonly=True)
    agreement_id = fields.Many2one('payment.agreement', readonly=True)
    transaction_id = fields.Many2one('payment.transaction', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)

    def _render_agreement(self):
        tx = self.transaction_id
        return self.agreement_id.with_context(lang=tx.partner_lang)._render_agreement({
            'partner': tx.partner_id,
            'amount': tx.amount,
            'currency': tx.currency_id,
        })

    def action_pdf(self):
        if not self.pdf:
            icp = self.env['ir.config_parameter'].sudo()
            base_url = icp.get_param('report.url') or icp.get_param('web.base.url')
            layout = self.env.ref('payment_jetcheckout.report_layout')
            html = layout._render({'body': self.body, 'base_url': base_url})
            pdf = self.env['ir.actions.report']._run_wkhtmltopdf(
                [html],
                specific_paperformat_args={
                    'data-report-margin-top': 10,
                    'data-report-header-spacing': 10,
                }
            )
            self.sudo().write({
                'pdf': base64.b64encode(pdf)
            })
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/web/content/%s/%s/pdf?mimetype=application%%2Fpdf&download=True' % (self._name, self.id)
        }

    def action_transaction(self):
        self.ensure_one()
        action = self.env.ref('payment_jetcheckout_system.action_transaction').sudo().read()[0]
        action['res_id'] = self.transaction_id.id
        action['views'] = [[False, 'form']]
        return action

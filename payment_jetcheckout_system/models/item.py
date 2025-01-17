# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PaymentItem(models.Model):
    _name = 'payment.item'
    _description = 'Payment Items'
    _order = 'id desc'

    def _compute_name(self):
        for payment in self:
            payment.name = payment.parent_id.name

    def _compute_is_admin(self):
        is_admin = self.env.user.has_group('base.group_system')
        for payment in self:
            payment.is_admin = is_admin

    @api.onchange('child_id')
    def _onchange_child_id(self):
        self.parent_id = self.child_id.parent_id.id if self.child_id else False

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        self.child_id = self.parent_id.child_ids and self.parent_id.child_ids[0].id if self.parent_id else False

    @api.depends('amount', 'paid_amount')
    def _compute_residual(self):
        for item in self:
            item.residual_amount = item.amount - item.paid_amount

    name = fields.Char(compute='_compute_name')
    child_id = fields.Many2one('res.partner', ondelete='restrict')
    parent_id = fields.Many2one('res.partner', ondelete='restrict')
    amount = fields.Monetary()
    date = fields.Date()
    due_date = fields.Date()
    file = fields.Binary()
    paid = fields.Boolean()
    ref = fields.Char()
    description = fields.Char()
    is_admin = fields.Boolean(compute='_compute_is_admin')
    paid_amount = fields.Monetary(readonly=True)
    residual_amount = fields.Monetary(compute='_compute_residual', store=True, readonly=True)
    installment_count = fields.Integer(readonly=True)
    paid_date = fields.Datetime(readonly=True)
    vat = fields.Char(related='parent_id.vat', string='VAT', store=True)
    campaign_id = fields.Many2one(related='parent_id.campaign_id', string='Campaign')
    transaction_ids = fields.Many2many('payment.transaction', 'transaction_item_rel', 'item_id', 'transaction_id', string='Transactions')
    system = fields.Selection(selection=[], readonly=True)
    company_id = fields.Many2one('res.company', required=True, ondelete='restrict', default=lambda self: self.env.company, readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)

    def onchange(self, values, field_name, field_onchange):
        return super(PaymentItem, self.with_context(recursive_onchanges=False)).onchange(values, field_name, field_onchange)

    def action_transaction(self):
        self.ensure_one()
        action = self.env.ref('payment.action_payment_transaction').sudo().read()[0]
        action['domain'] = [('id', 'in', self.transaction_ids.ids)]
        action['context'] = {'create': False, 'edit': False, 'delete': False}
        return action

    def action_receipt(self):
        self.ensure_one()
        transaction_ids = self.transaction_ids.filtered(lambda x: x.state == 'done')
        action = self.env.ref('payment_jetcheckout.report_receipt').report_action(transaction_ids.ids)
        return action

    def action_conveyance(self):
        self.ensure_one()
        transaction_ids = self.transaction_ids.filtered(lambda x: x.state == 'done')
        action = self.env.ref('payment_jetcheckout.report_conveyance').report_action(transaction_ids.ids)
        return action

    @api.model
    def create(self, values):
        res = super().create(values)
        if not res.system:
            res.system = res.company_id.system or res.parent_id.system or res.child_id.system
        if not res.currency_id:
            res.currency_id = res.company_id.currency_id.id
        return res

    def write(self, values):
        if 'paid' in values and not values['paid']:
            values['paid_amount'] = 0
        res = super().write(values)
        for item in self:
            if not item.system:
                item.system = item.company_id.system or item.parent_id.system or item.child_id.system
            if not item.currency_id:
                item.currency_id = item.company_id.currency_id.id
        return res

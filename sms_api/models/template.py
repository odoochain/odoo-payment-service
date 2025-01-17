# -*- coding: utf-8 -*-
from odoo import models


class SmsTemplate(models.Model):
    _inherit = 'sms.template'

    def send_sms(self, pid, values={}):
        partner = self.env['res.partner'].browse(pid)
        lang = values.get('lang', partner.lang)
        phone = values.get('phone', partner.mobile)
        company_id = self.env.company.id
        provider_id = self.env['sms.provider'].get(company_id).id
        note = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        message = self._render_field('body', [partner.id], set_lang=lang)[partner.id]
        sms = self.env['sms.sms'].create({
            'partner_id': partner.id,
            'body': message,
            'number': phone,
            'state': 'outgoing',
            'provider_id': provider_id,
        })
        self.env['mail.message'].create({
            'res_id': partner.id,
            'model': 'res.partner',
            'message_type': 'sms',
            'subtype_id': note,
            'body': message,
            'notification_ids': [(0, 0, {
                'res_partner_id': partner.id,
                'sms_number': phone,
                'notification_type': 'sms',
                'sms_id': sms.id,
                'is_read': True,
                'notification_status': 'ready',
                'failure_type': '',
            })]
        })
        sms._send()

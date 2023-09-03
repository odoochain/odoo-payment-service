# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    otp_redirect_url = fields.Char(string='OTP Redirect URL')

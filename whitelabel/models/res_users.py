# -- coding: utf-8 --
# Copyright © 2022 Projet (https://www.jetcheckout.com)
# Part of Paylox License. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    chatter_position = fields.Selection(
        [("normal", "Normal"), ("sided", "Sided")],
        default="sided",
    )

    """Override to add access rights.
    Access rights are disabled by default, but allowed on some specific
    fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
    """

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["chatter_position"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["chatter_position"]

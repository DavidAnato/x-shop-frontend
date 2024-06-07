# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    active = fields.Boolean(default=True)
# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class IBASSaleOrderNetwork(models.Model):
    _name = 'sale.order.network'
    _description = 'Sale Order Network'

    name = fields.Char(string='Network Name')
    address = fields.Char()
    contact = fields.Char()
    email = fields.Char(string='Email Address')
    tin = fields.Char(string='TIN')

class IBASSaleOrderNetworkSupervisor(models.Model):
    _name = 'sale.order.network.supervisor'
    _description = 'Sale Order Network Supervisor'

    name = fields.Char(string='Supervisor Name')
    address = fields.Char()
    contact = fields.Char()
    email = fields.Char(string='Email Address')
    tin = fields.Char(string='TIN')
    network_id = fields.Many2one('sale.order.network')

class IBASSaleOrderNetworkConsultant(models.Model):
    _name = 'sale.order.network.consultant'
    _description = 'Sale Order Network Consultant'

    name = fields.Char(string='Property Consultant Name')
    address = fields.Char()
    contact = fields.Char()
    email = fields.Char(string='Email Address')
    tin = fields.Char(string='TIN')
    network_id = fields.Many2one('sale.order.network')
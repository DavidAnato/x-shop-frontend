# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IBASAccountPayment(models.Model):
    _inherit = 'account.payment'

    check_number = fields.Char(string='Check Number')
    unit_id = fields.Many2one('product.product', string='Unit', compute='_compute_unit', store=True, readonly=False)
    project_id = fields.Many2one('ibas_realestate.project', string='Project', compute='_compute_project', store=True,
                                 readonly=False)

    @api.depends('reconciled_invoice_ids', 'reconciled_invoice_ids')
    def _compute_unit(self):
        for record in self:
            if record.payment_type == 'inbound':
                first_invoice = record.invoice_ids[:1]
                record.unit_id = first_invoice.unit_id if first_invoice else False
                # if first_invoice is False then get it from reconciled_invoice_ids
                if not record.unit_id:
                    first_invoice = record.reconciled_invoice_ids[:1]
                    record.unit_id = first_invoice.unit_id if first_invoice else False

    @api.depends('unit_id')
    def _compute_project(self):
        for record in self:
            record.project_id = record.unit_id.project_id if record.unit_id else False

    def relate_unit_id(self):
        for record in self:
            record._compute_unit()

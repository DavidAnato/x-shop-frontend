# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    # NEW FIELDS
    requested_by = fields.Char()

    # INHERIT FIELDS
    state = fields.Selection(selection_add=[
        ('submitted', 'Submitted'),
        ('finance_head', 'Finance Head'),
        ('coo', 'Chief Operating Officer'),
        ('ceo', 'Chief Executive Officer'),
        ('posted', 'Posted'),
        ('reject', 'Rejected'),
    ])

    bill_state = fields.Selection(related='state', tracking=False)
    bill_status = fields.Char(compute='_compute_bill_status', string='Status')

    @api.depends('state')
    def _compute_bill_status(self):
        for record in self:
            if record.state == 'draft':
                record.bill_status = 'Draft' 
            elif record.state == 'submitted':
                record.bill_status = 'To Approve by Finance Head'
            elif record.state == 'finance_head':
                record.bill_status = 'To Approve by COO'
            elif record.state == 'coo':
                record.bill_status = 'To Approve by CEO'
            elif record.state == 'ceo':
                record.bill_status = 'To be Posted'
            elif record.state == 'posted':
                record.bill_status = 'Posted'
            elif record.state == 'cancel':
                record.bill_status = 'Cancelled'
            elif record.state == 'reject':
                record.bill_status = 'Rejected'
            else:
                record.bill_status = record.state

    def action_submit(self):
        for record in self:
            record.write({'state': 'submitted'})

    def action_approve_finance_head(self):
        for record in self:
            record.write({'state': 'finance_head'})

    def action_approve_coo(self):
        for record in self:
            record.write({'state': 'coo'})

    def action_approve_ceo(self):
        for record in self:
            record.write({'state': 'ceo'})

    def action_reject(self):
        for record in self:
            record.write({'state': 'reject'})

    def action_draft(self):
        for record in self:
            record.write({'state': 'draft'})
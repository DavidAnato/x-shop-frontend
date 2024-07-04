# -*- coding: utf-8 -*-

import logging
from amortization.amount import calculate_amortization_amount
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError
from datetime import datetime
from dateutil.relativedelta import *

_logger = logging.getLogger(__name__)


class IBASSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string='Discount (%)',
                            digits=(16, 20), default=0.0)


class IBASSale(models.Model):
    _inherit = 'sale.order'

    @api.depends('date_order')
    def _compute_currency_rate(self):
        for order in self:
            date_order = order.date_order or fields.Datetime.now()
            if isinstance(date_order, datetime):
                date_order = date_order.date()
            # Suite du code avec date_order maintenant sûr
            order.currency_rate = self.env['res.currency']._get_conversion_rate(
                order.currency_id, order.company_id.currency_id, order.company_id, date_order
            )

    # Realestate
    unit_id = fields.Many2one('product.product', string='Unit', domain=[('is_a_property', '=', True),('state', '=', 'open')])

    project_id = fields.Many2one('ibas_realestate.project', string='Project',
                                 compute="_onchange_unit_id", store=True)

    # open date order, readonly=True
    date_order = fields.Date(string='Order Date', required=True, readonly=False, index=True, copy=False, default=fields.Date.today, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    # Requirements related to properties
    reservation_line_ids = fields.One2many('ibas_realestate.requirement_reservation_line', 'sale_id', string='Reservation')
    # reservation_line_ids = fields.One2many(related='unit_id.reservation_line_ids', string='Reservation')
    # booked_sale_line_ids = fields.One2many(related='unit_id.booked_sale_line_ids', string='Booked Sale')
    booked_sale_line_ids = fields.One2many('ibas_realestate.requirement_booked_sale_line', 'sale_id', string='Booked Sale')
    # contracted_sale_line_ids = fields.One2many(related='unit_id.contracted_sale_line_ids', string='Contracted Sale')
    contracted_sale_line_ids = fields.One2many('ibas_realestate.requirement_contracted_sale_line', 'sale_id', string='Contracted Sale')
    # loan_proceeds_line_ids = fields.One2many(related='unit_id.loan_proceeds_line_ids', string='Loan Proceeds')
    loan_proceeds_line_ids = fields.One2many('ibas_realestate.requirement_contracted_sale_line','sale_id', string='Loan Proceeds')
    unit_id_state = fields.Selection(related='unit_id.state', string='Unit Status', tracking=True, store=True)
    unit_id_on_hold = fields.Boolean(related='unit_id.on_hold', string='Tech Hold')

    sale_reservation_line_ids = fields.One2many('ibas_realestate.requirement_reservation_line', 'sale_id', string='Reservation', copy=False)
    sale_booked_sale_line_ids = fields.One2many('ibas_realestate.requirement_booked_sale_line', 'sale_id', string='Booked Sale', copy=False)
    sale_contracted_sale_line_ids = fields.One2many('ibas_realestate.requirement_contracted_sale_line', 'sale_id', string='Contracted Sale (line)', copy=False)
    sale_loan_proceeds_line_ids = fields.One2many('ibas_realestate.requirement_loan_proceeds_line', 'sale_id', string='Loan Proceeds (line)', copy=False)

    requirement_confirmed = fields.Boolean(string="Requirements Confirmed?")
    requirement_created = fields.Boolean(string="Requirements Created?")

    partner_id = fields.Many2one('res.partner')

    network_id = fields.Many2one('sale.order.network', string='Network')
    network_supervisor_id = fields.Many2one('sale.order.network.supervisor', string='Supervisor')
    network_consultant_id = fields.Many2one('sale.order.network.consultant', string='Property Consultant')


    def action_show_image(self):
        print(self)
        print(self)
        print(self)
        return
        # domain = ['&', ('res_model', '=', self._name), ('res_id', '=', self.id)]
        # attachment_view = self.env.ref('mrp.view_document_file_kanban_mrp')
        # return {
        #     'name': _('Attachments'),
        #     'domain': domain,
        #     'res_model': 'mrp.document',
        #     'type': 'ir.actions.act_window',
        #     'view_id': attachment_view.id,
        #     'views': [(attachment_view.id, 'kanban'), (False, 'form')],
        #     'view_mode': 'kanban,tree,form',
        #     'help': _('''<p class="o_view_nocontent_smiling_face">
        #                 Upload files to your ECO, that will be applied to the product later
        #             </p><p>
        #                 Use this feature to store any files, like drawings or specifications.
        #             </p>'''),
        #     'limit': 80,
        #     'context': "{'default_res_model': '%s','default_res_id': %d, 'default_company_id': %s}" % (self._name, self.id, self.company_id.id)
        # }



    @api.onchange('unit_id')
    def _onchange_unit_id_open(self):
        if self.unit_id and self.unit_id.state != 'open':
            raise ValidationError("This unit is not available! Please select another unit.")

    def action_cancel(self):

        if self.unit_id:
            self.unit_id.state = 'open'
            self.unit_id.customer = False
            self.unit_id.updatePrice()
            self.unit_id.reservation_date = False
            self.unit_id.so_selling_price = 0.00

            # RETAIN SALES REQUIREMENTS ON CANCEL
            # reservation_line_ids = []
            # for reservation in self.reservation_line_ids:
            #     reservation_data = {
            #         'parent_id': reservation.parent_id.id,
            #         # 'product_id': reservation.product_id.id,
            #         'requirement': reservation.requirement.id,
            #         'compliance_date': reservation.compliance_date,
            #         'requirement_file': reservation.requirement_file,
            #         'complied': reservation.complied,
            #         'sale_id': self.id,
            #     }
            #     reservation_line_ids += [(0, 0, reservation_data)]
            # self.update({'sale_reservation_line_ids': reservation_line_ids})

            # booked_sale_line_ids = []
            # for booked_sale in self.booked_sale_line_ids:
            #     booked_sale_data = {
            #         'parent_id': booked_sale.parent_id.id,
            #         # 'product_id': booked_sale.product_id.id,
            #         'requirement': booked_sale.requirement.id,
            #         'compliance_date': booked_sale.compliance_date,
            #         'requirement_file': booked_sale.requirement_file,
            #         'complied': booked_sale.complied,
            #         'sale_id': self.id,
            #     }
            #     booked_sale_line_ids += [(0, 0, booked_sale_data)]
            # self.update({'sale_booked_sale_line_ids': booked_sale_line_ids})

            # contracted_sale_line_ids = []
            # for contracted_sale in self.contracted_sale_line_ids:
            #     contracted_sale_data = {
            #         'parent_id': contracted_sale.parent_id.id,
            #         # 'product_id': contracted_sale.product_id.id,
            #         'requirement': contracted_sale.requirement.id,
            #         'compliance_date': contracted_sale.compliance_date,
            #         'requirement_file': contracted_sale.requirement_file,
            #         'complied': contracted_sale.complied,
            #         'sale_id': self.id,
            #     }
            #     contracted_sale_line_ids += [(0, 0, contracted_sale_data)]
            # self.update({'sale_contracted_sale_line_ids': contracted_sale_line_ids})

            # loan_proceeds_line_ids = []
            # for loan_proceeds in self.loan_proceeds_line_ids:
            #     loan_proceeds_data = {
            #         'parent_id': loan_proceeds.parent_id.id,
            #         # 'product_id': loan_proceeds.product_id.id,
            #         'requirement': loan_proceeds.requirement.id,
            #         'compliance_date': loan_proceeds.compliance_date,
            #         'requirement_file': loan_proceeds.requirement_file,
            #         'complied': loan_proceeds.complied,
            #         'sale_id': self.id,
            #     }
            #     loan_proceeds_line_ids += [(0, 0, loan_proceeds_data)]
            # self.update({'sale_loan_proceeds_line_ids': loan_proceeds_line_ids})

            
            # UNLINK REQUIREMENTS
            # self.reservation_line_ids.unlink()
            # self.booked_sale_line_ids.unlink()
            # self.contracted_sale_line_ids.unlink()
            # self.loan_proceeds_line_ids.unlink()

            self.requirement_confirmed = False

            self.unit_id.current_sale_order_id = False

        return self.write({'state': 'cancel'})

    def get_requirements(self):
        for rec in self:
            if not rec.requirement_created:
                if rec.unit_id.state in ['reservation','reserved']:
                    self.update({
                        'sale_reservation_line_ids': [(5, 0, 0)]
                    })

                    def_reqts = self.env['ibas_realestate.client_requirement'].search(
                        [('default_requirement', '=', True), ('stage', '=', 'reservation')])
                    if def_reqts:
                        for target_list in def_reqts:
                            self.update({
                                'sale_reservation_line_ids': [(0, 0, {
                                    'requirement': target_list.id,
                                })],
                            })
                        self.update({'requirement_created': True,})
                    else:
                        raise ValidationError(
                            'There are no Reservation Requirements Created.')

    def booked_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'booked')])
        client_lines = []
        if self.unit_id.state == 'reserved':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.sale_reservation_line_ids:
            is_complied = False
            for line in self.sale_reservation_line_ids:
                if line.complied == True:
                    is_complied = True
                else:
                    raise ValidationError(
                        'Not all Reservation Sale Requirements are submitted. Please upload submitted files before confirming.')
            if is_complied:
                self.unit_id.state = "booked"
                # self.requirement_confirmed = True
        else:
            raise ValidationError(
                'There are no Reservation Sale requirements in the list')

        if len(client_lines) > 0:
            booked_lines = []
            for client in client_lines:
                if not self.sale_booked_sale_line_ids:
                    booked_lines.append((0, 0, client))
            self.update({'sale_booked_sale_line_ids': booked_lines})
        # else:
        #    raise UserError('There are no client requirements')

    def contracted_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'contracted')])
        client_lines = []
        if self.unit_id.state == 'booked':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.sale_booked_sale_line_ids:
            is_complied = False
            for line in self.sale_booked_sale_line_ids:
                if line.complied == True:
                    is_complied = True
                else:
                    raise ValidationError(
                        'Not all Booked Sale Requirements are submitted. Please upload submitted files before confirming.')
            if is_complied:
                self.unit_id.state = 'contracted'
        else:
            raise ValidationError(
                'There are no Booked Sale requirements in the list')

        if len(client_lines) > 0:
            contracted_lines = []
            for client in client_lines:
                if not self.sale_contracted_sale_line_ids:
                    contracted_lines.append((0, 0, client))
            self.update({'sale_contracted_sale_line_ids': contracted_lines})
        # else:
        #    raise UserError('There are no client requirements')

    def loan_proceeds(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'proceeds')])
        client_lines = []
        if self.unit_id.state == 'contracted':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.sale_contracted_sale_line_ids:
            is_complied = False
            for line in self.sale_contracted_sale_line_ids:
                if line.complied == True:
                    is_complied = True
                else:
                    raise ValidationError(
                        'Not all Contracted Requirements are submitted. Please upload submitted files before confirming.')
            if is_complied:
                self.unit_id.state = 'proceed'
        else:
            raise ValidationError(
                'There are no Contracted Sale requirements in the list')

        if len(client_lines) > 0:
            loan_proceeds_lines = []
            for client in client_lines:
                if not self.sale_loan_proceeds_line_ids:
                    loan_proceeds_lines.append((0, 0, client))
            self.update({'sale_loan_proceeds_line_ids': loan_proceeds_lines})
        # else:
        #    raise UserError('There are no client requirements')

    def acceptance(self):
        if self.sale_loan_proceeds_line_ids:
            is_complied = False
            for line in self.sale_loan_proceeds_line_ids:
                if line.complied == True:
                    is_complied = True
                else:
                    raise ValidationError(
                        'Not all Loan Proceeds Requirements are submitted. Please upload submitted files before confirming.')
            if is_complied:
                self.unit_id.state = 'accept'
        else:
            raise ValidationError(
                'There are no Loan proceeds requirements in the list')

        self.state = 'done'

    def action_confirm(self):
        forbidden_states = {'cancel', 'done'}

        if forbidden_states & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(forbidden_states)))

        if self.unit_id.state not in ['open','reservation']:
            raise UserError(_('This property is already sold'))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        self.action_compute_sc()
        if self.unit_id:
            self.unit_id.state = 'reserved'
            self.unit_id.customer = self.partner_id
            self.unit_id.reservation_date = self.date_order
            self.unit_id.so_selling_price = self.list_price
            for prop in self.unit_id:
                prop.update({
                    'price_history_line_ids': [(0, 0, {
                        'effective_date': fields.Datetime.now(),
                        'selling_price': prop.list_price,
                        'pre_selling_price': prop.preselling_price,
                    })],
                })

            if len(self.sc_ids) > 0:
                myids = self.sc_ids.sorted(key=lambda r: r.date, reverse=True)
                self.unit_id.last_dp_date = myids[0].date

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

    # @api.depends('unit_id', 'list_price')
    # def _onchange_unit_id(self):
    #     for rec in self:
    #         if rec.unit_id.id is not False:
    #             rec.project_id = rec.unit_id.project_id.id
    #             rec.pre_selling_price = rec.unit_id.preselling_price
    #             rec.list_price = rec.unit_id.list_price
    #             # rec.discount_amount = rec.pre_selling_price - rec.list_price
    #             rec.dp_terms = rec.unit_id.dp_terms

    #             self.update({
    #                 'order_line': [(5, 0, 0)]
    #             })

    #             self.update({
    #                 'order_line': [(0, 0, {
    #                     'product_id': rec.unit_id.id,
    #                     'product_uom_qty': 1,
    #                     'price_unit': rec.list_price,
    #                     'name': rec.unit_id.name,
    #                     'customer_lead': 0
    #                 })]
    #             })

    #             for line in rec.order_line:
    #                 line.product_id_change()

    @api.onchange('unit_id', 'list_price')
    def _onchange_unit_id(self):
        for rec in self:
            if rec.unit_id:
                rec.project_id = rec.unit_id.project_id.id
                rec.pre_selling_price = rec.unit_id.preselling_price
                rec.list_price = rec.unit_id.list_price
                rec.dp_terms = rec.unit_id.dp_terms

                # Clear existing order lines
                rec.order_line = [(5, 0, 0)]

                # Add new order line
                rec.order_line = [(0, 0, {
                    'product_id': rec.unit_id.id,
                    'product_uom_qty': 1,
                    'price_unit': rec.list_price,
                    'name': rec.unit_id.name,
                    'customer_lead': 0
                })]

    pre_selling_price = fields.Float(string='Pre Selling Price')
    list_price = fields.Float(string='Selling Price')

    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type', default='fixed')

    discount_amount = fields.Float(string='Discount Amount', store=True)
    discount_amount_percent = fields.Float(
        string='Discount Amount %', compute="_compute_discount_price")

    discount_rate_id = fields.Many2one(
        'sale.discount.rate', string="Discount Rate")

    discounted_price = fields.Float(
        string="Discounted Price", compute="_compute_discount_price")

    downpayment = fields.Monetary(string='Downpayment')
    fix_downpayment = fields.Monetary(string='Fix Downpayment')
    closing_fees = fields.Monetary(string='Closing Fees')
    # RESERVATION ========================================
    reservation_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Reservation Type', default='fixed')
    reservation_rate = fields.Many2one(
        'sale.reservation.rate', string='Reservation Percentage')
    reservation_amount = fields.Monetary(string='Reservation Amount')
    # RESERVATION ========================================

    # SPOT DP ============================================
    discount_spotdp_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Spot DP Type', default='fixed')

    discount_spotdp_rate = fields.Many2one(
        'sale.spotdp.rate', string='Spot DP Percentage')

    discount_spotdp = fields.Monetary(string='Spot DP Discount')
    # SPOT DP ===========================================

    disc_spot = fields.Monetary(
        string='Discount Spot DP', compute='_disc_spot')
    disc_amount = fields.Monetary(
        string='Discount Amount', compute='_disc_amount')

    # Discount price
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty *
                                    line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_discount': amount_discount,
                'amount_total': amount_untaxed + amount_tax,
            })

    discount_rate = fields.Float('Discount Rate (f)', digits='Discount', readonly=True, compute='_compute_discount_rate')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 tracking=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   tracking=True)
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all', tracking=True)

    @api.depends('disc_spot', 'disc_amount')
    def _compute_discount_rate(self):
        for rec in self:
            if rec.disc_spot != 0 or rec.disc_amount != 0:
                rec.discount_rate += rec.disc_spot
                rec.discount_rate += rec.disc_amount
            else:
                rec.discount_rate += (rec.disc_amount + rec.disc_spot)

    @api.onchange('disc_spot', 'disc_amount', 'discount_rate', 'order_line')
    def supply_rate(self):

        for order in self:
            total = discount = 0.0
            for line in order.order_line:
                total += (line.product_uom_qty * line.price_unit)
            if order.discount_rate != 0:
                discount = (order.discount_rate / total) * 100
            else:
                discount = order.discount_rate
            for line in order.order_line:
                line.discount = discount

    def _prepare_invoice(self,):
        invoice_vals = super(IBASSale, self)._prepare_invoice()
        invoice_vals.update({
            'unit_id': self.unit_id.id,
            'downpayment': self.downpayment,
            'disc_spot': self.disc_spot,
            'disc_amount': self.disc_amount,
            'invoice_date': self.date_order,
        })
        return invoice_vals

    def button_dummy(self):

        self.supply_rate()
        return True
    # Discount price
    @api.depends('discount_spotdp')
    def _disc_spot(self):
        for rec in self:
            rec.update({
                'disc_spot': rec.discount_spotdp,
            })

    @api.depends('discount_amount_percent', 'discount_amount')
    def _disc_amount(self):
        for rec in self:
            if rec.discount_type == 'fixed':
                rec.update({
                    'disc_amount': rec.discount_amount,
                })

            elif rec.discount_type == 'percentage':
                rec.update({
                    'disc_amount': rec.discount_amount_percent,
                })

            else:
                rec.update({
                    'disc_amount': 0.0,
                })

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        for rec in self:
            if rec.discount_type == "fixed":
                rec.discount_amount_percent = 0.0

            elif rec.discount_type == "percentage":
                rec.discount_amount = 0.0

            else:
                rec.discount_amount_percent = 0.0
                rec.discount_amount = 0.0

    @api.depends('discount_amount', 'discount_rate_id', 'discount_type')
    def _compute_discount_price(self):
        for rec in self:
            if rec.discount_type == "fixed":
                rec.discounted_price = rec.list_price - rec.discount_amount
                rec.discount_amount_percent = 0.0

            elif rec.discount_type == "percentage":
                rec.discount_amount_percent = rec.list_price * rec.discount_rate_id.rate
                rec.discounted_price = rec.list_price - rec.discount_amount_percent

            else:
                rec.discounted_price = rec.list_price
                rec.discount_amount_percent = 0.0

    @api.onchange('list_price')
    def _onchange_list_price(self):
        for rec in self:
            rec.downpayment = 0  # rec.list_price * 0.10 - 5000  # 50000
            rec.reservation_amount = 5000  # 50000
            rec.closing_fees = rec.list_price * 0.05
            rec.discounted_price = rec.list_price

    sc_ids = fields.One2many(
        'ibas_realestate.sample_computation.line', 'order_id', string='Sample Computation')

    def action_compute_sc(self):
        for rec in self:
            if rec.unit_id.id is not False:
                self.update({
                    'sc_ids': [(5, 0, 0)]
                })

                reserve_date = rec.date_order  # + relativedelta(hours=8)
                self.update({
                    'sc_ids': [(0, 0, {
                        'date': reserve_date,
                        'payment_amount': rec.reservation_amount,
                        'closing_fees': 0,
                        'description': 'Reservation',
                    })]
                })

                if rec.dp_terms:
                    i = 0
                    my_dp_term_int = int(rec.dp_terms)
                    monthly_closing_fees = rec.closing_fees / my_dp_term_int
                    monthly_fees = rec.downpayment / my_dp_term_int
                    # if rec.is_cash:
                    #    monthly_fees = rec.downpayment  # - rec.discount_spotdp
                    while i < my_dp_term_int:
                        month_iteration = i + 1
                        ordinal = ""
                        if month_iteration != 0:
                            if month_iteration == 1:
                                ordinal = str(month_iteration) + "st"
                            elif month_iteration == 2:
                                ordinal = str(month_iteration) + "nd"

                            elif month_iteration == 3:
                                ordinal = str(month_iteration) + "rd"

                            elif month_iteration == 21:
                                ordinal = str(month_iteration) + "st"

                            elif month_iteration == 22:
                                ordinal = str(month_iteration) + "nd"

                            elif month_iteration == 23:
                                ordinal = str(month_iteration) + "rd"

                            else:
                                ordinal = str(month_iteration) + "th"

                        mydate = rec.date_order + \
                            relativedelta(months=+month_iteration)

                        self.update({
                            'sc_ids': [(0, 0, {
                                'date': mydate,
                                'payment_amount': monthly_fees,
                                'closing_fees': monthly_closing_fees,
                                'description': ordinal + ' Downpayment',
                            })]
                        })
                        i = i + 1

    dp_terms = fields.Selection([
        ('1', '1 Month'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('4', '4 Months'),
        ('5', '5 Months'),
        ('6', '6 Months'),
        ('7', '7 Months'),
        ('8', '8 Months'),
        ('9', '9 Months'),
        ('10', '10 Months'),
        ('11', '11 Months'),
        ('12', '12 Months'),
        ('13', '13 Months'),
        ('14', '14 Months'),
        ('15', '15 Months'),
        ('16', '16 Months'),
        ('17', '17 Months'),
        ('18', '18 Months'),
        ('19', '19 Months'),
        ('20', '20 Months'),
        ('21', '21 Months'),
        ('22', '22 Months'),
        ('23', '23 Months'),
        ('24', '24 Months'),

    ], string='DP Terms')

    #is_cash = fields.Boolean(string='Cash DP')

    downpayment_type = fields.Selection(
        [('fixed', 'Fixed'), ('percentage', 'Percentage')], string='Downpayment Type', default='percentage')
    dp_per_rate = fields.Many2one(
        'sale.downpayment.rate', string='DP Rate Percentage')
    downpayment_per_rate = fields.Selection(
        [('6_5', '6.5%'), ('8_5', '8.5%'), ('10', '10%')], string='DP Percentage Rate')

    financing_type = fields.Selection([
        ('phdmf', 'Pag-IBIG'), 
        ('bankf', 'Bank Financing'),
        ('hcmf', 'HCM Financing'),
        ('spot_cash', 'Spot Cash'),
        ('differed_cash', 'Differed Cash'),
        ('nhmfc', 'NHMFC'),
        ], string='Financing Type', default='phdmf')

    # OVERRIDE
    state = fields.Selection(selection_add=[
        ('draft', 'For Reservation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')])

    @api.onchange('financing_type')
    def _Onchangefinancetype(self):
        interest_rate = 0
        interest_rate_id = False

        if self.financing_type == 'phdmf':
            interest_rate = 0.06375
        if self.financing_type in ['bankf', 'hcmf']:
            interest_rate = 0.07500

        interest_rate_id = self.env['sale.interest.rate'].search([('rate','=',interest_rate)])

        if interest_rate_id:
            self.interest_rate = interest_rate_id.id
        else:
            self.interest_rate = False

    # COMPUTE DOWNPAYMENT ========================================
    @api.onchange('list_price', 'downpayment_type', 'dp_per_rate', 'discount_spotdp', 'reservation_amount', 'discount_type', 'discount_amount', 'discount_rate_id')
    def changeDownpaymentAmount(self):
        if not self.downpayment_type:
            self.downpayment = 0.0
            self.fix_downpayment = 0.0
            rate = self.dp_per_rate = False

        elif self.downpayment_type == 'fixed':
            self.downpayment = self.list_price * 0.10 - 5000
            self.fix_downpayment = self.list_price * 0.10 - 5000
            rate = self.dp_per_rate = False

        else:
            if not self.dp_per_rate:
                self.dp_per_rate = self.env.ref('ibas_realestate.rate_10_0').id

            rate = self.dp_per_rate and self.dp_per_rate.rate / 100.00

            self.fix_downpayment = self.discounted_price * rate
            amount = 0

            if self.discount_type or self.dp_per_rate:
                amount += self.discounted_price * rate

            if self.discount_spotdp >= 0:
                dp_amount = amount - \
                    (self.reservation_amount + self.discount_spotdp)
                self.downpayment = dp_amount

            # if not self.is_cash:
            #    self.discount_spotdp = 0.0

            if self.reservation_amount >= 0:
                dp_amount = amount - \
                    (self.reservation_amount + self.discount_spotdp)
                self.downpayment = dp_amount

    # COMPUTE DOWNPAYMENT ========================================

    # COMPUTE SPOT DP RATE ========================================
    @api.onchange('discount_spotdp_type', 'discount_spotdp_rate', 'discount_amount_percent', 'discount_amount', 'fix_downpayment')
    def _onchange_discount_spotdp_rate(self):
        if not self.discount_spotdp_rate:
            self.discount_spotdp_rate = self.env.ref(
                'ibas_realestate.spotdp_rate_10_0').id

        rate = self.discount_spotdp_rate and self.discount_spotdp_rate.rate / 100.00

        if self.discount_spotdp_type == 'percentage':
            self.discount_spotdp = self.fix_downpayment * rate

        if self.discount_spotdp_type == False:
            self.discount_spotdp = 0.0

    # COMPUTE SPOT DP RATE ========================================

    # COMPUTE RESERVATION RATE ========================================
    @api.onchange('reservation_type', 'reservation_rate', 'discount_amount_percent', 'discount_amount', 'fix_downpayment')
    def _onchange_reservation_rate(self):
        if not self.reservation_rate:
            self.reservation_rate = self.env.ref(
                'ibas_realestate.reservation_rate_10_0').id

        rate = self.reservation_rate and self.reservation_rate.rate / 100.00

        if self.reservation_type == 'percentage':
            self.reservation_amount = self.fix_downpayment * rate

        if self.reservation_type == False:
            self.reservation_amount = 0.0

    # COMPUTE RESERVATION RATE ========================================

    @api.onchange('dp_terms')
    def _onchange_dp_terms(self):
        if self.unit_id:
            self.unit_id.dp_terms = self.dp_terms

    # @api.onchange('is_cash')
    # def _onchange_is_cash(self):
    #    if self.unit_id:
    #        if self.is_cash:
    #            self.dp_terms = '1'
    #            self.unit_id.dp_terms = '1'
    #        else:
    #            self.dp_terms = self.unit_id.dp_terms

    monthly_3 = fields.Monetary(
        compute='_compute_monthly_3', string='Monthly Amortization 3 Years')

    monthly_5 = fields.Monetary(
        compute='_compute_monthly_5', string='Monthly Amortization 5 Years')

    monthly_10 = fields.Monetary(
        compute='_compute_monthly_10', string='Monthly Amortization 10 Years')

    monthly_20 = fields.Monetary(
        compute='_compute_monthly_20', string='Monthly Amortization 20 Years')

    monthly_25 = fields.Monetary(
        compute='_compute_monthly_25', string='Monthly Amortization 25 Years')

    monthly_30 = fields.Monetary(
        compute='_compute_monthly_30', string='Monthly Amortization 30 Years')

    interest_rate = fields.Many2one(
        'sale.interest.rate', string='Interest Rate')

    # @api.model
    # def default_get(self, fields):
    #    res = super(IBASSale, self).default_get(fields)
    #    res['interest_rate'] = self.interest_rate[0] if self.interest_rate else None
    #    return res

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_3(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_3 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 36)
        else:
            for rec in self:
                rec.monthly_3 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 36)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_5(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_5 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 60)
        else:
            for rec in self:
                rec.monthly_5 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 60)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_10(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_10 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 120)
        else:
            for rec in self:
                rec.monthly_10 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 120)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_20(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_20 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 240)
        else:
            for rec in self:
                rec.monthly_20 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 240)

    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_25(self):
        for rec in self:
            interest_rate = 0.06375
            if rec.interest_rate:
                interest_rate = rec.interest_rate.rate
            
            rec.monthly_25 = calculate_amortization_amount(rec.loanable_amount, interest_rate / 12, 300)


    @api.depends('loanable_amount', 'interest_rate')
    def _compute_monthly_30(self):
        if self.interest_rate:
            for rec in self:
                rec.monthly_30 = calculate_amortization_amount(
                    rec.loanable_amount, rec.interest_rate.rate / 12, 360)
        else:
            for rec in self:
                rec.monthly_30 = calculate_amortization_amount(
                    rec.loanable_amount, 0.06375 / 12, 360)

    loanable_amount = fields.Monetary(
        compute='_compute_loanable_amount', string='Loanable Amount')

    @api.depends('list_price', 'downpayment')
    def _compute_loanable_amount(self):
        for rec in self:
            rec.loanable_amount = rec.discounted_price - rec.downpayment - \
                rec.reservation_amount - rec.discount_spotdp
    # For Reports
    current_date = fields.Datetime('Date', compute='_compute_report_gen_date')

    def _compute_report_gen_date(self):
        for rec in self:
            rec.current_date = fields.Datetime.now()

    def write(self, vals):
        result = super(IBASSale, self).write(vals)
        if vals.get('partner_id') and self.state != 'cancel':
            raise ValidationError('Cannot change customer during this stage. You need to cancel the sales order in order to change customer.')
        if vals.get('unit_id'):
            unit_id = self.env['product.product'].browse(vals.get('unit_id'))
            if unit_id and self.state != 'cancel':
                # unit_id.write({'state': 'reservation', 'current_sale_order_id': self.id})
                raise ValidationError('Cannot change unit during this stage. You need to cancel the sales order in order to change unit.')
            else:
                unit_id.write({'state': 'reservation', 'current_sale_order_id': self.id})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        result = super(IBASSale, self).create(vals_list)
        for vals in vals_list:
            if vals.get('unit_id'):
                unit_id = self.env['product.product'].browse(vals.get('unit_id'))
                if unit_id:
                    unit_id.write({'state': 'reservation', 'current_sale_order_id': result.id})
        return result

class SalesSampleComputationLine(models.Model):
    _name = 'ibas_realestate.sample_computation.line'
    _description = 'Sample Computation Line'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id",
                                  required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company',  required=True,
                                 default=lambda self: self.env.company.id)
    date = fields.Date(string='Date')
    payment_amount = fields.Monetary(string='Amount')
    closing_fees = fields.Monetary(string='Closing Fees')
    description = fields.Char(string='Description')
    total = fields.Monetary(compute='_compute_total', string='Total')

    order_id = fields.Many2one('sale.order', string='Order ID')

    @api.depends('payment_amount', 'closing_fees')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.payment_amount + rec.closing_fees


class SaleDownPaymentRate(models.Model):
    _name = 'sale.downpayment.rate'
    _description = 'Downpayment Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate %', digits=(5, 5))


class SaleInterestRate(models.Model):
    _name = 'sale.interest.rate'
    _description = 'Interest Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate', digits=(5, 5))


class SaleDiscountRate(models.Model):
    _name = 'sale.discount.rate'
    _description = 'Discount Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate', digits=(5, 5))


class SaleSpotDPRate(models.Model):
    _name = 'sale.spotdp.rate'
    _description = 'Spot DP Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate %', digits=(5, 5))


class SaleReservationRate(models.Model):
    _name = 'sale.reservation.rate'
    _description = 'Reservation Rate'

    name = fields.Char('Name', required=True)
    rate = fields.Float(string='Rate %', digits=(5, 5))
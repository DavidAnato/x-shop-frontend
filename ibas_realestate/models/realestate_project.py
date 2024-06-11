# -*- coding: utf-8 -*-

import logging

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class custom_partner(models.Model):
    _inherit = "res.partner"

    is_company = fields.Boolean(default=False)


class IBASREProject(models.Model):
    _name = 'ibas_realestate.project'
    _description = 'Real Estate Project'

    name = fields.Char(string='Project Name', required=True)
    address = fields.Char(string='Address')


class PropertiesProjectProperty(models.Model):
    _inherit = 'product.product'
    _description = 'Real Estate Properties'
    _sql_constraints = [('name_uniq', 'unique (name)',
                         'Duplicate products not allowed !')]

    is_a_property = fields.Boolean(string='Is A Property')

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id",
                                  required=True, string='Currency', help="Main currency of the company.")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company.id)

    @api.onchange('project_id', 'block', 'lot', 'propmodel_id')
    def _compute_name(self):
        for rec in self:
            if rec.is_a_property:

                try:
                    rec.name = rec.project_id.name + ' Block ' + rec.block + \
                               ' Lot ' + rec.lot + ' - ' + rec.propmodel_id.name
                except:
                    pass

    project_id = fields.Many2one('ibas_realestate.project', string='Project')
    block = fields.Char(string='Block')
    lot = fields.Char(string='Lot')
    phase = fields.Char('Phase')
    propmodel_id = fields.Many2one(
        'ibas_realestate.propertymodel', string='Model')

    preselling_price = fields.Monetary(string='Pre Selling Price')

    responsible = fields.Many2one('res.users', string='Account Officer')
    responsible_emp_id = fields.Many2one(
        'hr.employee', string='Account Officer')
    contractor = fields.Many2one('res.partner', string='Contractor')
    construction_status = fields.Char(string='Construction Status')
    construction_start_date = fields.Date(string='Construction Start Date')
    construction_current_date = fields.Date(string='Construction Current Date')
    construction_end_date = fields.Date(string='Construction End Date')
    actual_construction_complete_date = fields.Date(
        string='Actual Construction Completion Date')
    financing_type = fields.Selection([
        ('na', 'NA'),
        ('bank', 'Bank'),
        ('pagibig', 'Pag-Ibig'),
        ('cash', 'Cash')
    ], string='Financing')

    state = fields.Selection([
        ('open', 'Available'),
        ('reservation', 'For Reservation'),
        ('reserved', 'Reservation Stage'),
        ('booked', 'Contracting Stage'),
        ('contracted', 'Loan Release Stage'),
        ('proceed', 'Turnover Stage'),
        ('accept', 'Accepted'),
    ], string='Status', default='open', tracking=True)

    customer = fields.Many2one('res.partner', string='Customer')

    last_dp_date = fields.Date(string='Last DP Date')
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

    propclass_id = fields.Many2one(
        'ibas_realestate.property_class', string='Type')
    floor_area = fields.Float(string='Floor Area (sqm)')
    lot_area = fields.Float(string='Lot Area (sqm)')

    reservation_line_ids = fields.One2many(
        'ibas_realestate.requirement_reservation_line', 'product_id', string='Reservation')
    booked_sale_line_ids = fields.One2many(
        'ibas_realestate.requirement_booked_sale_line', 'product_id', string='Booked Sale')
    contracted_sale_line_ids = fields.One2many(
        'ibas_realestate.requirement_contracted_sale_line', 'product_id', string='Contracted Sale')

    loan_proceeds_line_ids = fields.One2many(
        'ibas_realestate.requirement_loan_proceeds_line', 'product_id', string='Loan Proceeds')

    price_history_line_ids = fields.One2many(
        'ibas_realestate.price_history_line', 'product_id', string='Price History')

    proplot_id = fields.Many2one(
        'ibas_realestate.property_lot', string='Lot Class')

    on_hold = fields.Boolean('Tech Hold')

    reservation_date = fields.Date(
        string='Date Reserved', compute='_compute_reservation_date', store=True)

    finishing_id = fields.Many2one(
        'ibas_realestate.property_finishing', string='Finishing')
    price_history_current_date = fields.Datetime(
        'Price History Current Date', default=fields.Datetime.now())

    sale_order_id = fields.One2many(
        'sale.order', 'unit_id', string='Sale Order')

    so_selling_price = fields.Float(string='SO Selling Price')

    list_price = fields.Float(
        'Selling Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")

    current_sale_order_id = fields.Many2one('sale.order', string='Sales Order')

    @api.depends('sale_order_id.date_order')
    def _compute_reservation_date(self):
        # sale_order = self.env['sale.order'].search(
        #    [('unit_id', '=', self.id), ('state', '=', 'sale')], limit=1)
        for rec in self:
            sale_order = self.env['sale.order'].search(
                [('unit_id', '=', rec.id), ('state', '=', 'sale')], limit=1)
            if sale_order:
                reserve_date = sale_order[0].date_order + \
                               relativedelta(hours=8)
                rec.reservation_date = reserve_date
            else:
                rec.reservation_date = False

    @api.constrains('name')
    def _check_names(self):
        name = self.env['product.product'].search(
            [('name', '=', self.name)])
        if name:
            for n in name:
                if n.id != self.id:
                    raise ValidationError("Duplicate Record")

    def unlink(self):
        for rec in self:
            if rec.name:
                raise UserError(_('You cannot delete record.'))
            return super(PropertiesProjectProperty, self).unlink()

    def tech_hold(self):
        self.on_hold = True

    def release_hold(self):
        self.on_hold = False

    def acceptance(self):
        if self.loan_proceeds_line_ids:
            for line in self.loan_proceeds_line_ids:
                if line.complied == True:
                    self.state = 'accept'
                else:
                    raise ValidationError(
                        'Not all Loan Proceeds Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Loan proceeds requirements in the list')

        sale_obj = self.env['sale.order']
        sale_order = sale_obj.search(
            [('unit_id', '=', self.id), ('state', '=', 'sale')])

        if sale_order:
            for sale in sale_order:
                sale.state = 'done'

    def loan_proceeds(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'proceeds')])
        client_lines = []
        if self.state == 'contracted':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.contracted_sale_line_ids:
            for line in self.contracted_sale_line_ids:
                if line.complied == True:
                    self.state = 'proceed'
                else:
                    raise ValidationError(
                        'Not all Contracted Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Contracted Sale requirements in the list')

        if len(client_lines) > 0:
            loan_proceeds_lines = []
            for client in client_lines:
                if not self.loan_proceeds_line_ids:
                    loan_proceeds_lines.append((0, 0, client))
            self.update({'loan_proceeds_line_ids': loan_proceeds_lines})
        # else:
        #    raise UserError('There are no client requirements')

    def get_requirements(self):
        for rec in self:
            if rec.state == 'reserved':
                self.update({
                    'reservation_line_ids': [(5, 0, 0)]
                })

                def_reqts = self.env['ibas_realestate.client_requirement'].search(
                    [('default_requirement', '=', True), ('stage', '=', 'reservation')])
                if def_reqts:
                    for target_list in def_reqts:
                        self.update({
                            'reservation_line_ids': [(0, 0, {
                                'requirement': target_list.id,
                            })],
                        })
                else:
                    raise ValidationError(
                        'There are no Reservation Requirements Created.')

    def booked_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'booked')])
        client_lines = []
        if self.state == 'reserved':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.reservation_line_ids:
            for line in self.reservation_line_ids:
                if line.complied == True:
                    self.state = 'booked'
                else:
                    raise ValidationError(
                        'Not all Reservation Sale Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Reservation Sale requirements in the list')

        if len(client_lines) > 0:
            booked_lines = []
            for client in client_lines:
                if not self.booked_sale_line_ids:
                    booked_lines.append((0, 0, client))
            self.update({'booked_sale_line_ids': booked_lines})
        # else:
        #    raise UserError('There are no client requirements')

    def contracted_sale(self):
        client_reqs = self.env['ibas_realestate.client_requirement'].search(
            [('default_requirement', '=', True), ('stage', '=', 'contracted')])
        client_lines = []
        if self.state == 'booked':
            for req in client_reqs:
                client_line = {
                    'requirement': req.id
                }
                client_lines.append(client_line)
        if self.booked_sale_line_ids:
            for line in self.booked_sale_line_ids:
                if line.complied == True:
                    self.state = 'contracted'
                else:
                    raise ValidationError(
                        'Not all Booked Sale Requirements are submitted. Please upload submitted files before confirming.')
        else:
            raise ValidationError(
                'There are no Booked Sale requirements in the list')

        if len(client_lines) > 0:
            contracted_lines = []
            for client in client_lines:
                if not self.contracted_sale_line_ids:
                    contracted_lines.append((0, 0, client))
            self.update({'contracted_sale_line_ids': contracted_lines})
        # else:
        #    raise UserError('There are no client requirements')

    # back to

    def back_to_reservation(self):
        for rec in self:
            rec.state = 'reserved'

    def back_to_booked(self):
        for rec in self:
            rec.state = 'booked'

    def back_to_contracted(self):
        for rec in self:
            rec.state = 'contracted'

    ####

    def open_view_form(self):
        return {
            'name': 'Property Form',  # Lable
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('ibas_realestate.ire_property_view_form').id,
            'res_model': 'product.product',  # your model
            'res_id': self.id
        }

    @api.model_create_multi
    def create(self, vals):
        res = super(PropertiesProjectProperty, self).create(vals)
        if res:
            # Add Price History
            price_history_line_model = self.env['ibas_realestate.price_history_line']

            res_create = price_history_line_model.create({
                'product_id': res.id,
                'effective_date': res.price_history_current_date,
                'selling_price': vals['list_price']
            })
        return res

    def write(self, vals):
        _logger.info(vals)

        for rec in self:
            remove_list_price = False
            if 'list_price' in vals:
                if rec.state != 'open':
                    remove_list_price = True
                price_history_line_model = self.env['ibas_realestate.price_history_line']

                # current_date = rec.price_history_current_date if 'price_history_current_date' in vals else fields.Datetime.now()
                # raise Warning(current_date)

                validate_price = price_history_line_model.search(
                    [('product_id', '=', rec.id)], order="id asc", limit=1)
                if validate_price:
                    if vals['list_price'] < validate_price.selling_price:
                        raise ValidationError(
                            "Selling Price is lower than the Original Price")

                list_price = vals['list_price']

                if remove_list_price:
                    vals.pop('list_price')

                if 'not_allow' in vals:
                    if vals['not_allow'] == True:
                        vals.pop('not_allow')
                        continue

                res_create = price_history_line_model.create({
                    'product_id': rec.id,
                    # 'effective_date': rec.price_history_current_date,
                    'effective_date': vals[
                        'price_history_current_date'] if 'price_history_current_date' in vals else fields.Datetime.now(),
                    'selling_price': list_price
                })

        res = super(PropertiesProjectProperty, self).write(vals)
        return res

    def updatePrice(self, allow_addhistory=True):
        for rec in self:
            # raise Warning(fields.Datetime.now())
            price_history_line_model = self.env['ibas_realestate.price_history_line'].search(
                [('product_id', '=', rec.id),
                 ('effective_date', '>=', fields.Datetime.now())],
                order="effective_date desc",
                limit=1)

            update_vals = {
                'list_price': price_history_line_model.selling_price,
                'price_history_current_date': price_history_line_model.effective_date, }

            if not allow_addhistory:
                update_vals['not_allow'] = True

            # CHeck First if there's a latest Price base on Date Now
            # If Not check the Latest
            if not price_history_line_model:
                price_history_line_model = self.env['ibas_realestate.price_history_line'].search(
                    [('product_id', '=', rec.id)], order="effective_date desc", limit=1)

            if price_history_line_model:
                update_vals['list_price'] = price_history_line_model.selling_price
                update_vals['price_history_current_date'] = fields.Datetime.now()
                rec.write(update_vals)


# MENU Model


class IBASPropModel(models.Model):
    _name = 'ibas_realestate.propertymodel'
    _description = 'Property Model'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('ibas_realestate.project', string='Project')


# MENU Client Requirements


class IBASRequirementModel(models.Model):
    _name = 'ibas_realestate.client_requirement'
    _description = 'Client Requirements'

    name = fields.Char(string='Name', required=True)
    default_requirement = fields.Boolean(string='Default')
    stage = fields.Selection([('reservation', 'Reservation Stage'),
                              ('booked', 'Contracting Stage'), ('contracted', 'Loan Release Stage'),
                              ('proceeds', 'Turnover Stage')], string="Stage")


# reservation


class IBASPropertyRequirementReservationLine(models.Model):
    _name = 'ibas_realestate.requirement_reservation_line'
    _description = 'Requirement Reservation Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Reservation', domain=[('stage', '=', 'reservation')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')
    sale_id = fields.Many2one('sale.order', string='Sales Order')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.update({
                    'complied': True,
                    'compliance_date': fields.Date.today(),
                })
            else:
                rec.complied = False

    def preview_attachment(self):
        data_file = None
        res_id = self.id
        model = self._name
        res_field = 'requirement_file'
        size = self.requirement_file
        if res_id and model and res_field and size:
            # Using query as unable to find the data
            query = """select id from ir_attachment 
                where res_model=%s and 
                res_id=%s and 
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    data_file = {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if data_file.get('type') in ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/svg']:
            return {
                'type': 'ir.actions.act_url',
                'url': '%s/ibas/preview_attachment?attachment_id=%s' % (base_url, attachment_ids[0]),
                'target': 'new',
            }
        else:
            return {
                'target': 'new',
                'name': 'testing',
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%d/%s?download=false' % (self._name, self.id, 'requirement_file')
            }


class IBASPropertyRequirementBookedSaleLine(models.Model):
    _name = 'ibas_realestate.requirement_booked_sale_line'
    _description = 'Requirement Booked Sale Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Booked Sale', domain=[('stage', '=', 'booked')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')
    sale_id = fields.Many2one('sale.order', string='Sales Order')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.update({
                    'complied': True,
                    'compliance_date': fields.Date.today(),
                })
            else:
                rec.complied = False

    def preview_attachment(self):
        data_file = None
        res_id = self.id
        model = self._name
        res_field = 'requirement_file'
        size = self.requirement_file
        if res_id and model and res_field and size:
            # Using query as unable to find the data
            query = """select id from ir_attachment 
                where res_model=%s and 
                res_id=%s and 
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    data_file = {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if data_file.get('type') in ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/svg']:
            return {
                'type': 'ir.actions.act_url',
                'url': '%s/ibas/preview_attachment?attachment_id=%s' % (base_url, attachment_ids[0]),
                'target': 'new',
            }
        else:
            return {
                'target': 'new',
                'name': 'testing',
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%d/%s?download=false' % (self._name, self.id, 'requirement_file')
            }


# contracted sale


class IBASPropertyRequirementContractedSaleLine(models.Model):
    _name = 'ibas_realestate.requirement_contracted_sale_line'
    _description = 'Requirement Contracted Sale Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Contracted Sale', domain=[('stage', '=', 'contracted')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')
    sale_id = fields.Many2one('sale.order', string='Sales Order')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.update({
                    'complied': True,
                    'compliance_date': fields.Date.today(),
                })
            else:
                rec.complied = False

    def preview_attachment(self):
        data_file = None
        res_id = self.id
        model = self._name
        res_field = 'requirement_file'
        size = self.requirement_file
        if res_id and model and res_field and size:
            # Using query as unable to find the data
            query = """select id from ir_attachment 
                where res_model=%s and 
                res_id=%s and 
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    data_file = {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if data_file.get('type') in ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/svg']:
            return {
                'type': 'ir.actions.act_url',
                'url': '%s/ibas/preview_attachment?attachment_id=%s' % (base_url, attachment_ids[0]),
                'target': 'new',
            }
        else:
            return {
                'target': 'new',
                'name': 'testing',
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%d/%s?download=false' % (self._name, self.id, 'requirement_file')
            }


class IBASPropertyRequirementLoanProceedsLine(models.Model):
    _name = 'ibas_realestate.requirement_loan_proceeds_line'
    _description = 'Requirement Loan Proceeds Line'

    parent_id = fields.Many2one('res.partner', string="customer")
    product_id = fields.Many2one('product.product', string='Property')
    requirement = fields.Many2one(
        'ibas_realestate.client_requirement', string='Loan Proceeds', domain=[('stage', '=', 'proceed')])
    compliance_date = fields.Date(string='Date Complied')
    requirement_file = fields.Binary(string='File Attachment')
    complied = fields.Boolean(compute='_compute_complied', string='Complied')
    sale_id = fields.Many2one('sale.order', string='Sales Order')

    @api.depends('requirement_file')
    def _compute_complied(self):
        for rec in self:
            if rec.requirement_file:
                rec.update({
                    'complied': True,
                    'compliance_date': fields.Date.today(),
                })
            else:
                rec.complied = False

    def preview_attachment(self):
        data_file = None
        res_id = self.id
        model = self._name
        res_field = 'requirement_file'
        size = self.requirement_file
        if res_id and model and res_field and size:
            # Using query as unable to find the data
            query = """select id from ir_attachment 
                where res_model=%s and 
                res_id=%s and 
                res_field=%s"""
            request.env.cr.execute(query, (model, res_id, res_field,))
            attachment_ids = request.env.cr.fetchall()
            if attachment_ids:
                attachment_ids = [t[0] for t in attachment_ids]
                datas = request.env['ir.attachment'].sudo().browse(attachment_ids)
                if datas and len(datas) == 1:
                    data_file = {
                        'name': datas.name or datas.dispay_name,
                        'id': datas.id,
                        'type': datas.mimetype,
                    }
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if data_file.get('type') in ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/svg']:
            return {
                'type': 'ir.actions.act_url',
                'url': '%s/ibas/preview_attachment?attachment_id=%s' % (base_url, attachment_ids[0]),
                'target': 'new',
            }
        else:
            return {
                'target': 'new',
                'name': 'testing',
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s/%d/%s?download=false' % (self._name, self.id, 'requirement_file')
            }


# Price History


class IBASPropertyPriceHistoryLine(models.Model):
    _name = 'ibas_realestate.price_history_line'
    _description = 'Price History'
    _order = "effective_date asc"

    product_id = fields.Many2one('product.product', string='Property')
    effective_date = fields.Datetime(string='Effective Date')
    selling_price = fields.Float(string='Sale Price')
    pre_selling_price = fields.Float(string='Pre Selling Price')
    user_id = fields.Many2one('res.users', string='Update By:',
                              required=True, default=lambda self: self.env.uid)

    @api.model_create_multi
    def create(self, vals):
        res = super(IBASPropertyPriceHistoryLine, self).create(vals)
        if res:
            res.product_id.updatePrice(allow_addhistory=False)
        return res


# MENU  Type


class PropertyClass(models.Model):
    _name = 'ibas_realestate.property_class'
    _description = 'Property Class'

    name = fields.Char(string='Class', required=True)
    _sql_constraints = [
        ('unique_properties_name', 'UNIQUE(name)',
         'You can not have two properties')
    ]


# MENU  Type


class PropertyFinishing(models.Model):
    _name = 'ibas_realestate.property_finishing'
    _description = 'Property Finishing'

    name = fields.Char(string='Name', required=True)


class LotClass(models.Model):
    _name = 'ibas_realestate.property_lot'
    _description = 'Property Lot Class'

    name = fields.Char(string='Lot Class', required=True)

# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class ApproveAccountBill(models.TransientModel):
	_name = "approve.account.bill"
	_description = "Approve Account Bill"

	def approve_bill(self):
		context = dict(self._context or {})
		moves = self.env['account.move'].browse(context.get('active_ids'))

		for move in moves:
			if self.user_has_groups('ibas_account.group_account_finance_head') and move.state == 'submitted':
				move.write({'state': 'finance_head'})
			elif self.user_has_groups('ibas_account.group_account_coo') and move.state == 'finance_head':
				move.write({'state': 'coo'})
			elif self.user_has_groups('ibas_account.group_account_ceo') and move.state == 'coo':
				move.write({'state': 'ceo'})

		# if self.user_has_groups('ibas_account.group_account_finance_head'):
		# 	move_to_approve = moves.filtered(lambda m: m.state == 'submitted').sorted(lambda m: (m.date, m.ref, m.id))
		# 	# if not move_to_approve:
		# 	# 	raise UserError(_('There are no bills for finance head approval.'))
		# 	move_to_approve.write({'state': 'finance_head'})

		# if self.user_has_groups('ibas_account.group_account_coo'):
		# 	move_to_approve = moves.filtered(lambda m: m.state == 'finance_head').sorted(lambda m: (m.date, m.ref, m.id))
		# 	# if not move_to_approve:
		# 	# 	raise UserError(_('There are no bills for COO appoval.'))
		# 	move_to_approve.write({'state': 'coo'})

		# if self.user_has_groups('ibas_account.group_account_ceo'):
		# 	move_to_approve = moves.filtered(lambda m: m.state == 'coo').sorted(lambda m: (m.date, m.ref, m.id))
		# 	# if not move_to_approve:
		# 	# 	raise UserError(_('There are no bills for CEO appoval.'))
		# 	move_to_approve.write({'state': 'ceo'})

		return {'type': 'ir.actions.act_window_close'}

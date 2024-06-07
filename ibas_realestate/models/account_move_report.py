from odoo import models, fields, api

class AccountMoveReport(models.AbstractModel):
    _name = 'report.ibas_realestate.report_journal_entry'
    _description = 'Journal Entry Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'proforma': self.env.context.get('proforma', False),
            'create_date': fields.Datetime.now,
        }

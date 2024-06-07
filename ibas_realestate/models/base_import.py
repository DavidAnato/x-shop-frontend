from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class InheritImport(models.TransientModel):
    _inherit = 'base_import.import'

    def do(self, fields, columns, options, dryrun=False):
    	res_import = super(InheritImport, self).do(fields, columns,options, dryrun)
    	if self.res_model == 'product.product':
    		_logger.info(fields)
    		_logger.info(columns)
    	_logger.info(res_import)
    	return res_import
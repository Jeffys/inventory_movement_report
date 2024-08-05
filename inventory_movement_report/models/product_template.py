from odoo import api, fields, models, tools
from datetime import date
from odoo.http import request
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_open_stock_history(self):
        dt_today = date.today()
        first_of_the_month = dt_today.replace(day=1)
        date_debut = first_of_the_month - relativedelta(months=12)
        list_stock_history_obj = self.env['stock.history.view'].search([('product_template_id', '=', self.id),('date', '>=', date_debut)])
        list_stock_history = list_stock_history_obj.ids

        _logger.debug("#################### show_pivot_matos 3")

        name_form = "Stocks Histories"
        return {
            'name': name_form,
            'res_model': 'stock.history.view',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph,pivot,tree',
            'domain': [('id', 'in', list_stock_history),('product_template_id', '=', self.id)],
            'target': 'current',
        }

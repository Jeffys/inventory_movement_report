from odoo import api, fields, models, tools
from datetime import date
from odoo.http import request
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class stock_history_view(models.Model):
    _name = 'stock.history.view'
    _auto = False

    date = fields.Date('Date')
    income = fields.Float(string='Input', digits=(8, 6))
    outcome = fields.Float(string='Output', digits=(8, 6))
    qty = fields.Float(string='Stock Quantity uom', digits=(8, 6))

    product_template_id = fields.Many2one('product.template', string="Product", readonly=True)

    uom_id = fields.Many2one('uom.uom')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    categ_id = fields.Many2one('product.category', string="Category", readonly=True)

    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'stock_history_view')
        self._cr.execute(""" CREATE VIEW stock_history_view AS (
                    WITH income_outcome_cte AS (
                        SELECT
                            sm.product_id,
                            sml.date,
                            CASE WHEN sm.location_dest_id = 8 THEN sml.qty_done ELSE 0 END AS income,
                            CASE WHEN sm.location_id = 8 THEN sml.qty_done ELSE 0 END AS outcome
                        FROM stock_move sm
                        join (select move_id, sum(qty_done) as qty_done, min(date) as date from stock_move_line sml
                            group by move_id) sml on sml.move_id = sm.id
                        WHERE sm.state = 'done'
                    ),

                    income_outcome_cte_final as (
                        select	product_id,
                                date_trunc('MONTH',(CURRENT_DATE - INTERVAL '1.1 year'))::DATE as date,
                                sum(income) as income,
                                sum(outcome) as outcome
                        FROM income_outcome_cte
                        WHERE date <= date_trunc('MONTH',(CURRENT_DATE - INTERVAL '1.1 year'))::DATE
                        group by product_id
                        
                        union all

                        select	*
                        FROM income_outcome_cte
                        WHERE date > date_trunc('MONTH',(CURRENT_DATE - INTERVAL '1.1 year'))::DATE
                    ),

                    date_series as (
                        SELECT (generate_series(
                            date_trunc('MONTH',(CURRENT_DATE - INTERVAL '1.1 year'))::DATE,
                            (CURRENT_DATE + INTERVAL '1 month')::DATE,
                            '1 month'::INTERVAL
                            )::DATE - INTERVAL '1 day')::DATE AS date
                    ),

                    stock_history as (
                    SELECT
                        p.product_id,
                        g.date,
                        SUM(COALESCE(i.income, 0)) AS income,
                        SUM(COALESCE(i.outcome, 0)) AS outcome
                    FROM date_series g
                    CROSS JOIN (SELECT pp.id as product_id FROM product_product pp
                        join product_template pt on pp.product_tmpl_id = pt.id 
                        where pt.active is true) p
                    LEFT JOIN income_outcome_cte_final i ON to_char(g.date, 'YYYY-MM') = to_char(i.date, 'YYYY-MM') AND p.product_id = i.product_id
                    GROUP BY p.product_id, g.date
                    ORDER BY p.product_id, g.date
                    ),

                    supplier as (
                        select distinct product_tmpl_id, partner_id from product_supplierinfo ps
                        where product_tmpl_id is not null
                    )

                    select 
                        concat(pt.id::text, to_char(date, 'YYYYMMDD')) as id,
                        pt.id as product_template_id,
                        date,
                        income,
                        outcome,
                        round(SUM(income - outcome) OVER (PARTITION BY product_id ORDER BY date), 3) AS qty,
                        pt.uom_id,
                        pt.categ_id,
                        s.partner_id as supplier_id
                    from stock_history sh
                    join product_product pp on pp.id = sh.product_id
                    join product_template pt on pp.product_tmpl_id = pt.id
                    left join supplier s on s.product_tmpl_id = pt.id
                    )""")

    def show_pivot_matos(self):

        dt_today = date.today()
        first_of_the_month = dt_today.replace(day=1)
        date_debut = first_of_the_month - relativedelta(months=12)
        list_stock_history_obj = self.env['stock.history.view'].search([('date', '>=', date_debut)])
        list_stock_history = list_stock_history_obj.ids

        _logger.debug("#################### show_pivot_matos 3")

        name_form = "Stocks histories "
        return {
            'name': name_form,
            'res_model': 'stock.history.view',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'pivot,tree',
            'domain': [('id', 'in', list_stock_history)],
            'context': "{'search_default_groupby_supplier':1}",
            'target': 'current',
        }
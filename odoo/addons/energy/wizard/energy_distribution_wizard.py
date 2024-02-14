# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

cached_property = {
    "contract": [],
    "d_order": [],
    "d_order_line": [],
}


class EnergyDistributionWizard(models.TransientModel):
    _name = "energy.distribution.wizard"
    _description = 'Energy Distribution'
    delivery_point_id = fields.Many2one('border', string='Contract Delivery Point')
    power_date = fields.Date(string='Power Date', required=True)
    position = fields.Selection([
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ], string='Position', required=True,default='buy')    
    other_borders = fields.Many2many('border', string='Other Borders')
    loadshape_details_ids_12 = fields.Many2many('loadshape_details', relation='wizard_loadshape_details_12_rel')
    temp_contract = fields.Many2one('contract')
    loadshape_details_ids_24 = fields.Many2many('loadshape_details',relation='wizard_loadshape_details_24_rel')

    @api.onchange('other_borders')
    def load_data(self):
        power_date = self.power_date
        if not power_date or not self.delivery_point_id or not self.other_borders :
            self.loadshape_details_ids_12 = []
            return
        
        contract_position = self.env.context.get('contract_position')
        temp_contract = self.env["contract"].create({
                    "name": "temp" + str(power_date),
                    "start_date": power_date,
                    "end_date": power_date,
                    "delivery_point_id": self.delivery_point_id.id,
                    "position": contract_position,
                    'status': 'executing',
                    'is_transit': True,
                    'type': 'efet',
                    'product': 'energy',
                    'power': 0,
                    'powerUnit': 'mwh',
                    'timeUnit': '60',
                    'total_contract_power': 0,
                    'price': 0,
                    'total_contract_value': 0,
                    'vat': False,
                    'total_contract_value_with_vat': 0,
                    'risk': 'low',
                    'cai_code': 'cai_code',
                    'profile_id': 1,
                    'period_id': 1
            })

        contract_in_range = self.env["contract"].search([
            ("is_transit", "=", False),
            ("position", "=", contract_position),
            ("delivery_point_id", "=", self.delivery_point_id.id),
            ("start_date", "<=", power_date),
        ])

        total_power_hour = 0

        for i in range(24):
            total_power_hour = 0
            for contract in contract_in_range:
                for  line in contract.loadshape_details_ids:
                    if line.powerdate == power_date and line.powerhour == (i+1):
                        total_power_hour = total_power_hour + line.power
                
            self.env["loadshape_details"].create({
                            'contract_id': temp_contract.id,
                            'powerdate': power_date,
                            'powerhour': i+1,
                            'powerprice': temp_contract.price,
                            'powerunit': temp_contract.powerUnit,
                            'powerfinalprice': 0,
                            'powerfinal': 0,
                            'power': total_power_hour,
                            'delivery_point_id': self.delivery_point_id.id,
                        })
               
        
        for border in self.other_borders:
            for i in range(24):
              self.env["loadshape_details"].create({
                            'contract_id': temp_contract.id,
                            'powerdate': power_date,
                            'powerhour': i+1,
                            'powerprice': temp_contract.price,
                            'powerunit': temp_contract.powerUnit,
                            'powerfinalprice': 0,
                            'powerfinal': 0,
                            'power': 0,
                            'delivery_point_id':  border.id,
                        })

        self.loadshape_details_ids_12 = temp_contract.loadshape_details_ids.filtered(lambda l: l.powerhour <= 12).mapped('id')

        self.loadshape_details_ids_24 = temp_contract.loadshape_details_ids.filtered(lambda l: l.powerhour > 12).mapped('id')
        self.temp_contract = temp_contract.id

    def _calc_totals(self):
        total_power = 0
        for line in self.loadshape_details_ids_12:
            total_power = total_power + line.power
        return total_power

    def action_distribute(self):
        self.env['contract'].search([('id', '=', self.temp_contract.id)]).write({'status': 'executed'})
        return {'type': 'ir.actions.act_window_close'}


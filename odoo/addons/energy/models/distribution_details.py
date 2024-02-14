from odoo import api, models, fields


class DistributionOrder(models.Model):
    _name = "distribution.order"
    _description = "Distribution"

    name = fields.Char(string='Name', required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('distribution.order'))
    position = fields.Selection([
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ], 'Position', required=True,default='buy')    
    delivery_point_id = fields.Many2one('border',
                                        string='Delivery Point', store=True)
    power_date = fields.Date(string='Power Date', required=True)

    distributed_power = fields.Float(string='Distributed Power' )
    total_power = fields.Float(string='Actual Power' )
    distribution_line_ids = fields.One2many('distribution.order.line', 'distribution_id', string='Distribution Lines')

    # def _compute_power_balance(self):
    #     for record in self:
    #         total_power = 0.0
    #         # get all active contracts for this border to compute total power available
    #         contracts = self.env["contract"].search([
    #             ("delivery_point_id", "=", record.delivery_point_id.id),
    #             ("status", "=", "executing"),
    #             ("position", "=", record.position)
    #         ])
    #         if contracts:
    #             total_power = sum(contracts.loadshape_details_ids.filtered(
    #                 lambda l: l.powerdate == record.power_date and l.powerhour == record.power_hour).mapped("power"))
    #         record.total_power = total_power
    #         record.distributed_power = sum(record.distribution_line_ids.mapped("power"))
    #         record.actual_power = record.total_power - record.distributed_power


class DistributionOrderLine(models.Model):
    _name = "distribution.order.line"
    _description = "Distribution Line"
    _order = 'distribution_id, power_date, power_hour'
    # _rec_names_search = ['contract_id.name', 'distribution_id.name']

    name = fields.Text(string='Description', compute='_compute_name', store=True)
    #contract_id = fields.Many2one('contract', related="distribution_id.contract_id", string='Contract')
    delivery_point_id = fields.Many2one('border',
                                        string='Delivery Point', store=True)
    distribution_id = fields.Many2one('distribution.order', string='Distribution', ondelete='cascade',
                                      index=True, copy=False)
    power_date = fields.Date(string='Power Date')
    power_hour = fields.Integer(string='Power Hour')
    total_power = fields.Float(string='Total Power')

    @api.depends('power_date', 'power_hour')
    def _compute_name(self):
        for line in self:
            name = False
            if line.distribution_id:
                name = str(line.distribution_id.id) + " - " + str(line.id)
            line.name = name

    # def _compute_power_balance_line(self):
    #     for record in self:
    #         total_power = 0.0
    #         # get all active contracts for this border to compute total power available
    #         contracts = self.env["contract"].search([
    #             ("delivery_point_id", "=", record.distribution_id.delivery_point_id.id),
    #             ("status", "=", "executing"),
    #             ("position", "=", record.position)
    #         ])
    #         if contracts:
    #             total_power = sum(contracts.loadshape_details_ids.filtered(
    #                 lambda l: l.powerdate == record.power_date and l.powerhour == record.power_hour).mapped("total_power"))

    #         record.total_power = total_power
    #         #record.distributed_power = sum(record.distribution_line_ids.mapped("total_power"))

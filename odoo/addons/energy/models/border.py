from odoo import models, fields


class Border(models.Model):
    _name = "border"
    _description = "Description of the Border model"

    name = fields.Char(string="Name", required=True)
    first_area = fields.Many2one('area', string='First Area', required=True)
    second_area = fields.Many2one('area', string='Second Area', required=True)


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime
import base64,re

class QuickMoveLotWizard(models.TransientModel):
        _name = 'quick.move.lot.wizard'
        _description = 'quick.move.lot.wizard'

        location_id = fields.Many2one('stock.location',string='Ubicacion destino',domain="[('usage','=','internal')]")

        @api.multi
        def action_confirm(self):
		if not self.env.context['active_ids']:
			raise ValidationError('Error inesperado - no active_ids')
                quant_ids = self.env.context['active_ids']
		quants = []
                for quant_id in quant_ids:
                        quant = self.env['stock.quant'].browse(quant_id)
                        if quant.lot_id.id:
                        	quants.append(quant)
		if not quants:
			raise ValidationError('Error inesperado - no hay quants')
		src_locations = []
		for quant in quants:
			if quant.location_id.id not in src_locations:
				src_locations.append(quant.location_id.id)
		if len(src_locations) > 1:
			raise ValidationError('Debe elegir nros de serie pertenecientes a una sola ubicacion')
		for quant in quants:
			if quant.lot_id:
				str_name = 'QUICK ' + quant.product_id.display_name + ' ' + quant.lot_id.name
			else:
				str_name = 'QUICK ' + quant.product_id.display_name
	                move_id = self.env['stock.move'].create({
				'name': str_name,
                	        'date': str(date.today()),
                        	'date_expected': str(date.today()),
	                        'product_id': quant.product_id.id,
        	                'product_uom': quant.product_id.uom_id.id,
                	        'product_uom_qty': quant.qty,
                        	'location_id': quant.location_id.id,
	                        'location_dest_id': self.location_id.id,
                        	'origin': str_name,
        	                })
                        move_id.action_confirm()
                        if quant.product_id.tracking == 'none':
                                move_id.action_assign()
                                move_id.action_done()
                                #quants = self.env['stock.quant']
                                #quants |= move_raw.quant_ids.filtered(lambda x: x.qty > 0.0)
                                #move_id.quant_ids.sudo().write({'consumed_quant_ids': [(6, 0, [x.id for x in quants])]})
                        else:
                                move_id.action_assign()
                                move_id.action_done()
                                self.env['stock.quant'].quants_move([(quant,1)], move_id, move_id.location_dest_id, lot_id = quant.lot_id.id)


from odoo import models, fields, api, _


class Web3WalletType(models.Model):
    _name = 'web3.wallet.type'
    _description = "Web3钱包类型"

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码', required=True)


class CurrencyType(models.Model):
    _name = 'web3.currency.type'

    name = fields.Char(string='名称', required=True)


class WalletAddress(models.Model):
    _name = 'web3.wallet.address'
    _order = 'sequence'

    name = fields.Char(string='名称')
    currency_ids = fields.Many2many('web3.currency.type', 'crypto_currency_address_rel',
                                    column1='address_id', column2='currency_id', string="货币", required=True)
    address = fields.Char(string='钱包地址', required=True)
    wallet_id = fields.Many2one('web3.wallet', string="关联钱包", required=True)
    sequence = fields.Integer(string='序号')


class Web3Wallet(models.Model):
    _name = 'web3.wallet'

    name = fields.Char(string='名称', store=True, compute='_compute_name')
    wallet_name = fields.Char(string='钱包名称')
    main_address = fields.Char(string='主要地址', required=True)
    address_ids = fields.One2many('web3.wallet.address', inverse_name='wallet_id', string='地址')
    wallet_type_id = fields.Many2one('web3.wallet.type', required=True, string='钱包种类')
    sequence = fields.Integer(string='Sequence')

    @api.depends('name', 'wallet_type_id.name')
    def _compute_name(self):
        for record in self:
            if not all([record.main_address, record.wallet_type_id]):
                continue
            if len(record.main_address) > 18:
                record.name = f'{record.wallet_type_id.name}/{record.main_address[:6]}******{record.main_address[-6:]}'
            else:
                record.name = f'{record.wallet_type_id.name}/{record.main_address}'



import logging
import base64

from cryptography.fernet import Fernet

from odoo import models, fields, api, tools

# from ..fields_encrypted_patch import apply_encryption_patch

_logger = logging.getLogger(__name__)

ferent_key = tools.config.get('ferent_key') or '0WhfskScQ5xxuZUOx_9oT0I3fc9avYv_o_PARZrJlrc='
cipher = Fernet(ferent_key.encode())


def is_fernet_encrypted(value: str) -> bool:
    try:
        base64.b64decode(value.encode(), validate=True)
        try:
            cipher.decrypt(value.encode())
            return True
        except:
            return False
    except:
        return False




class Web3WalletType(models.Model):
    _name = 'web3.wallet.type'
    _description = "Web3钱包类型"

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码', required=True)


class CurrencyType(models.Model):
    _name = 'web3.currency.type'
    _description = "虚拟币"

    name = fields.Char(string='名称', required=True)


# class WalletAddress(models.Model):
#     _name = 'web3.wallet.address'
#     _order = 'sequence'
#
#     name = fields.Char(string='名称')
#     address = fields.Char(string='钱包地址', required=True)
#     wallet_id = fields.Many2one('web3.wallet', string="关联钱包", required=True)
#     private_key = fields.Text(string="私钥")
#     sequence = fields.Integer(string='序号')
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             if 'private_key' in vals and vals['private_key']:
#                 vals['private_key'] = cipher.encrypt(vals['private_key'].encode()).decode()
#         return super().create(vals_list)
#
#     def write(self, vals):
#         if 'private_key' in vals and vals['private_key']:
#             vals['private_key'] = cipher.encrypt(vals['private_key'].encode()).decode()
#         return super().write(vals)
#
#     def read_private_key(self):
#         self.ensure_one()
#         try:
#             decrypted = cipher.decrypt(self.private_key.encode()).decode()
#         except Exception:
#             decrypted = '[解密失败]'
#         _logger.info('======================= %s' % decrypted)
#         return decrypted


class Web3Wallet(models.Model):
    _name = 'web3.wallet'
    _description = "web3钱包"

    name = fields.Char(string='名称', store=True, compute="_compute_name")
    wallet_name = fields.Char(string='钱包名称', required=True)
    memo = fields.Text(string="助记词")
    private_key = fields.Text(string="私钥")
    main_address = fields.Char(string='钱包地址', required=True)
    # address_ids = fields.One2many('web3.wallet.address', inverse_name='wallet_id', string='地址')
    wallet_type_id = fields.Many2one('web3.wallet.type', required=True, string='钱包种类')
    currency_ids = fields.Many2many('web3.currency.type', 'crypto_currency_wallet_rel',
                                    column1='address_id', column2='currency_id', string="货币", required=False)
    sequence = fields.Integer(string='Sequence')

    # def _register_hook(self):
    #     apply_encryption_patch()

    @api.depends('wallet_name', 'main_address')
    def _compute_name(self):
        for record in self:
            if not all([record.main_address, record.wallet_name]):
                continue
            if len(record.main_address) > 18:
                record.name = f'{record.wallet_name}/{record.main_address[:6]}******{record.main_address[-6:]}'
            else:
                record.name = f'{record.wallet_name}/{record.main_address}'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'private_key' in vals and vals['private_key'] and not is_fernet_encrypted(vals['private_key']):
                vals['private_key'] = cipher.encrypt(vals['private_key'].encode()).decode()
            if 'memo' in vals and vals['memo'] and not is_fernet_encrypted(vals['memo']):
                vals['memo'] = cipher.encrypt(vals['memo'].encode()).decode()
        return super().create(vals_list)

    def write(self, vals):
        if 'private_key' in vals and vals['private_key'] and not is_fernet_encrypted(vals['private_key']):
            vals['private_key'] = cipher.encrypt(vals['private_key'].encode()).decode()
        if 'memo' in vals and vals['memo'] and not is_fernet_encrypted(vals['memo']):
            vals['memo'] = cipher.encrypt(vals['memo'].encode()).decode()
        return super().write(vals)

    def read_private_key(self):
        self.ensure_one()
        if not self.private_key:
            return
        try:
            decrypted = cipher.decrypt(self.private_key.encode()).decode()
        except Exception:
            decrypted = '[解密失败]'
        _logger.info('=======================私钥 %s' % decrypted)
        return decrypted

    def read_memo(self):
        self.ensure_one()
        if not self.memo:
            return
        try:
            decrypted = cipher.decrypt(self.memo.encode()).decode()
        except Exception:
            decrypted = '[解密失败]'
        # _logger.info('=======================助记词 %s' % decrypted)
        return decrypted



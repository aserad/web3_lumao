# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import config
from odoo.exceptions import ValidationError
from cryptography.fernet import Fernet
import base64
import logging

_logger = logging.getLogger(__name__)

# 默认加密密钥（应通过配置传入）
FERNET_KEY = config.get('fernet_key')
if not FERNET_KEY:
    raise EnvironmentError("ferent_key is not set in config file!!!")
fernet = Fernet(FERNET_KEY)


class Base(models.AbstractModel):
    _inherit = 'base'

    def _valid_field_parameter(self, field, name):
        return name in ('encrypted', 'read_auto_decrypted') or super()._valid_field_parameter(field, name)
#
#     def __init__(self, env, ids, prefetch_ids):
#         super().__init__(env, ids, prefetch_ids)
#         for model_name, model in env.items():
#             for field_name, field in model._fields.items():
#                 if getattr(field, 'encrypted', False):
#                     self._wrap_encrypted_field(field_name, field, model)
#
#     def _wrap_encrypted_field(self, field_name, field, model):
#         if getattr(field, 'read_auto_decrypted', False) and not getattr(field, 'encrypted', False):
#             raise ValidationError("Field '%s' has read_auto_decrypted=True but is not encrypted." % field_name)
#
#         def getter(self):
#             val = self[field_name]
#             if val and getattr(field, 'read_auto_decrypted', False):
#                 try:
#                     return fernet.decrypt(val.encode()).decode()
#                 except Exception as e:
#                     _logger.error(f"Decryption failed for field {field_name}: {e}")
#                     return val
#             return val
#
#         def setter(self, value):
#             if getattr(field, 'encrypted', False):
#                 if value is not None:
#                     value = fernet.encrypt(value.encode()).decode()
#             self.__dict__['__cache__'][field_name] = value
#
#         setattr(model, field_name, property(getter, setter))
#
#
# # 示例模型使用
# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#     secure_notes = fields.Text(string="Secure Notes", encrypted=True, read_auto_decrypted=True)

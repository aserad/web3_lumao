# from odoo import fields, models
# from odoo.tools import config
# from cryptography.fernet import Fernet
# import logging
#
# _logger = logging.getLogger(__name__)
#
# # key = Fernet.generate_key().decode()
# FERNET_KEY = config.get("fernet_key")
# if not FERNET_KEY:
#     raise Exception("Missing 'fernet_key' in config")
# cipher = Fernet(FERNET_KEY.encode())
#
#
# _original_valid_field_parameter = models.BaseModel._valid_field_parameter
#
#
# def _patched_valid_field_parameter(self, field, name):
#     if name in ('encrypted', 'read_auto_decrypted'):
#         return True
#     return _original_valid_field_parameter(self, field, name)
#
#
# models.BaseModel._valid_field_parameter = _patched_valid_field_parameter
#
#
# def _setup_attrs_encrypted(self, model, name):
#     # 先执行原有逻辑
#     self._original_setup_attrs(model, name)
#
#     # 注入新属性
#     self.encrypted = self.args.get("encrypted", False)
#     self.read_auto_decrypted = self.args.get("read_auto_decrypted", False)
#
#     if self.read_auto_decrypted and not self.encrypted:
#         raise ValueError(
#             f"Field '{name}' in model '{model._name}' has read_auto_decrypted=True but encrypted=False."
#         )
#
#
# def _convert_to_write_encrypted(self, value, record):
#     value = self._original_convert_to_write(value, record)
#     if self.encrypted and isinstance(value, str):
#         try:
#             return cipher.encrypt(value.encode()).decode()
#         except Exception as e:
#             _logger.warning("Encryption failed: %s", e)
#             return value
#     return value
#
#
# def _convert_to_cache_encrypted(self, value, record, validate=True):
#     value = self._original_convert_to_cache(value, record, validate)
#     if self.read_auto_decrypted and isinstance(value, str):
#         try:
#             return cipher.decrypt(value.encode()).decode()
#         except Exception as e:
#             _logger.warning("Decryption failed: %s", e)
#             return value
#     return value
#
#
# def patch_field(cls):
#     if not hasattr(cls, "_original_setup_attrs"):
#         cls._original_setup_attrs = cls._setup_attrs
#         cls._setup_attrs = _setup_attrs_encrypted
#
#     if not hasattr(cls, "_original_convert_to_write"):
#         cls._original_convert_to_write = cls.convert_to_write
#         cls.convert_to_write = _convert_to_write_encrypted
#
#     if not hasattr(cls, "_original_convert_to_cache"):
#         cls._original_convert_to_cache = cls.convert_to_cache
#         cls.convert_to_cache = _convert_to_cache_encrypted
#
#
# def apply_encryption_patch():
#     patch_field(fields.Char)
#     patch_field(fields.Text)
#     _logger.info("Patched fields.Char and fields.Text to support encrypted/read_auto_decrypted")







# from odoo.fields import _String
# from odoo.tools.misc import unquote, has_list_types, Sentinel, SENTINEL
# import logging
#
# from .fernet_encrypt import encrypt_value, decrypt_value
#
# _logger = logging.getLogger(__name__)
#
# # 保存原始方法
# original_init = _String.__init__
# original_convert_to_column = _String.convert_to_column
# original_convert_to_record = _String.convert_to_record
# original_convert_to_cache = _String.convert_to_cache
#
#
# def patched_init(self, string=SENTINEL, **kwargs):
#     self.encrypted = kwargs.pop('encrypted', False)
#     self.read_auto_decrypted = kwargs.pop('read_auto_decrypted', False)
#     original_init(self, string=string, **kwargs)
#
#
# def patched_convert_to_column(self, value, record, values=None, validate=True):
#     if self.encrypted and value not in [None, False]:
#         try:
#             value = encrypt_value(value)
#         except Exception as e:
#             _logger.warning(f"Encryption failed on field {self.name}: {e}")
#     return original_convert_to_column(self, value, record, values, validate)
#
#
# def patched_convert_to_record(self, value, record):
#     # 如果开启了自动解密（read_auto_decrypted）
#     if self.encrypted and self.read_auto_decrypted and value not in [None, False]:
#         try:
#             value = decrypt_value(value)
#         except Exception as e:
#             _logger.warning(f"Decryption failed on field {self.name}: {e}")
#     return original_convert_to_record(self, value, record)
#
#
# # def convert_to_cache(self, value, record, validate=True):
# #     # 如果开启了自动解密（read_auto_decrypted）
# #     if self.encrypted and self.read_auto_decrypted and value not in [None, False]:
# #         try:
# #             value = decrypt_value(value)
# #         except Exception as e:
# #             _logger.warning(f"Decryption failed on field {self.name}: {e}")
# #     return original_convert_to_cache(self, value, record, validate=validate)
#
#
# # 打补丁
# _String.__init__ = patched_init
# _String.convert_to_column = patched_convert_to_column
# _String.convert_to_record = patched_convert_to_record
#

import traceback
import logging

from cryptography.fernet import Fernet

from odoo.tools import config

_logger = logging.getLogger(__name__)

# 默认加密密钥（应通过配置传入）
FERNET_KEY = config.get('fernet_key')
if not FERNET_KEY:
    raise EnvironmentError("ferent_key is not set in config file!!!")
fernet = Fernet(FERNET_KEY)


def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()


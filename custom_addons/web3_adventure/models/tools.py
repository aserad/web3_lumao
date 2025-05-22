from odoo import fields, api, _, tools, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval

from collections import defaultdict
import json
import math
import re
import time
import datetime
import dateutil
import logging
import inspect
import random
import traceback
import requests
import base64

_logger = logging.getLogger(__name__)


# class NotFindMethodError(except_orm):
#     pass


def wrapper_sudo(self, params):
    for key, model in params.items():
        if isinstance(model, models.BaseModel):
            params[key] = model.sudo()

    return params


def eval_code(self, code, context=None):
    """
    解析python code 并执行，返回执行结果
    :param code: python代码。 type: str
    :param context: 参数
    :return:
    """
    
    eval_context = context or {}
    eval_context = wrapper_sudo(self, eval_context)
    eval_context.update({"__skip_check_context__": True})
    try:
        safe_eval(code, eval_context, mode='exec', nocopy=True)
        return eval_context.get('result', None)
    except Exception as e:
        if isinstance(e, UserError):
            raise e

        traceback.print_exc()
        raise ValidationError(f'"{self.name}"方法执行失败：{e}')

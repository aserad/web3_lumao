import base64
import json
import math
import operator
import random
import re
import datetime
import time
import dateutil
import logging
import requests
import hashlib
import web3
import eth_account
from pytz import timezone
import types

from collections import defaultdict

import odoo
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
from odoo.tools.func import lazy_property
from odoo.tools.safe_eval import (wrap_module, json as safe_json, datetime as safe_datetime,
                                  dateutil as safe_dateutil, time as safe_time, pytz as safe_pytz)
import traceback
from .tools import eval_code
import psycopg2

_logger = logging.getLogger(__name__)

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - user: Odoo Environment User who call the sequence
#  - self: record on which the script is triggered
#  - context: Odoo Environment Context on which the sequence is called
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - ValidationError: ValidationError Exception to use with raise
#  - logger(msg, level="info"): Log information
# To return an result, assign: result = {...}
# result must be a dict type.\n
result = {}\n\n"""


def my_wrap(mod, wrap_attrs):
    # def _get_attr(module_name, depth=1):
    #     res = {}
    #     for attr in dir(module_name):
    #         if attr.startswith('_') or depth > 10:
    #             continue
    #         try:
    #             if isinstance(getattr(module_name, attr), types.ModuleType):
    #                 res.update({attr: _get_attr(getattr(module_name, attr), depth + 1)})
    #             else:
    #                 res.update({attr: None})
    #         except:
    #             pass
    #     return res
    #
    # if mod.__name__ in wrap_attrs:
    #     tmp_attrs = wrap_attrs.get(mod.__name__)
    # else:
    #     tmp_attrs = _get_attr(mod)
    #     wrap_attrs[mod.__name__] = tmp_attrs
    # return wrap_module(mod, tmp_attrs)
    return mod


class ScriptTasks(models.Model):
    _name = 'script.tasks'

    name = fields.Char("名称", required=True)
    description = fields.Char("描述")

    # 执行脚本相关字段
    python_code = fields.Text("脚本代码", default=DEFAULT_PYTHON_CODE)
    tmp_storage = fields.Text("存储信息")
    running_log = fields.Text("运行输出")
    next_execute_time = fields.Datetime("下次执行时间")
    execute_duration = fields.Float("最近一次运行耗时(秒)")
    execute_status = fields.Selection([("running", "运行中"), ("stopped", "停止")],
                                      default="stopped", string="脚本状态")
    cron_id = fields.Many2one("ir.cron")

    # 信息查询相关字段
    search_code = fields.Text("查询代码", default=DEFAULT_PYTHON_CODE)
    search_result = fields.Text("查询结果")

    def unlink(self):
        if self.execute_status == 'running':
            raise ValidationError("不能删除运行中的脚本")  # 启用状态的规则不允许删除
        return super().unlink()

    def get_eval_context(self):
        """
        获取执行python代码的全局变量
        :return:
        """
        # icp = self.env['ir.config_parameter'].sudo()
        # key = 'module_wrap_attrs'
        # module_wrap_attrs = icp.get_param(key) or '{}'
        module_wrap_attrs = {}
        res = {
            'env': self.env,
            'self': self,
            'result': {},
            'logger': _logger,
            'uid': self._uid,
            'user': self.env.user,
            'context': self.env.context or {},
            'ValidationError': ValidationError,

            'time': safe_time,
            'datetime': safe_datetime,
            'dateutil': safe_dateutil,
            'timezone': safe_pytz.timezone,

            'json': safe_json,
            'random': my_wrap(random, module_wrap_attrs),
            'math': my_wrap(math, module_wrap_attrs),
            'operator': my_wrap(operator, module_wrap_attrs),
            'base64': my_wrap(base64, module_wrap_attrs),
            'requests': my_wrap(requests, module_wrap_attrs),
            're': my_wrap(re, module_wrap_attrs),
            'web3': my_wrap(web3, module_wrap_attrs),
            'eth_account': my_wrap(eth_account, module_wrap_attrs),
            'hashlib': my_wrap(hashlib, module_wrap_attrs),
            'getattr': getattr,
            'hasattr': hasattr,
        }
        # module_wrap_attrs = json.dumps(module_wrap_attrs, ensure_ascii=False, indent=2)
        # icp.search([('key', '=', key)]).write({"value": module_wrap_attrs})
        return res

    def execute(self, code=None):
        log_buffer = []

        def log(msg, level="info"):
            if hasattr(_logger, level):
                getattr(_logger, level)(f"[ScriptLog] {str(msg)}")
            else:
                _logger.warning(f"[ScriptLog] ********** 未找到 {level} 级别的日志，使用默认的 info 级别 **********")
                _logger.info(f"[ScriptLog] {str(msg)}")
            log_buffer.append(str(msg))

        if not self.exists():
            return
        now = datetime.datetime.now()
        if self.next_execute_time and (self.next_execute_time - now).total_seconds() > 100:
            _logger.info("[ScriptLog] 未到下次执行时间，跳过。。。")
            return
        context = dict(self.env.context)
        context.update(self.get_eval_context())
        context.update({'logger': log})
        t1 = time.time()
        res = eval_code(
            self,
            self.python_code if code is None else code,
            context=context
        )
        t2 = time.time()
        next_execute_time = res and isinstance(res, dict) and res.get("next_execute_time") or now + datetime.timedelta(hours=1)
        self.next_execute_time = next_execute_time
        self.execute_duration = t2 - t1
        self.write({
            "next_execute_time": next_execute_time,
            "execute_duration": t2 - t1,
            "running_log": '\n'.join(log_buffer)
        })
        return res

    def action_activate_script(self):
        self.ensure_one()
        if not self.cron_id:
            cron = self.env['ir.cron'].sudo().create([{
                'user_id': self.env.ref('base.user_root').id,
                'active': True,
                'interval_type': 'minutes',
                'interval_number': 5,
                'name': self.name,
                'model_id': self.env['ir.model']._get_id(self._name),
                'state': 'code',
                'code': f"env['{self._name}'].browse({self.id}).exists().execute()",
            }])
            self.cron_id = cron.id
        else:
            self.cron_id.sudo().write({"active": True})
        self.execute_status = 'running'

    def action_deactivate_script(self):
        if not self.cron_id:
            return
        self.cron_id.sudo().write({"active": False})
        self.execute_status = 'stopped'

    def action_manual_test(self):
        self.ensure_one()
        self.cron_id.sudo().method_direct_trigger()

    def execute_script_search(self):
        self.ensure_one()
        res = self.execute(self.search_code)
        self.search_result = res



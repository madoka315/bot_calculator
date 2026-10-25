from hoshino import Service
import re

help_str = '四则运算计算器，直接发送四则运算公式即可，如"1+1"、"(1+2)*3"，支持全角与×÷'

sv = Service("四则运算器", help_=help_str)

# 输入归一化：兼容全角数字/运算符与 ×÷
FULLWIDTH_TRANS = str.maketrans('０１２３４５６７８９＋－＊／（）．×÷',
                                '0123456789+-*/().*/')

# 安全约束：eval 只允许接收通过此白名单的表达式，禁止放宽，否则构成注入
# (?!.*\*\*) 禁用次方：防止 9**9**9 这类不可完成的大数运算阻塞事件循环
VALID_PATTERN = re.compile(r'^(?!.*\*\*)[0-9+\-*/(). ]{1,100}$')
OPERATOR = re.compile(r'[+\-*/]')
# 年份开头的完整日期（2026-10-25、2026/10/25）不是算式，不回复
DATE_PATTERN = re.compile(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$')


@sv.on_message()
async def calc_message(bot, ev):
    expr = ev.message.extract_plain_text().strip().translate(FULLWIDTH_TRANS)
    if not VALID_PATTERN.match(expr) or not OPERATOR.search(expr):
        return
    if DATE_PATTERN.match(expr.replace(' ', '')):
        return
    try:
        result = eval(expr, {'__builtins__': {}}, {})
    except Exception:
        return
    await bot.send(ev, f'= {result}')

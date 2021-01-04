from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger

from . import sql_exec

import requests
import sqlite3
import xmltodict
import json
import os.path


# 当用户输入关键字没有输入值时则提示
@on_command('wuping', aliases=('.jita', 'jita'), only_to_me=False)
async def wuping(session: CommandSession):
    chawuping = session.get('chawuping', prompt='你想查询的物品名称是什么？')
    wuping = await get_wuping(chawuping)
    await session.send(wuping, at_sender=True)


#  当用户输入关键字和值时直接运行
@wuping.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['chawuping'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要查询的物品名称不能为空，请重新输入')

    session.state[session.current_key] = stripped_arg


async def get_wuping(name: str) -> str:
    name.replace("'", "").replace('"', '')
    try:
        logger.info("[FSOTech-Jita]Market Bot Search Price for {}".format(name))
        if name == '矿价':
            url = "https://www.ceve-market.org/api/evemon"
            headers = {
                "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            string = response.text
            dic = xmltodict.parse(string, encoding='utf-8')
            json_string = json.dumps(dic, indent=4, ensure_ascii=False)
            json_join = json.loads(json_string)
            minerals = json_join['minerals']['mineral']
            k = ''
            for i in minerals:
                l = ''
                name = i['name']
                price = i['price']
                l = k + '{}\n价格:{}\n'.format(name, price)
                k = l
            return '吉他矿价:\n' + k + '数据来源:ceve-market'

        elif '谷歌' in name:
            return "\n".join(
                ["北府牛痣派", "卖价订单:", "最高:1,000,000,000,000,000", "最低:1,000,000,000,000,000", "收价订单:", "最高:0", "最低:0"])

        elif '牛痣' in name or '牛子' in name:
            return "牛痣无价，请珍惜"

        elif ('谎言之镜' in name) or ('先先' in name):
            return "红烧兔头30一斤 50两斤"

        elif '轩轩' in name:
            return "猪不要钱免费送"

        else:
            d = sql_exec.sql_execute('SELECT typeID FROM nameandid WHERE name = "{}"'.format(name))
            if d == []:
                c = sql_exec.sql_execute('SELECT * FROM nameandid WHERE name LIKE "%{}%" LIMIT 5'.format(name))
                if c == []:
                    return '输入的物品名称不正确/不存在，请重新输入'
                else:
                    k = ''
                    for i in c:
                        l = ''
                        url = "https://www.ceve-market.org/api/market/region/10000002/type/{}.json".format(i[1])
                        headers = {
                            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
                        }
                        response = requests.get(url, headers=headers)
                        string = response.json()

                        string = '🎁🎁' + i[0] + '\n' + json_to_natural(string)

                        l = k + '\n' + string
                        k = l
						
                    return '吉他物价:' + k + '\n' + '数据来源:ceve-market'
            else:
                c = sql_exec.sql_execute('SELECT typeID FROM nameandid WHERE name = "{}"'.format(name))
                id = c[0][0]
                url = "https://www.ceve-market.org/api/market/region/10000002/type/{}.json".format(id)
                headers = {
                    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                string = response.json()
                string = '🎁🎁' + name + '\n' + json_to_natural(string) + '\n' + '数据来源:ceve-market'

                return string
    except Exception as e:
        logger.info("[FSOTech-Jita]Market Bot Error: {}".format(repr(e)))
        string = "市场鸡坏了.jpg 请把以下内容截图给牛痣:\n" + repr(e)
        return string

def json_to_natural(string):
    buydict = string['buy']
    buymax = buydict['max']
    buymin = buydict['min']

    if buymax == 0 and buymin == 0:
        string2 = '❎收价订单:无\n'
    else:
        max = format(buymax, ',')
        min = format(buymin, ',')
        string2 = '⏩收价订单:\n☝最高:{}\n👇最低:{}'.format(max, min)

    selldict = string['sell']
    sellmax = selldict['max']
    sellmin = selldict['min']

    if sellmax == 0 and sellmin == 0:
        string1 = '❎卖价订单:无\n'
    else:
        max = format(sellmax, ',')
        min = format(sellmin, ',')
        string1 = '⏪卖价订单:\n☝最高:{}\n👇最低:{}\n'.format(max, min)

    if buymax == 0 and buymin == 0 and sellmax == 0 and sellmin == 0:
        string1 = '⛔市场无订单'
        string2 = ''

    return string1 + string2



if __name__ == '__main__':
    get_wuping('狂怒')
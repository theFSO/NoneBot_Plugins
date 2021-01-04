from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from nonebot.message import MessageSegment, Message

import json
import requests
import os.path
import linecache
import sys
import math

# 当用户输入关键字没有输入值时则提示
@on_command('idh', aliases=('.idh', 'idh'), only_to_me=False)
async def idh(session: CommandSession):
	id = session.get('id', prompt='请输入要查询的ID')
	result = await get_idh(id)
	await session.send(result, at_sender=True)


#  当用户输入关键字和值时直接运行
@idh.args_parser
async def _(session: CommandSession):
	stripped_arg = session.current_arg_text.strip()

	if session.is_first_run:
		if stripped_arg:
			session.state['id'] = stripped_arg
		return

	if not stripped_arg:
		session.pause('请输入起点 终点（中间用空格链接）(.dist 0MV-4W UNAG-6)')

	session.state[session.current_key] = stripped_arg
	
	
	
async def get_idh(name: str) -> str:
	try:
		logger.info("[FSOTech-ID History]History Search For: {}".format(name))
		url = "https://esi.evepc.163.com/latest/universe/ids/?datasource=serenity&language=zh"
		headers = {
			"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
		}
		data = '["{}"]'.format(name).encode("UTF-8")
		response = requests.post(url, headers=headers,data = data)
		char = json.loads(response.text.replace("'",'"'))
		if char == {}:
			return "未查询到角色 / ESI未响应"
		charID = char['characters'][0]['id']
		
		picurl = "https://image.evepc.163.com/Character/{}_128.jpg".format(str(charID))
		
		
		url = "https://esi.evepc.163.com/latest/characters/{}/corporationhistory/?datasource=serenity".format(str(charID))
		response = requests.get(url, headers = headers)
		history = json.loads(response.text.replace("'",'"'))
		
		result = "查询到 {} 的雇佣记录:\n".format(name)
		
		for i in history:
			cname = get_corp(str(i["corporation_id"]))
			result = result + "{} [加入了] {}\n".format(i["start_date"], cname)
			
		msg = MessageSegment.image(picurl) + (MessageSegment.text(result))
		return msg
		
		
		
	except Exception as e:
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		exp = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
		
		logger.info("[FSOTech-ID History]Distance Calculater Error: {}".format(exp))
		string = "雇佣查询坏了.jpg 请把以下内容截图给牛痣:\n" + exp
		return string


def get_corp(id):
	url = "https://esi.evepc.163.com/latest/corporations/{}/?datasource=serenity".format(id)
	headers = {
		"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
	}
	response = requests.get(url, headers=headers)
	data = json.loads(response.text.replace('true','"true"'))
	return str(data['name'])
		


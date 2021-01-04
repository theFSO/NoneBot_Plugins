from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger

from . import sql_exec

import os.path
import linecache
import sys
import math

# 当用户输入关键字没有输入值时则提示
@on_command('dist', aliases=('.dist', 'dist'), only_to_me=False)
async def dist(session: CommandSession):
	system_name = session.get('system_name', prompt='请输入起点 终点（中间用空格链接）(.dist 0MV-4W UNAG-6)')
	distance = await get_dist(system_name)
	await session.send(distance, at_sender=True)


#  当用户输入关键字和值时直接运行
@dist.args_parser
async def _(session: CommandSession):
	stripped_arg = session.current_arg_text.strip()

	if session.is_first_run:
		if stripped_arg:
			session.state['system_name'] = stripped_arg
		return

	if not stripped_arg:
		session.pause('请输入起点 终点（中间用空格链接）(.dist 0MV-4W UNAG-6)')

	session.state[session.current_key] = stripped_arg
	
	
	
async def get_dist(name: str) -> str:
	try:
		name.replace("'","").replace('"','')
		name = name.upper()
		logger.info("[FSOTech-Dist]Distance Calculater for {}".format(name))
		s_system = name.split(" ")
		if len(s_system) != 2:
			return '请输入起点 终点（中间用空格链接）(.dist 0MV-4W UNAG-6)'

		start_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN = "{}"'.format(s_system[0]))
		if len(start_sys) != 1:
			start_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN LIKE "{}%"'.format(s_system[0]))
		if len(start_sys) != 1:
			start = "%".join(list(s_system[0])) + "%"
			start_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN = "{}"'.format(start))
		
		end_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN = "{}"'.format(s_system[1]))
		if len(end_sys) != 1:
			end_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN LIKE "{}%"'.format(s_system[1]))
		if len(end_sys) != 1:
			end = "%".join(list(s_system[1])) + "%"
			end_sys = sql_exec.sql_execute('select solarSystemID, solarSystemNameCN from systemnameandid where solarSystemNameCN LIKE "{}"'.format(end))
		
		if start_sys == [] or end_sys == []:
			return '星系名都能输错，你还是拿手量吧'
			
		if len(start_sys) + len(end_sys) >= 10:
			return '搜索范围太广了，你还是拿手量吧'
		elif len(start_sys) > 1 or len(end_sys) > 1:
		
			result = '有多个星系:\n'
			if len(start_sys) != 1:
				result = result + "起始星系:\n"
				for i in start_sys:
					result = result + i[1] + "\n"
					
			if len(end_sys) != 1:
				result = result + "目标星系:\n"
				for i in end_sys:
					result = result + i[1] + "\n"
					
			result = result + "请选择星系"
			return result
			
		start_detail = sql_exec.sql_execute('select x, y, z from mapsolarsystems where solarSystemID = {}'.format(start_sys[0][0]))
		end_detail = sql_exec.sql_execute('select x, y, z from mapsolarsystems where solarSystemID = {}'.format(end_sys[0][0]))
		a = (start_detail[0][0]-end_detail[0][0])
		b = (start_detail[0][1]-end_detail[0][1])
		c = (start_detail[0][2]-end_detail[0][2])
		distance_ly = math.sqrt(a*a+b*b+c*c)*1.05702341E-16
		distance_ly = round(distance_ly, 2)
		return "计算结果:\n由 {} 到 {} 的距离为 {} 光年".format(start_sys[0][1],end_sys[0][1],str(distance_ly))
		
		
		
		
	except Exception as e:
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		exp = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
		
		logger.info("[FSOTech-Dist]Distance Calculater Error: {}".format(exp))
		string = "计算器坏了.jpg 请把以下内容截图给牛痣:\n" + exp
		return string

		


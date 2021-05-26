from nonebot import on_command, CommandSession, session
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from nonebot.message import MessageSegment, Message

from . import sql_exec

import json
import requests
import os.path
import linecache
import sys
import math

# 当用户输入关键字没有输入值时则提示


@on_natural_language({''}, only_to_me=False)
async def _(session: NLPSession):
	return IntentCommand(name='fd', confidence=100.0, current_arg=session.msg_text)


@on_command('fd', aliases=('.fd', 'fd'), only_to_me=False)
async def fd(session: session):
	gid = session.event.group_id
	result = await fd_check(session.current_arg, gid)
	if result != "":
		await session.send(result)


#  当用户输入关键字和值时直接运行
@fd.args_parser
async def get_fd(name: str) -> str:
	pass
	return ""
	
	
async def fd_check(msg,gid):
	result = sql_exec.sqlite_exec("general.db","SELECT * FROM repeat WHERE Group_id = '{}';".format(str(gid)))
	tim = result[0][2]
	if result == []:
		sql_exec.sqlite_exec("general.db","INSERT INTO repeat (Group_id, Word, Time) VALUES ('{}', '{}', {});".format(str(gid),str(msg),"1"))
	elif int(tim) > 1 and msg == result[0][1]:
		sql_exec.sqlite_exec("general.db","UPDATE repeat SET Time = {} WHERE Group_id = '{}';".format("-1",str(gid)))
		logger.info("[FSO-Tech复读BOT]复读成功: "+msg)
		return str(msg)
	elif int(tim) <= 2 and msg == result[0][1]:
		sql_exec.sqlite_exec("general.db","UPDATE repeat SET Time = {} WHERE Group_id = '{}';".format(tim+1,str(gid)))
	else:
		sql_exec.sqlite_exec("general.db","UPDATE repeat SET Time = {},Word = '{}' WHERE Group_id = '{}';".format("1",str(msg),str(gid)))
	return ""

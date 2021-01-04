from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
import random

# 当用户输入关键字没有输入值时则提示
@on_command('roll', aliases=('roll', '抽奖'), only_to_me=False)
async def roll(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    roll_range = session.get('roll_range', prompt='你想roll的范围是多少(1~?) [可选人数，不填写代表1位]')
    # 获取城市的天气预报
    roll_resort = await get_rollpoint(roll_range)
    # 向用户发送天气预报
    await session.send(roll_resort, at_sender=True)


#  当用户输入关键字和值时直接运行
@roll.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['roll_range'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('你想roll的范围是多少(1~?) [可选人数，不填写代表1位]' )

    session.state[session.current_key] = stripped_arg


async def get_rollpoint(roll_range: str) -> str:
	try:
		arglist = roll_range.split(" ")
		
		
		
		
		if len(arglist) == 2:
			if not is_number(arglist[0]) or not is_number(arglist[1]):
				return '请输入数字，这你roll🐴呢'
			if int(arglist[1]) >= int(arglist[0]):
			
				return '北府数学? 这你roll🐴呢'
				
			luckyguy = []
			
			for i in range(int(arglist[1])):
				luckynumber = str(random.randint(1,int(arglist[0])))
				
				while luckynumber in luckyguy:
					luckynumber = str(random.randint(1,int(arglist[0])))
				
				luckyguy.append(luckynumber)
				
			luckyguy = list(map(int, luckyguy))
			luckyguy.sort()
			luckyguy = list(map(str, luckyguy))
			
			return '那么幸运观众们是: ' + " ".join(luckyguy)
		elif len(arglist) == 1:
			if not is_number(arglist[0]):
				return '请输入数字，这你roll🐴呢'
			return '那么幸运观众是: ' + str(random.randint(1,int(arglist[0])))
		else:
			return '参数错误'
	except Exception as e:
		return "内部出错，请联系牛痣:\n" + repr(e)
		
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
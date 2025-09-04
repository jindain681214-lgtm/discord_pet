import discord
import os
import json
import random
from discord.ext import tasks

# 봇의 의도(intents)를 설정합니다.
intents = discord.Intents.default()
intents.message_content = True # 메시지 내용을 읽기 위한 권한

client = discord.Client(intents=intents)

# --- 펫 데이터 관리 ---
PET_FILE = "pets.json"
pets = {}

def save_data():
    with open(PET_FILE, 'w', encoding='utf-8') as f:
        json.dump(pets, f, indent=4, ensure_ascii=False)

def load_data():
    global pets
    try:
        with open(PET_FILE, 'r', encoding='utf-8') as f:
            pets = json.load(f)
    except FileNotFoundError:
        print("펫 데이터 파일이 없어 새로 생성합니다.")
        pets = {}
    except json.JSONDecodeError:
        print("펫 데이터 파일이 손상되어 새로 생성합니다.")
        pets = {}

load_data()
# --------------------

@tasks.loop(hours=1)
async def game_loop():
    print("자동 상태 변화 루프 실행...")
    for user_id, pet in pets.items():
        pet['hunger'] = max(0, pet['hunger'] - 5)
        pet['happiness'] = max(0, pet['happiness'] - 5)
    save_data()
    print("자동 상태 변화 완료.")
# --------------------

@client.event
async def on_ready():
    print(f'{client.user}으로 로그인했습니다!')
    print('봇이 준비되었습니다.')
    game_loop.start()

@client.event
async def on_message(message):
    # 봇 자신의 메시지는 무시합니다.
    if message.author == client.user:
        return

    # '!입양' 명령어
    if message.content == '!입양':
        user_id = str(message.author.id)
        if user_id in pets:
            await message.channel.send("이미 펫을 키우고 있어요!")
        else:
            pets[user_id] = {
                'name': 'pet',
                'level': 1,
                'xp': 0,
                'hunger': 100,
                'happiness': 100,
                'stage': '성장기'
            }
            save_data()
            await message.channel.send(f"{message.author.mention}님, 새로운 펫을 입양하셨어요! `!상태`로 펫의 상태를 확인해보세요.")

    # '!상태' 명령어
    elif message.content == '!상태':
        user_id = str(message.author.id)
        if user_id not in pets:
            await message.channel.send("아직 펫이 없어요. `!입양`으로 새로운 펫을 맞아주세요!")
        else:
            pet = pets[user_id]
            embed = discord.Embed(
                title=f"{message.author.display_name}님의 펫 정보",
                description=f"이름: **{pet['name']}** ({pet['stage']})",
                color=discord.Color.green()
            )
            embed.add_field(name="🌟 레벨", value=f"{pet['level']}", inline=True)
            embed.add_field(name="✨ 경험치", value=f"{pet['xp']}", inline=True)
            embed.add_field(name="❤️ 포만감", value=f"{pet['hunger']}/100", inline=False)
            embed.add_field(name="😊 행복도", value=f"{pet['happiness']}/100", inline=True)
            embed.set_footer(text="`!밥주기`로 밥을 주고, `!놀아주기`로 놀아줄 수 있어요.")
            await message.channel.send(embed=embed)

    # '!밥주기' 명령어
    elif message.content == '!밥주기':
        user_id = str(message.author.id)
        if user_id not in pets:
            await message.channel.send("아직 펫이 없어요. `!입양`으로 새로운 펫을 맞아주세요!")
            return
        
        pet = pets[user_id]
        if pet['hunger'] >= 100:
            await message.channel.send(f"{pet['name']}는 이미 배가 불러요!")
            return
        
        amount = random.randint(10, 20)
        xp_gain = 5
        pet['hunger'] = min(100, pet['hunger'] + amount)
        pet['xp'] += xp_gain
        save_data()
        await message.channel.send(f"냠냠! {pet['name']}에게 밥을 줬어요.\n포만감이 {amount}만큼, 경험치가 {xp_gain}만큼 올랐습니다. (현재 포만감: {pet['hunger']}/100)")

    # '!놀아주기' 명령어
    elif message.content == '!놀아주기':
        user_id = str(message.author.id)
        if user_id not in pets:
            await message.channel.send("아직 펫이 없어요. `!입양`으로 새로운 펫을 맞아주세요!")
            return

        pet = pets[user_id]
        if pet['happiness'] >= 100:
            await message.channel.send(f"{pet['name']}는 지금 너무 행복해요! 잠시 쉬게 해주세요.")
            return

        amount = random.randint(10, 20)
        xp_gain = 5
        pet['happiness'] = min(100, pet['happiness'] + amount)
        pet['xp'] += xp_gain
        save_data()
        await message.channel.send(f"신난다! {pet['name']}와 즐겁게 놀아줬어요.\n행복도가 {amount}만큼, 경험치가 {xp_gain}만큼 올랐습니다. (현재 행복도: {pet['happiness']}/100)")

# 아래에 토큰을 입력해요.
client.run('YOUR_BOT_TOKEN')

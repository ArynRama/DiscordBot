import json
import discord
from discord.ext import commands


def set_data(server_id:str, key:str, data):
    with open('data.json', 'r') as j:
        js:dict = json.load(j)

    server_id = str(server_id)
    if server_id in js.keys():
        js[server_id][key] = data
    else:
        js[server_id] = {key: data}

    with open('data.json', 'w+') as j:
        json.dump(js, j, indent="\t")

def get_data(server_id:str, key:str):
    with open('data.json', 'r') as j:
        js:dict = json.load(j)
    
    server_id = str(server_id)

    if server_id in js.keys():
        if key in js[server_id].keys():
            return js[server_id][key]
        else:
            return None
    else:
        return None
    
async def user_has_perm(client: commands.Bot, user:discord.Member, perm:discord.Permissions):
    for a in set(perm):
        if a[1] == True:
            break
    
    if a in set(user.guild_permissions) or user.guild_permissions.administrator or user.guild.owner_id == user.id:
        return True
    else:
        return False
    
async def send(ctx: discord.ApplicationContext, message:str , fields: list[dict] = None):
    embed = discord.Embed(colour=discord.Colour(int('0864f4', 16)))
    embed.title = message
    if fields != None:
        i = 1
        for field in fields:
            if len(embed.fields) == 25:
                break
            embed.add_field(name = f" {i}. {field['name']}", value= field["author"], inline=False)
            i += 1
    return await ctx.respond(embed=embed, ephemeral=True)

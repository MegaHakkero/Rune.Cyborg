import importlib.util
import discord
import asyncio
import shlex
import types
import os

from inspect import getfullargspec

class CyborgCommand:
	def __init__(self, cmd):
		if not isinstance(cmd, str):
			raise ValueError("cmd must be a string")
		self.raw_command = cmd
		lexer = shlex.shlex(cmd, posix=True)
		lexer.wordchars += "-./~?*="
		lexer.whitespace_split = True
		cmdlist = list(lexer)
		if len(cmdlist) < 1:
			raise ValueError("cmd is empty")
		pathlist = cmdlist[0].split(".", 1)
		if len(pathlist) < 2:
			raise ValueError("no module path in command")
		self.module = pathlist[0]
		self.command = pathlist[1]
		self.args = cmdlist[:1]

class CyborgModule:
	def __init__(self, name, path):
		if not isinstance(name, str):
			raise ValueError("name is not a string")
		if not isinstance(path, str):
			raise ValueError("path is not a string")
		modspec = None
		mod = None
		commands = dict()
		try:
			modspec = importlib.util.spec_from_file_location(name, path)
			mod = importlib.util.module_from_spec(modspec)
			modspec.loader.exec_module(mod)
		except OSError as err:
			raise OSError("cannot load module: " + str(err))
		for key in mod.__dict__:
			if callable(getattr(mod, key)) and key.startswith("cmd_"):
				commands[key[4:]] = getattr(mod, key)
		self.path     = path
		self.name     = name
		self.mod      = mod
		self.commands = commands

class MedjedCyborg:
	def __init__(self, token, uid, cmd_prefix="//", logging=False, log_prefix="Medjed.Cyborg", mod_dir="./modules"):
		tmp_prefix = log_prefix
		tmp_cmd_prefix = cmd_prefix
		if not isinstance(token, str):
			raise ValueError("token is not a string")
		if not isinstance(uid, int):
			raise ValueError("uid is not an int")
		if not mod_dir:
			raise NameError("mod_dir")
		elif not isinstance(mod_dir, str):
			raise ValueError("mod_dir is not a string")
		if not log_prefix:
			tmp_prefix = "Medjed.Cyborg"
		if not cmd_prefix:
			tmp_cmd_prefix = "//"
		self.version    = "v1.0.0"
		self.token      = token
		self.logging    = logging
		self.log_prefix = str(tmp_prefix)
		self.cmd_prefix = str(tmp_cmd_prefix)
		self.mod_dir    = os.path.realpath(mod_dir)
		self.modules    = list()
		self.client     = discord.Client()
		self.uid        = uid

		@self.client.event
		async def on_ready():
			if self.logging: self.log("connected")
			await self.handle_ready()	
	
		@self.client.event
		async def on_message(msg):
			if msg.author.id == self.uid and msg.content.startswith(self.cmd_prefix):
				if self.logging: self.log("got command: " + msg.content)
				cmd = None
				try:
					cmd = CyborgCommand(msg.content[len(self.cmd_prefix):])
				except Exception as err:
					self.log("invalid command: " + str(err))
					await msg.channel.send(embed=self.embed("invalid syntax (" + str(err) + ")", 0xBB0000))
					return
				await self.handle_command_prerun(cmd)
				mod_found = False
				for mod in self.modules:
					if mod.name == cmd.module:
						mod_found = True
						cmd_found = False
						for cmd2 in mod.commands:
							if cmd2 == cmd.command:
								cmd_found = True
								try:
									if len(getfullargspec(mod.commands[cmd.command])[0]) < 3:
										await mod.commands[cmd.command](self, msg)
									else:
										await mod.commands[cmd.command](self, msg, *cmd.args)
								except Exception as err:
									if self.logging: self.log("failed to run " + cmd.module + "." + cmd.command + ": " + str(err))
									await msg.channel.send(embed=self.embed("failed to run " + cmd.module + "." + cmd.command + ": " + str(err), 0xBB0000))
								if self.logging: self.log("successfully called " + cmd.module + "." + cmd.command)
								break
						if not cmd_found:
							if self.logging: self.log("no such command: " + cmd.command + " in module " + cmd.module)
							await msg.channel.send(embed=self.embed("no such command `" + cmd.command + "` in module `" + cmd.module + "`", 0xBB0000))
						break
				if not mod_found:
					if self.logging: self.log("no such module: " + cmd.module)
					await msg.channel.send(embed=self.embed("no such module: `" + cmd.module + "`", 0xBB0000))
				await self.handle_command_postrun(cmd)

	def log(self, string):
		print(str(self.log_prefix) + ":", string)

	def connect(self):
		if self.logging: self.log("trying to connect")
		self.client.run(self.token, bot=False)

	def load_module(self, path):
		if not path.endswith(".py"):
			if self.logging: self.log("not a python script: " + path)
			return
		mod = None
		try:
			name = os.path.basename(path)[:-3]
			for mod2 in self.modules:
				if name == mod2.name:
					if self.logging: self.log("a module with the same name is already loaded")
					return
			mod = CyborgModule(name, path)
		except Exception as err:
			self.log("failed loading module: " + str(err))
			return
		self.modules.append(mod)

	def load_all_modules(self):
		mods = None
		try:
			mods = os.listdir(self.mod_dir)
		except OSError as err:
			self.log("failed loading modules from " + self.mod_dir + ": " + str(err))
			return
		for i in range(len(mods) - 1):
			if not mods[i].endswith(".py"): del mods[i]
		for file in mods:
			self.load_module(self.mod_dir + "/" + file)

	def embed(self, description, color):
		if not isinstance(description, str):
			if self.logging: self.log("embed: invalid description")
			return None
		if not isinstance(color, int):
			if self.logging: self.log("embed: invalid color")
		embed = discord.Embed()
		embed.description = description
		embed.type = "rich"
		embed.colour = color
		embed.set_footer(text="Medjed.Cyborg " + self.version)
		return embed

	async def handle_ready(self):
		self.log("DUMMY handle_ready called")

	async def handle_command_prerun(self, cmd):
		self.log("DUMMY handle_command_prerun called")

	async def handle_command_postrun(self, cmd):
		self.log("DUMMY handle_command_postrun called")


# Medjed.Cyborg
A module-based framework for writing Discord selfbots in Python
## How to use
If you're just writing a selfbot, you only need to care about the `MedjedCyborg` class, which is the client. It has a few required parameters without default values (your token and user ID). The other parameters are also required, but they have a default value, so you can just use those. Here's a full list of all the arguments you can pass to the client:
```md
token (string): Your user token - used to log into Discord
uid (int): Your user ID - used to make sure no-one else can run commands
cmd_prefix (string): The prefix that should be attached to each command you want to run in Discord
logging (bool): Whether to do logging or not (NOTE: not to a file, but the terminal)
log_prefix (string): The prefix that should be attached to each line of Medjed.Cyborg's log output
mod_dir (string): A folder for the MedjedCyborg.load_all_modules() function
```
Following are all of the client's functions that you can use in modules to implement functionality:
```py
MedjedCyborg.log(message <string>) # Prints a log message to the terminal screen
MedjedCyborg.connect() # Connects and logs the client into Discord
MedjedCyborg.load_module(path <string>) # Attempts to load a module from the provided full path
MedjedCyborg.load_all_modules() # Attempts to load all modules from the directory given to the client with the mod_dir parameter
MedjedCyborg.embed(description <string>, color <int>) # A convenient function for creating text-only embeds
```
I've also included in some hooks for certain events like the client connecting. They're all coroutines (`async def`). The `CyborgCommand` type I've used in some of them is an object that automatically parses commands when initialized.
```py
MedjedCyborg.handle_ready() # Gets called when the client becomes ready (AKA has connected and logged in)
MedjedCyborg.handle_command_prerun(cmd <CyborgCommand>) # Gets called right after a command has been parsed, but not yet called
MedjedCyborg.handle_command_postrun(cmd <CyborgCommand>) # Gets called right after a command has finished executing, whether it errored or not.
```
## How to write modules
It's pretty simple. Commands are just coroutines whose names are prefixed with `cmd_`. All commands get passed the cyborg instance itself as well as the message object of the command that's being executed. They're automatically loaded by Medjed.Cyborg. This means that you have to import `asyncio` in each of your modules. Here's an example module called `Example` that sends a green embed with `Hello World` as its description as a response to the command `Hello`.
```py
# Example.py
import asyncio

async def cmd_Hello(client, message):
  await message.channel.send(embed=client.embed("Hello World!", 0x00AA00))
```
Modules' names are determined by their file name, so `Example.py` would create a module called `Example`. The command system works as follows: the first part right after the prefix but before the first whitespace character is the actual command, which consists of two parts: the module containing the command, and the command itself, in that order. They are separated by a dot. The other parts of the command are simply parameters for it.

To load this example module, you have to load it with the `load_module` function of the client:
```py
MedjedCyborg.load_module("Example.py")
```
After this, you can use the `Hello` command in Discord: `<prefix>Example.Hello`, `<prefix>` being the command prefix you chose when you initialized the client, or `//` if you used the default one.

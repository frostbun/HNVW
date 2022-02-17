from discord import ButtonStyle
from discord.utils import MISSING
from discord.ui import View as _View, Button as _Button, Select as _Select

class View(_View):
    def __init__(self, *items, timeout=None, check=[], on_timeout=[], params={}):
        super().__init__(
            *items,
            timeout = timeout,
        )
        self.on_t_o = on_timeout
        self.check = check
        self.params = params

    async def on_timeout(self):
        for on_t_o in self.on_t_o:
            await on_t_o(**self.params)

    async def interaction_check(self, i):
        for check in self.check:
            if not await check(i): return False
        await i.message.delete()
        return True

class Button(_Button):
    def __init__(
        self,
        label = None,
        emoji = None,
        url = None,
        style = ButtonStyle.gray,
        disabled = False,
        custom_id = None,
        row = None,
        callback = [],
        params = {},
    ):
        super().__init__(
            label = label,
            emoji = emoji,
            url = url,
            style = style,
            disabled = disabled,
            custom_id = custom_id,
            row = row,
        )
        self.cb = callback
        self.params = params

    async def callback(self, i):
        if "context" in self.params: self.params["context"].author = i.user
        for cb in self.cb: await cb(**self.params)

class Select(_Select):
    def __init__(
        self,
        placeholder,
        options,
        disabled = False,
        custom_id = MISSING,
        row = None,
        callback = [],
        default_param_name = "index",
        default_param_type = int,
        params = {},
    ):
        super().__init__(
            placeholder = placeholder,
            options = options,
            disabled = disabled,
            custom_id = custom_id,
            row = row,
        )
        self.cb = callback
        self.default_param_name = default_param_name
        self.default_param_type = default_param_type
        self.params = params

    async def callback(self, i):
        self.params[self.default_param_name] = self.default_param_type(self.values[0])
        if "context" in self.params: self.params["context"].author = i.user
        for cb in self.cb: await cb(**self.params)

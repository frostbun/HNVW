from discord import ui

from configs import VIEW_TIMEOUT

class View(ui.View):
    def __init__(self, *items, timeout=VIEW_TIMEOUT, on_timeout=[]):
        super().__init__(
            *items,
            timeout = timeout
        )
        self.on_t_o = on_timeout

    async def on_timeout(self):
        for on_t_o in self.on_t_o:
            await on_t_o()

class Button(ui.Button):
    def __init__(self, label, style, disabled=False, callback=[], check=[], params={}):
        super().__init__(
            label = label,
            style = style,
            disabled = disabled,
        )
        self.cb = callback
        self.check = check
        self.params = params

    async def callback(self, i):
        for check in self.check:
            if not await check(i):
                return
        await i.message.delete()
        if "context" in self.params:
            self.params["context"].author = i.user
        for cb in self.cb:
            await cb(**self.params)

class Select(ui.Select):
    def __init__(self, placeholder, options, callback=[], check=[], default_param_name="index", default_param_type=int, params={}):
        super().__init__(
            placeholder = placeholder,
            options = options,
        )
        self.cb = callback
        self.check = check
        self.default_param_name = default_param_name
        self.default_param_type = default_param_type
        self.params = params

    async def callback(self, i):
        for check in self.check:
            if not await check(i):
                return
        await i.message.delete()
        if "context" in self.params:
            self.params["context"].author = i.user
        self.params[self.default_param_name] = self.default_param_type(self.values[0])
        for cb in self.cb:
            await cb(**self.params)

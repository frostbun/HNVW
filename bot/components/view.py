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
        [ await on_t_o() for on_t_o in self.on_t_o ]

class Button(ui.Button):
    def __init__(self, label, style, disabled=False, callback=[], check=[], **params):
        super().__init__(
            label = label,
            style = style,
            disabled = disabled,
        )
        self.cb = callback
        self.check = check
        self.params = params

    async def callback(self, i):
        if all(await check(i) for check in self.check):
            await i.message.delete()
            if "ctx" in self.params:
                self.params["ctx"].author = i.user
            [ await cb(**self.params) for cb in self.callback ]

class Select(ui.Select):
    def __init__(self, placeholder, options, callback=[], check=[], default_param_name="index", **params):
        super().__init__(
            placeholder = placeholder,
            options = options,
        )
        self.cb = callback
        self.check = check
        self.default_param_name = default_param_name
        self.params = params

    async def callback(self, i):
        if all(await check(i) for check in self.check):
            await i.message.delete()
            if "ctx" in self.params:
                self.params["ctx"].author = i.user
            self.params[self.default_param_name] = int(self.values[0])
            [ await cb(**self.params) for cb in self.callback ]

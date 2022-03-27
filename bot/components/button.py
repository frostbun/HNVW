from discord import ButtonStyle, Interaction
from discord.ui import Button as _Button

class Button(_Button):
    def __init__(
        self,
        label = None,
        emoji = None,
        url = None,
        style = ButtonStyle.gray,
        custom_id = None,
        row = None,
        disabled = False,
        callbacks = (),
    ) -> None:
        super().__init__(
            label = label,
            emoji = emoji,
            url = url,
            style = style,
            custom_id = custom_id,
            row = row,
            disabled = disabled,
        )
        self.callbacks = callbacks

    async def callback(self, interaction: Interaction) -> None:
        for func in self.callbacks:
            await func(interaction)

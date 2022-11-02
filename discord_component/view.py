from discord import Interaction
from discord.ui import Item
from discord.ui import View as _View

from .callback import InteractionCallback


class View(_View):
    def __init__(
        self,
        *items: Item,
        auto_delete: bool = True,
        timeout: float | None = None,
        checks: list[InteractionCallback] = [],
        on_timeouts: list[InteractionCallback] = [],
    ) -> None:
        super().__init__(
            *items,
            timeout = timeout,
        )
        self.checks = checks 
        self.auto_delete = auto_delete
        self.on_timeouts = on_timeouts

    async def on_timeout(self) -> None:
        for func in self.on_timeouts:
            await func()

    async def interaction_check(self, interaction: Interaction) -> bool:
        for func in self.checks:
            if not await func(interaction):
                return False
        if self.auto_delete:
            await interaction.message.delete()
        return True

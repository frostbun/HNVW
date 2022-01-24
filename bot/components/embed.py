from discord import Embed as _Embed, Color

class Embed(_Embed):
    def __init__(
        self,
        title,
        desc,
        author_text = "",
        author_icon = _Embed.Empty,
        footer_text = _Embed.Empty,
        footer_icon = _Embed.Empty,
        thumbnail = _Embed.Empty,
        image = _Embed.Empty,
        color = Color.red(),
    ):
        super().__init__(
            title = title,
            description = desc,
            color = color,
        )
        self.set_author(name = author_text, icon_url = author_icon)\
            .set_footer(text = footer_text, icon_url = footer_icon)\
            .set_thumbnail(url = thumbnail)\
            .set_image(url = image)

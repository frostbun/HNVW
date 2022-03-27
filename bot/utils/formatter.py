def format_duration(duration) -> str:
    duration = int(duration)
    return f"{duration//60:02d}:{duration%60:02d}" if duration < 3600\
        else f"{duration//3600:02d}:{duration%3600//60:02d}:{duration%60:02d}"

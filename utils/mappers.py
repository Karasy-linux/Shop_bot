def list_to_str(names: list, parse_mode: str | None = None) -> str:
    if not names:
        return ""

    if parse_mode == "HTML":
        return ", ".join(f"<b>{name}</b>" for name in names)
    if parse_mode == "MarkdownV2":
        return ", ".join(f"*{name}*" for name in names)

    return ", ".join(names)

import click


def get_description():
    MARKER = "# Write your description above"
    message = click.edit("\n\n" + MARKER)
    if message is not None:
        return message.split(MARKER, 1)[0].rstrip("\n")


def get_note():
    MARKER = "# Write your note above"
    message = click.edit("\n\n" + MARKER)
    if message is not None:
        return message.split(MARKER, 1)[0].rstrip("\n")

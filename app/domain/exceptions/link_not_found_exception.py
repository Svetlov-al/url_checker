from dataclasses import dataclass


@dataclass(eq=False)
class LinkNotFoundException(Exception):
    message: str

    def __str__(self):
        return self.message

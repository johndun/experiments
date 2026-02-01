"""Custom exceptions for md_view."""


class MdViewError(Exception):
    """Base exception for md_view."""

    pass


class FileNotFoundError(MdViewError):
    """Raised when markdown file is not found."""

    pass


class RenderError(MdViewError):
    """Raised when markdown rendering fails."""

    pass

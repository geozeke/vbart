#!/usr/bin/env python3
"""Support classes for status-label handling."""

import sys


class ExhaustedListError(Exception):
    """Raised when code attempts to remove a label from an empty list."""

    def __init__(self):
        """Initialize the exception message."""
        self.message = "Cannot remove label, list of labels is empty."
        super().__init__(self.message)


class Labels:
    """Manage status labels for aligned console output."""

    def __init__(self, s: str) -> None:
        """Create a new ``Labels`` object.

        Parameters
        ----------
        s : str
            Multiline string containing one label per line.
        """
        # The (t := token.strip()) part of the list comprehension below
        # is python's assignment expression and takes care of any blank
        # lines or leading/trailing whitespace in the docstring. It
        # assigns token.strip() to t then evaluates t. If t is an empty
        # string, it evaluates to False otherwise it's True.
        self.labels = [t for token in s.split("\n") if (t := token.strip())]
        self.pad = len(max(self.labels, key=len)) + 3
        return

    def next(self) -> None:
        """Print the next label.

        Raises
        ------
        ExhaustedListError
            If the label list is empty.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        print(f"{self.labels.pop(0):.<{self.pad}}", end="", flush=True)
        return

    def pop_first(self) -> str:
        """Pop and return the first label.

        Returns
        -------
        str
            The first label.

        Raises
        ------
        ExhaustedListError
            If the label list is empty.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        return self.labels.pop(0)

    def pop_last(self) -> str:
        """Pop and return the last label.

        Returns
        -------
        str
            The last label.

        Raises
        ------
        ExhaustedListError
            If the label list is empty.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        return self.labels.pop(-1)

    def pop_item(self, index: int) -> str:
        """Pop and return the label at a given index.

        Parameters
        ----------
        index : int
            Index of the label to remove.

        Returns
        -------
        str
            The removed label.

        Raises
        ------
        ExhaustedListError
            If the label list is empty.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        try:
            label = self.labels.pop(index)
            return label
        except IndexError as e:
            print(f"{e}. Attempting to pop index {index}.")
            print("Terminating program.")
            sys.exit(1)


if __name__ == "__main__":
    pass

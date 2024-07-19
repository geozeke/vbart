#!/usr/bin/env python3
"""Support classes."""

import sys


class ExhaustedListError(Exception):
    """Exception when attempting to pop elements from an empty list.

    Parameters
    ----------
    Exception : Python Exception type
        ExhaustedListError is a sub-class of Python's Exception class.
    """

    def __init__(self):
        """Initialize exception."""
        self.message = "Cannot remove label, list of labels is empty."
        super().__init__(self.message)


class Labels:
    """Class to manage status labels."""

    def __init__(self, s: str) -> None:
        """Create a new Labels object.

        Parameters
        ----------
        s : str
            This is a docstring that has one label per line, the
            initializer will repackage it into a list, along with an int
            variable (pad) that represents the length of the longest
            label. This is used for justifying the output when printing.
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
        """Print the next label (the one at position 0).

        Raises
        ------
        ExhaustedListError
            If attempting to pop from an empty list.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        print(f"{self.labels.pop(0):.<{self.pad}}", end="", flush=True)
        return

    def pop_first(self) -> str:
        """Pop and return the first label (position 0).

        Returns
        -------
        str
            A label.

        Raises
        ------
        ExhaustedListError
            If attempting to pop from an empty list.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        return self.labels.pop(0)

    def pop_last(self) -> str:
        """Pop and return the last label (position -1).

        Returns
        -------
        str
            A label.

        Raises
        ------
        ExhaustedListError
            If attempting to pop from an empty list.
        """
        if len(self.labels) == 0:
            raise ExhaustedListError()
        return self.labels.pop(-1)

    def pop_item(self, index: int) -> str:
        """Pop a label from a given index.

        Parameters
        ----------
        index : int
            The index to pop from.

        Returns
        -------
        str
            The popped label.

        Raises
        ------
        ExhaustedListError
            If attempting to pop from an empty list.
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

from __future__ import annotations
from typing import List, Union, TYPE_CHECKING
from huligutta.piece import Goat, Tiger
import address

if TYPE_CHECKING:
    from huligutta.board import Board


class Position:
    """
    Represents a position on the board, identified
    with a letter and number i.e. "a1".

    A position can contain either empty space, a Tiger, or a Goat.
    """

    def __init__(self, board: Board, addr: str):

        # a reference to the board
        self.board = board

        # the position address
        self.address = addr

        # the piece currently in this position
        self.piece: Union[tuple, Piece] = ()

        try:
            assert address.is_valid(self.address) is True

        except AssertionError as e:
            print("Tried initializing position with invalid address")
            raise e

    def is_empty(self) -> bool:
        return self.piece == ()

    def is_goat(self) -> bool:
        return type(self.piece) is Goat

    def is_tiger(self) -> bool:
        return type(self.piece) is Tiger

    def set_piece(self, piece: Union[tuple, "Piece"]):
        """Place a piece into this position."""
        self.piece = piece

    def clear(self):
        """Delete any piece from this position."""
        # FIXME: have None represent an empty piece instead?
        self.set_piece(())

    def place_tiger(self):
        self.set_piece(Tiger(self.board, self))
        # print(f"a tiger has been placed at {self.address}")

    def place_goat(self):
        self.set_piece(Goat(self.board, self))
        # print(f"a goat has been placed at {self.address}")

    def get_adjacent_positions(self) -> List["Position"]:
        adjacent_addrs = address.get_adjacent_addrs(self.address)
        return [self.board.get_pos(addr) for addr in adjacent_addrs]

    def is_adjacent(self, pos_to: "Position") -> bool:
        """
        Checks if this position is adjacent to the given position.
        """
        return address.is_adjacent(self.address, pos_to.address)

    def __str__(self):
        if self.is_empty():
            return "-"
        else:
            return str(self.piece)

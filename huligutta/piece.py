from __future__ import annotations
from typing import List, Union, Optional, TYPE_CHECKING
import address

if TYPE_CHECKING:
    from huligutta.board import Board
    from huligutta.position import Position


class Piece:
    """
    Represents a piece that can occupy any position on the board.
    """

    def __init__(self, board: Board, pos: Position):
        # the board this piece is on
        self.board = board

        # the current position this piece is in
        self.pos = pos

    def get_valid_moves(self) -> List[str]:
        """
        Get a list of all addresses this piece can move to.
        """
        valid_moves = []
        for pos in self.pos.get_adjacent_positions():
            if pos.is_empty():
                valid_moves.append(pos.address)

        return valid_moves

    def move(self, target_pos: Position) -> Optional[str]:
        """
        Move this piece to a new position.

        Returns notation of the move if the move was successful.
        """

        if self.pos.is_adjacent(target_pos) and target_pos.is_empty():
            self.pos.set_piece(())
            # will place a Tiger if called from inside a Tiger,
            # and ditto for Goats
            target_pos.set_piece(type(self)(self.board, target_pos))
            res = f"{self.pos.address},\t{target_pos.address}"
            self.pos = target_pos  # update position reference
            return res

        print(f"unable to move this piece to {target_pos.address}")
        return None

    def get_next_adjacent_pos(self, target_pos: Position) -> Optional[Position]:
        """
        Return the next adjacent position after the target position. This is
        used for the Tiger capturing logic.

        For example, if this piece is in a1 and the target position is b1,
        then the next adjacent position will be c1.

        If the target position is not adjacent, None is returned.
        If the next adjacent position does not exist, or is not empty,
        then None is returned.
        """

        if not self.pos.is_adjacent(target_pos):
            return None

        landing_addr = address.move_towards(self.pos.address, target_pos.address, 2)

        if landing_addr:
            new_pos = self.board.get_pos(landing_addr)
            if not new_pos.is_empty():
                return None

            return new_pos

        return None


class Tiger(Piece):
    """
    Represents a Tiger piece, symbolized with an "X".

    During their turn, Tigers can move to an adjacent empty position,
    or can capture an adjacent Goat piece by jumping over it into
    the next empty position.

    If there is no empty position to land on behind a Goat, the Tiger
    cannot move over it and the Goat cannot be captured
    (the Goat is considered "safe").
    """

    def move(self, target_pos: Position):

        # check if moving to target_pos is a capturing move
        capturing_moves = self._get_capturing_positions()
        for landing_pos, goat_pos in capturing_moves:
            if target_pos.address == landing_pos.address:
                if self.capture(goat_pos):
                    return (
                        f"{self.pos.address},\t"
                        + f"x{goat_pos.address},\t"
                        + f"{landing_pos.address}"
                    )
                else:
                    return None

        # call the move method from Piece
        return super().move(target_pos)

    def _get_capturing_positions(self) -> List[tuple]:
        """
        Returns a list of tuples of landing positions and goat positions
        where moving to the landing position will capture the goat.
        """
        # a list of positions where moving to it will capture a piece
        capturing_moves: List[tuple] = []

        # check adjacent positions and check if they're goats
        for goat_pos in self.pos.get_adjacent_positions():
            if isinstance(goat_pos.piece, Goat):

                landing_addr = self.can_capture_pos(goat_pos.address)

                if landing_addr:
                    # add a tuple of address and goat position
                    capturing_moves.append((self.board.get_pos(landing_addr), goat_pos))

        return capturing_moves

    def can_capture_pos(self, addr: str) -> Optional[str]:
        """
        Checks if this tiger can capture a goat placed at a
        specific position.

        If it can, then the landing position is returned.
        """
        pos = self.board.get_pos(addr)

        # if pos to capture not adjacent to this piece, cannot capture
        if not self.pos.is_adjacent(pos):
            return None

        # if pos is in a corner, cannot capture
        if address.is_in_corner(addr):
            return None

        # check adjacent positions to the goat
        for empty_pos in pos.get_adjacent_positions():
            if empty_pos is self.pos:
                continue

            delta = address.get_displacement(self.pos.address, empty_pos.address)
            if delta not in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                continue

            if empty_pos.is_empty():
                return empty_pos.address

        return None

    def get_capturing_moves(self) -> List[str]:
        """
        Get a list of addresses where moving there will capture
        a goat.
        """
        pos_tuples = self._get_capturing_positions()
        return [tup[0].address for tup in pos_tuples]

    def get_valid_moves(self) -> List[str]:
        # combine capturing moves and valid moves
        valid_moves = super().get_valid_moves()
        valid_moves.extend(self.get_capturing_moves())
        return valid_moves

    def capture(self, target_pos: Position) -> bool:
        # the position where the Tiger will land
        landing_pos = self.get_next_adjacent_pos(target_pos)

        if not landing_pos:
            print(
                "cannot capture: cannot find landing position ("
                + self.pos.address
                + " -> "
                + target_pos.address
                + ")"
            )
            return False

        if not isinstance(target_pos.piece, Goat):
            print("cannot capture: move does not capture a Goat")
            return False

        if not isinstance(self.pos.piece, Tiger):  # shouldn't happen
            print("cannot capture: this piece is not a Tiger")
            return False

        self.pos.set_piece(())  # old position of tiger
        target_pos.set_piece(())  # captured goat piece
        landing_pos.set_piece(Tiger(self.board, landing_pos))  # new position of tiger

        self.board.num_captured += 1  # increment captured pieces
        # print(f"the goat at {target_pos.address} has been captured")

        return True

    def __str__(self):
        return "X"  # the string representation of this piece


class Goat(Piece):
    """
    Represents a Goat piece, symbolized by an "O".

    During their turn, a Goat may move to any adjacent empty position.
    Unlike Tigers, Goats cannot capture pieces.
    """

    def __str__(self):
        return "O"  # the string representation of this piece

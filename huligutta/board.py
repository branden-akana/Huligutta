from typing import List, Optional, cast
from huligutta.position import Position
from huligutta.piece import Piece, Tiger, Goat
import copy
import address


class Board:
    """
    Represents the game board.

    In Huligutta, there are six columns a-f, and five rows 0-4.
    In the columns a and f, rows 0 and 4 do not exist.
    The position in row 0 is shared by columns b-e.
    """

    def __init__(self):

        # the position shared by columns b-e
        self.origin = ()

        # columns a-f

        self.a = {1: (), 2: (), 3: ()}
        self.b = {0: self.origin, 1: (), 2: (), 3: (), 4: ()}
        self.c = {0: self.origin, 1: (), 2: (), 3: (), 4: ()}
        self.d = {0: self.origin, 1: (), 2: (), 3: (), 4: ()}
        self.e = {0: self.origin, 1: (), 2: (), 3: (), 4: ()}
        self.f = {1: (), 2: (), 3: ()}

        # a 2D array of positions (column-major)
        self.positions = [self.a, self.b, self.c, self.d, self.e, self.f]

        # the number of captured goats
        self.num_captured = 0

        # the number of moves made
        # self.num_moves = 0

        # the history of previous moves
        self.move_history = []

        # if True, then 15 goats have been placed at one point
        self.is_all_goats_placed = False

        self.clear()

    def clear(self):
        """
        Reset the board.
        """
        self.positions = {}
        for let in address.LETTERS:  # iterate through columns
            self.positions[let] = {}

            for num in address.NUMBERS:  # iterate through rows
                addr = let + num
                # check if this position ID is valid
                if address.is_valid(addr):
                    if num == 0:
                        pos = Position(self, "b0")
                    else:
                        pos = Position(self, addr)

                    self.positions[let][int(num)] = pos

        # also reset the number of captured pieces
        self.num_captured = 0
        self.move_history = []
        self.is_all_goats_placed = False

        # print("the board has been cleared")

    def copy_board(self, original=None) -> dict:
        """Copy the board state."""
        original = original or self.positions
        positions: dict = {}
        for let in address.LETTERS:  # iterate through columns
            positions[let] = {}
            for num in address.NUMBERS:  # iterate through rows
                addr = let + num
                if address.is_valid(addr):
                    if num == 0:
                        pos = Position(self, "b0")
                    else:
                        pos = Position(self, addr)

                    if original[let][int(num)].is_tiger():
                        pos.place_tiger()
                    elif original[let][int(num)].is_goat():
                        pos.place_goat()
                    positions[let][int(num)] = pos
        return positions

    def print_board(self):
        """
        Print the board.
        """
        a, b, c, d, e, f = self.positions.values()
        num_tigers, num_goats = self.num_pieces()

        print(f"\t*\t*\t{ b[0] }\t*\t*\t")
        print(f"{ a[1] }\t{ b[1] }\t{ c[1] }\t\t{ d[1] }\t{ e[1] }\t{ f[1] }")
        print(f"{ a[2] }\t{ b[2] }\t{ c[2] }\t\t{ d[2] }\t{ e[2] }\t{ f[2] }")
        print(f"{ a[3] }\t{ b[3] }\t{ c[3] }\t\t{ d[3] }\t{ e[3] }\t{ f[3] }")
        print(f"\t{ b[4] }\t{ c[4] }\t\t{ d[4] }\t{ e[4] }")

        print(f"tigers: {num_tigers}, goats: {num_goats}")
        print(f"captured goats: {self.num_captured}")

    def num_pieces(self) -> tuple:
        """Get the number of Tigers and Goats."""

        num_tigers, num_goats = 0, 0

        for col in self.positions.values():
            for pos in col.values():
                if type(pos) is tuple:
                    continue
                if isinstance(pos.piece, Tiger):
                    num_tigers += 1
                if isinstance(pos.piece, Goat):
                    num_goats += 1

        return num_tigers, num_goats

    def get_num_goats(self) -> int:
        """Get the number of Goats."""
        return len(self.get_all_goat_positions())

    def get_num_tigers(self) -> int:
        """Get the number of Tigers."""
        return len(self.get_all_tiger_positions())

    def get_pos(self, addr: str) -> "Position":
        """Get a Position by its address."""

        # i, j = _address_to_indices(addr)
        return self.positions[addr[0]][int(addr[1])]

    def get_all_positions(self) -> List["Position"]:
        """Get a flattened list of board positions.

        For a 2D list of positions, use self.position.
        """
        flat_positions = [j for i in self.positions.values() for j in i.values()]
        # filter out non-positions
        flat_positions = [pos for pos in flat_positions if type(pos) is Position]
        return flat_positions

    def get_all_goat_positions(self) -> List["Position"]:
        """Get a list of all Positions on the board that are holding a Goat."""
        return [pos for pos in self.get_all_positions() if pos.is_goat()]

    def get_all_tiger_positions(self) -> List["Position"]:
        """Get a list of all Positions on the board that are holding a Tiger."""
        return [pos for pos in self.get_all_positions() if pos.is_tiger()]

    def get_all_empty_positions(self) -> List["Position"]:
        return [pos for pos in self.get_all_positions() if pos.is_empty()]

    def get_all_tigers(self) -> List[Tiger]:
        """Get a list of all Tigers on the board."""
        tiger_positions = self.get_all_tiger_positions()
        return cast(List[Tiger], [pos.piece for pos in tiger_positions])

    def get_all_goats(self) -> List[Goat]:
        """Get a list of all Goats on the board."""
        goat_positions = self.get_all_goat_positions()
        return cast(List[Goat], [pos.piece for pos in goat_positions])

    def get_all_addresses(self) -> List[str]:
        return address.possible_pos

    def get_piece(self, addr: str) -> Optional["Piece"]:
        """Get the Piece at a position.

        If there is no piece at the given position, then None
        is returned.
        """
        piece = self.get_pos(addr).piece
        if isinstance(piece, Piece):
            return piece
        else:
            return None

    def get_tiger_possible_moves(self) -> List:
        """
        Get all the possible moves the tigers can make.

        Does not include placing new tigers.

        Moves are returned as a list of tuples, where
        each tuple has the starting address and end address.
        """
        moves = []
        for pos in self.get_all_positions():
            if pos.is_tiger():
                addr_from = pos.address
                for addr_to in pos.piece.get_valid_moves():
                    moves.append((addr_from, addr_to))

        return moves

    def get_tiger_capturing_moves(self) -> List[tuple]:
        """
        Get all the capturing moves the tigers can make.

        Returns a list of tuples of tiger landing positions and goat positions.
        """
        tuples: List[tuple] = []
        for pos in self.get_all_tiger_positions():
            for landing_pos, goat_pos in pos.piece._get_capturing_positions():
                tuples.append((landing_pos, goat_pos))

        return tuples

    def get_goat_possible_moves(self) -> List:
        """
        Get all the possible moves the tigers can make.

        Does not include placing new tigers.

        Moves are returned as a list of tuples, where
        each tuple has the starting address and end address.
        """
        moves = []
        for pos in self.get_all_positions():
            if pos.is_goat():
                addr_from = pos.address
                for addr_to in pos.piece.get_valid_moves():
                    moves.append((addr_from, addr_to))

        return moves

    @property
    def num_moves(self) -> int:
        return len(self.move_history)

    @property
    def last_move(self) -> str:
        """Return the notation of the last move that was made."""
        return self.move_history[-1][0]

    def is_pos_safe(self, addr: str) -> bool:
        """Checks if a goat in this position could be captured."""
        for tiger_pos in self.get_all_tiger_positions():
            if tiger_pos.piece.can_capture_pos(addr):
                return False

        return True

    def is_pos_blocking(self, addr: str) -> bool:
        """Checks if a goat in this position blocks the movement
        of a tiger."""
        for tiger_pos in self.get_all_tiger_positions():
            if tiger_pos.is_adjacent(self.get_pos(addr)):
                return True

        return False

    def _push_move(self, notation: str):
        """Push the move to the end of the move history."""
        # copy the state of the board
        self.positions_copy = self.copy_board()
        # push it to the end of the move history
        self.move_history.append((notation, self.positions_copy))

    def undo_move(self, n=1):
        """Restore a previous state of the board by n amount of moves."""
        self.state = self.move_history[-n - 1]
        self.positions = self.copy_board(self.state[1])
        # delete all moves between the current state and the restored state
        del self.move_history[-n:]

    def place_tiger(self, addr: str) -> bool:
        """Place a Tiger at the position by its address.
        Returns true if the move was successful."""
        try:
            self.get_pos(addr).place_tiger()
            self._push_move(f"T{addr}")
            return True
        except Exception:
            return False

    def place_goat(self, addr: str) -> bool:
        """Place a Goat at the position by its address.
        Returns true if the move was successful."""
        try:
            self.get_pos(addr).place_goat()
            if len(self.get_all_goat_positions()) >= 15:
                self.is_all_goats_placed = True
            self._push_move(f"G{addr}")
            return True
        except Exception:
            return False

    def move_piece(self, addr_from: str, addr_to: str) -> bool:
        """Move a piece between two positions by its address.
        Returns true if the move was successful."""

        pos_from = self.get_pos(addr_from)
        pos_to = self.get_pos(addr_to)
        piece = pos_from.piece

        if isinstance(piece, Piece):
            res = piece.move(pos_to)
            # print(f"moved {piece} from {addr_from} to {addr_to}")
            if res:
                self._push_move(res)
                return True
        return False

    def clear_pos(self, addr: str):
        """Clear the position by its address."""
        self.get_pos(addr).clear()


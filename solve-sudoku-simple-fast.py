"""
MRV + Forward Checking + Bitmasks (Fast & Simple)
 
MRV: Picks the empty cell with the fewest candidates first.
Forward checking: After any placement, fail early if any empty cell has no candidates left.
Bitmasks: O(1) checks for row/col/box usage.
"""


from typing import List, Tuple

def print_grid(grid: List[List[int]]) -> None:
    """Nicely print a 9x9 Sudoku grid."""
    for r in range(9):
        row = []
        for c in range(9):
            v = grid[r][c]
            row.append(str(v) if v != 0 else ".")
        print(" ".join(row))
    print()

def solve_sudoku_mrv_bitmask(grid: List[List[int]]) -> bool:
    """
    Solve Sudoku in-place using:
      - MRV (Minimum Remaining Values) cell selection
      - Forward checking
      - Bitmask constraints for rows/columns/boxes

    Returns:
        True if a solution is found and written into 'grid', else False.
    """
  
    # Constants & helpers
    FULL_MASK = (1 << 9) - 1  # 0b1_1111_1111 (bits 0..8 represent digits 1..9)

    def box_index(r: int, c: int) -> int:
        return (r // 3) * 3 + (c // 3)

    def bit(d: int) -> int:
        """Bit mask for digit d (1..9)."""
        return 1 << (d - 1)

    def candidates_mask(r: int, c: int) -> int:
        """Return a bitmask of feasible digits at (r, c)."""
        used = row_masks[r] | col_masks[c] | box_masks[box_index(r, c)]
        return (~used) & FULL_MASK

    def select_cell_mrv() -> Tuple[int, int, int, int]:
        """
        Pick the empty cell with the fewest candidates (MRV).
        Returns (r, c, mask, count).
        If no empties remain, returns (None, None, None, None).
        If a cell has 0 candidates, returns it with mask=0, count=0 to force backtrack.
        """
        best = (None, None, None, None)
        best_count = 10  # larger than any possible candidate count (<=9)

        for (rr, cc) in empties:
            if grid[rr][cc] != 0:
                continue
            mask = candidates_mask(rr, cc)
            cnt = mask.bit_count()
            if cnt == 0:
                return rr, cc, mask, cnt
            if cnt < best_count:
                best = (rr, cc, mask, cnt)
                best_count = cnt
                if cnt == 1:
                    break
        return best

    # Initialize masks
    row_masks = [0] * 9
    col_masks = [0] * 9
    box_masks = [0] * 9

    # Fill masks from givens and validate
    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            if v == 0:
                continue
            b = box_index(r, c)
            m = bit(v)
            if (row_masks[r] | col_masks[c] | box_masks[b]) & m:
                # Conflict in givens
                return False
            row_masks[r] |= m
            col_masks[c] |= m
            box_masks[b] |= m

    # Prepare a list of empty cells (we'll check their values from grid each time)
    empties = [(r, c) for r in range(9) for c in range(9) if grid[r][c] == 0]

    # Optional: pre-check that every empty cell has at least one candidate
    for (r, c) in empties:
        if candidates_mask(r, c) == 0:
            return False

    # Backtracking with MRV + forward checking
    def dfs() -> bool:
        # Select the next cell via MRV
        r, c, mask, cnt = select_cell_mrv()
        if r is None:
            # No empties left → solved
            return True
        if cnt == 0:
            # Dead end
            return False

        b = box_index(r, c)

        # Value ordering: Least Constraining Value (optional heuristic)
        # Compute "cost" for each candidate = number of peers that would lose this candidate.
        # We'll derive candidate list (bit, cost) and sort by cost ascending.
        cand_list = []
        tmp = mask
        while tmp:
            one = tmp & -tmp
            d = one.bit_length()  # since one = 1 << (d-1), bit_length() = d
            cost = 0

            # Row peers
            for cc in range(9):
                if cc == c or grid[r][cc] != 0:
                    continue
                if candidates_mask(r, cc) & one:
                    cost += 1
            # Column peers
            for rr in range(9):
                if rr == r or grid[rr][c] != 0:
                    continue
                if candidates_mask(rr, c) & one:
                    cost += 1
            # Box peers
            br, bc = (r // 3) * 3, (c // 3) * 3
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    if (rr == r and cc == c) or grid[rr][cc] != 0:
                        continue
                    if candidates_mask(rr, cc) & one:
                        cost += 1

            cand_list.append((cost, one))
            tmp &= tmp - 1

        cand_list.sort(key=lambda t: t[0])  # least constraining first

        for _, one in cand_list:
            d = one.bit_length()
            # Place digit
            grid[r][c] = d
            row_masks[r] |= one
            col_masks[c] |= one
            box_masks[b] |= one

            # Forward check: ensure no remaining empty cell has zero candidates
            ok = True
            for (rr, cc) in empties:
                if grid[rr][cc] == 0:
                    if candidates_mask(rr, cc) == 0:
                        ok = False
                        break

            if ok and dfs():
                return True

            # Undo placement
            grid[r][c] = 0
            row_masks[r] &= ~one
            col_masks[c] &= ~one
            box_masks[b] &= ~one

        return False

    return dfs()

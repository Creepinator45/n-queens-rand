from random import shuffle
from itertools import chain

def init_queens(size: int) -> list[int]:
    """
        Initialize a random arrangement of n-queens.
    """
    queen = list(range(size))
    shuffle(queen)
    return queen

def compute_collisions(queen: list[int],dn: list[int],dp list[int])->int:
    """
        Initialize dn and dp, and return number of collisions.
        queen should be a list with len=size.
        dn & dp should be list of 0s with len=2*size -1.
    """
    size = len(queen)
    # count queens on positive diagonals 
    # using zip(range) instead of enumerate to maintain symmetry with negative diagonals
    for (row_index, col_index) in  enumerate(queen):
        # queens that share a negative diagonal have the same sum
        sum = row_index + col_index
        dn[sum] += 1
        # queens that share a positive diagonal have the same difference
        # offset to give positive indices
        offset_dif = row_index-col_index + size-1
        dp[offset_dif] += 1
    # count total collisions
    collisions = 0
    for diagonal in dn + dp:
        if diagonal >= 2:
            collisions += diagonal-1
    return collisions

def compute_attacks(queen: list[int], dn: list[int], np: list[int], attack: list[int]) -> int:
    """
        Initialize attack, and return number of queens under attack.
    """
    pass    

def queen_search2(queen: list[int], C1 = 0.45, C2 = 32) -> list[int]:
    """
        Search for a valid arrangement of queens.
        Algorithm based on https://doi.org/10.1109/21.135698.
        Takes a random starting arrangment of queens, returns valid solution to the n-queens problem.
    """
    size = len(queen)
    # initialization
    dn = [0]*(size*2-1)
    dp = [0]*(size*2-1)
    attack = []
    collisions = compute_collisions(queen, dn, dp)
    print(f"dn: {dn}")
    print(f"dp: {dp}")
    print(f"collisions: {collisions}")
    limit = C1*collisions
    #number_of_attacks = compute_attacks(queen, dn, np, attack)

def main():
    queen = init_queens(8)
    print(queen)
    queen_search2(queen)

if __name__ == "__main__":
    main()

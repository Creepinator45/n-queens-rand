from random import shuffle
from itertools import chain

def init_queens(size: int) -> list[int]:
    queen = list(range(size))
    shuffle(queen)
    return queen

def compute_collisions(queen,dn,dp)->int:
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

def compute_attacks(queen, dn, np, attack) -> int:
    pass    

def queen_search2(queen, C1 = 0.45, C2 = 32):
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

import graycode


test_value = 500
i = test_value


def find_one_bit_distances(input_number):
    nums = []

    stringified = f"{graycode.tc_to_gray_code(input_number):>09b}"
    for idx, char in enumerate(stringified):
        # print(f">> flipping big no {idx:>2}")
        replacement = "1" if char == "0" else "0"
        new_str = stringified[:idx] + replacement + stringified[idx + 1 :]

        nums.append(graycode.gray_code_to_tc(int(new_str, base=2)))

    return nums


all_distances = []
for j in range(512):
    nums = find_one_bit_distances(j)
    dists = [j - num for num in nums]
    all_distances += dists

    print(80 * "*")
    print(f"{j:>3} - {graycode.tc_to_gray_code(j):>09b}")
    print(nums)
    print(dists)


print(len(all_distances))

import statistics


print(statistics.mean(all_distances))

print(statistics.median(all_distances))


import math

all_distances = [abs(val) for val in all_distances]


print(statistics.mean(all_distances))

print(statistics.median(all_distances))

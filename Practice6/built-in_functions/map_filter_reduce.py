from functools import reduce

nums = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x**2, nums))
print("Squares:", squares)

even = list(filter(lambda x: x % 2 == 0, nums))
print("Even:", even)

sum_all = reduce(lambda a, b: a + b, nums)
print("Sum:", sum_all)
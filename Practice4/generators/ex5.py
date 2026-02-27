def reverse_gen(n):
    for i in range(n,-1,-1):
        yield i
n=int(input())
for num in reverse_gen(n):
    print(num)
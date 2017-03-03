mass = range(1, 100)
# new_list = [x ** 3 for x in mass if not (x % 3 or x % 4)]
# Если делится на 3 и 4 без остатка, то делится без остатка на произведение этих чисел
new_list = [x ** 3 for x in mass if not (x % (3 * 4))]
print(new_list)

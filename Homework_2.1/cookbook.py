def read_cookbook(cookbook_filename):
	with open(cookbook_filename) as cookbook_file:
		# по сути в одну строку just for fun
		cookbook = {
			line.strip(): [
				dict(zip(['product','quantity','unit'], cookbook_file.readline().strip().split(' | '))) for _ in range(int(cookbook_file.readline()))
			]
			for line in cookbook_file if line.strip()
		}
	return cookbook

def get_menu(cookbook):
	menu = []
	dishes = [dish.strip() for dish in input('Составьте меню. Введите названия блюд через запятую: ').split(',')]
	for dish in dishes:
		if cookbook.get(dish.capitalize()):
			menu.append(cookbook[dish.capitalize()])
		else:
			print('Блюдо "%s" отсутствует в кулинарной книге. Исключено из меню.' % dish)
	return menu

def get_shop_list_by_menu(menu, people_count):
	shop_list = {}
	for dish in menu:
		for ingridient in dish:
			ingridient['quantity'] = int(ingridient['quantity']) * people_count
			if ingridient['product'] in shop_list:
				shop_list[ingridient['product']]['quantity'] += ingridient['quantity']
			else:
				shop_list[ingridient['product']] = ingridient
	return shop_list

def print_shop_list(shop_list):
	print('Список покупок для составленного меню:')
	for key, shop_list_item in shop_list.items():
		print('{product} {quantity} {unit}'.format(**shop_list_item))

def create_shop_list():
	menu = get_menu(read_cookbook('cookbook.txt'))
	people_count = int(input('Сколько человек нужно накормить? '))
	shop_list = get_shop_list_by_menu(menu, people_count)
	print_shop_list(shop_list)

def print_cookbook():
	cookbook = read_cookbook('cookbook.txt')
	print('Кулинарная книга:')
	for key, cookbook_item in cookbook.items():
		print(key)
		print("".join(list(('{product} {quantity} {unit}\n'.format(**ingridient) for ingridient in cookbook_item))))

while True:
	user_input = input('Выберите действие:\n1 - Вывести кулинарную книгу.\n2 - Составить меню и список покупок.\n0 - Выход\n=> ')
	if user_input == '1':
		print_cookbook()
	elif user_input == '2':
		create_shop_list()
	elif user_input == '0':
		break
	else:
		print('\nОшибка ввода, попробуйте еще раз.')
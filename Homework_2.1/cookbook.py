import json
import yaml

# для генерации файла json
def dump_json (jsonfilename = 'cookbook.json'):
	with open(jsonfilename, 'w', encoding='utf-8') as f:
		txtcookbook = read_cookbook('cookbook.txt')
		jsoncookbook = json.dump(txtcookbook, f)

# для генерации файла yaml
def dump_yaml (yamlfilename = 'cookbook.yaml'):
	with open(yamlfilename, 'w', encoding='utf-8') as f:
		txtcookbook = read_cookbook('cookbook.json')
		yamlcookbook = yaml.dump(txtcookbook, f)

# чтение файла с книгой рецептов, любой формат - txt, json, yaml
def read_cookbook(cookbook_filename):
	with open(cookbook_filename) as cookbook_file:
		if cookbook_filename.split('.')[-1] == 'txt':
			cookbook = {
				line.strip(): [
					dict(zip(['product','quantity','unit'], cookbook_file.readline().strip().split(' | '))) for _ in range(int(cookbook_file.readline()))
				]
				for line in cookbook_file if line.strip()
			}
		elif cookbook_filename.split('.')[-1] == 'json':
			cookbook = json.load(cookbook_file)
		elif cookbook_filename.split('.')[-1] == 'yaml':
			cookbook = yaml.load(cookbook_file) 
	return cookbook

def get_menu(cookbook):
	menu = {}
	dishes = [dish.strip() for dish in input('Составьте меню. Введите названия блюд через запятую: ').split(',')]
	for dish in dishes:
		if cookbook.get(dish.capitalize()):
			menu[dish.capitalize()] = cookbook[dish.capitalize()]
		else:
			print('Блюдо "%s" отсутствует в кулинарной книге. Исключено из меню.' % dish)	
	print('Будем готовить:',', '.join(list(dishname for dishname in menu)))
	return menu

def get_shop_list_by_menu(menu, people_count):
	shop_list = {}
	for name, dish in menu.items():
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
	menu = get_menu(read_cookbook('cookbook.yaml'))
	people_count = int(input('Сколько человек нужно накормить? '))
	shop_list = get_shop_list_by_menu(menu, people_count)
	print_shop_list(shop_list)

def print_cookbook():
	cookbook = read_cookbook('cookbook.yaml')
	print('Кулинарная книга:')
	for key, cookbook_item in cookbook.items():
		print(key)
		print("".join(list(('{product} {quantity} {unit}\n'.format(**ingridient) for ingridient in cookbook_item))))

functions = {'1': print_cookbook, '2': create_shop_list, '8': dump_json, '9': dump_yaml}
while True:
	user_input = input('Выберите действие:\n1 - Вывести кулинарную книгу.\n2 - Составить меню и список покупок.\nДля выхода введите любой другой символ.\n=> ')
	functions.get(user_input, exit)()
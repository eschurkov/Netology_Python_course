import glob
import os

def find_files(files_directory):
    program_path = os.path.dirname(os.path.realpath(__file__))
    files_path = os.path.join(program_path, files_directory, '*.sql')
    return glob.glob(files_path)

def check_files(user_string, files):
    iterfiles = files
    files = []
    for file in iterfiles:
        with open(file) as f:
            for line in f:
                if user_string in line:
                    files.append(file)
                    break
    return files

def print_result(files):
    print('Найдено файлов:', len(files))
    if len(files) > 20:
        print('... большой список файлов ... - ', len(files))
    else:
        print(*files, sep='\n')

def find_target_file(directory):
    files = find_files(directory)
    while True:
        user_string = input('Введите строку для поиска: ').strip()
        files = check_files(user_string, files)
        print_result(files)

find_target_file('Advanced Migrations')
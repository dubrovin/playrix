# -*- coding: utf-8 -*-
import csv
import os
import shutil
import string

from multiprocessing import Process
from uuid import uuid4
from random import randrange, choice
from xml.etree.ElementTree import ElementTree, Element, SubElement, fromstring
from zipfile import ZipFile, is_zipfile

# 1. Создает 50 zip-архивов, в каждом 100 xml файлов со случайными данными следующей структуры:
# <root>
#     <var name=’id’ value=’<случайное уникальное строковое значение>’/>
#     <var name=’level’ value=’<случайное число от 1 до 100>’/>
#     <objects>
#         <object name=’<случайное строковое значение>’/>
#         <object name=’<случайное строковое значение>’/>
#         …
#     </objects>
# </root>

# В тэге objects случайное число (от 1 до 10) вложенных тэгов object.

def get_random_word(length):
   return ''.join(choice(string.ascii_lowercase) for i in range(length))

def create_xml_tree():
    root_tag = Element('root')
    id_tag = SubElement(root_tag, 'id')
    id_tag.text = str(uuid4())
    lvl_tag = SubElement(root_tag, 'level')
    lvl_tag.text = str(randrange(1, 101))
    objects_tag = SubElement(root_tag, 'objects')
    objects_list = [
        Element('object', name=str(get_random_word(5)))
        for i in range(0, randrange(1, 11))
    ]
    objects_tag.extend(objects_list)
    tree = ElementTree(root_tag)

    return tree

def generate():
    tmp_dir = 'tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    for i in range(0, 50):
        # create zip
        with ZipFile(''.join([str(i), '.zip']), 'w') as zip_file:
            for j in range(0, 100):
                xml_tree = create_xml_tree()
                xml_file_name = ''.join([str(j), '.xml'])
                xml_file_path = os.path.join(tmp_dir, xml_file_name)
                xml_tree.write(xml_file_path)
                zip_file.write(xml_file_path, xml_file_name)
    shutil.rmtree(tmp_dir)

# 2. Обрабатывает директорию с полученными zip архивами, разбирает вложенные xml файлы и формирует 2 csv файла:
# Первый: id, level - по одной строке на каждый xml файл
# Второй: id, object_name - по отдельной строке для каждого тэга object (получится от 1 до 10 строк на каждый xml файл)

# Очень желательно сделать так, чтобы задание 2 эффективно использовало ресурсы многоядерного процессора.
# Также желательно чтобы программа работала быстро.

def parse_1st_csv(zip_file):
    file_name = ''.join(zip_file.filename.split('.')[0])
    with open(
            ''.join(['1st_', file_name, '.csv']), 'w', newline=''
        ) as csv_file:
        writer = csv.writer(
                csv_file, delimiter=' ',
                quotechar='|', quoting=csv.QUOTE_MINIMAL
        )
        for name in zip_file.namelist():
            xml_tree = fromstring(zip_file.read(name))
            writer.writerow([
                xml_tree.find('id').text,
                xml_tree.find('level').text,
            ])



def parse():
    jobs = []
    for file in os.listdir():
        if is_zipfile(file):
            with ZipFile(file) as zip_file:
                # take file name without extension
                tmp_dir = ''.join(zip_file.file_name.split('.')[0])
                # zip_file.extractall(tmp_dir)
                jobs.append(Process(
                    target=parse_1st_csv,
                    args=(zip_file)
                    ))
                # for name in zip_file.name_list():
                #     xml_file = os.path.join(tmp_dir, name)
                #     xml_tree = parse(xml_file)



                shutil.rmtree(tmp_dir)







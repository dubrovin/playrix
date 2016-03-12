# -*- coding: utf-8 -*-
from csv import QUOTE_MINIMAL, writer as csv_writer
from os import makedirs, path, listdir
from shutil import rmtree
from string import ascii_lowercase
from time import clock

from multiprocessing import Process
from uuid import uuid4
from random import randrange, choice
from xml.etree.ElementTree import ElementTree, Element, SubElement, fromstring
from zipfile import ZipFile, is_zipfile

#first part
def get_random_word(length):
   return ''.join(choice(ascii_lowercase) for i in range(length))

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
    if not path.exists(tmp_dir):
        makedirs(tmp_dir)
    for i in range(0, 50):
        # create zip
        with ZipFile(''.join([str(i), '.zip']), 'w') as zip_file:
            for j in range(0, 100):
                xml_tree = create_xml_tree()
                xml_file_name = ''.join([str(j), '.xml'])
                xml_file_path = path.join(tmp_dir, xml_file_name)
                xml_tree.write(xml_file_path)
                zip_file.write(xml_file_path, xml_file_name)
    rmtree(tmp_dir)

#second part
def parse_1st_csv(zip_file):
    with open('1st.csv', 'a', newline='') as csv_file:
        writer = csv_writer(
                csv_file, delimiter=' ',
                quotechar='|', quoting=QUOTE_MINIMAL
        )
        for name in zip_file.namelist():
            xml_tree = fromstring(zip_file.read(name))
            writer.writerow([
                xml_tree.find('id').text,
                xml_tree.find('level').text,
            ])

def parse_2nd_csv(zip_file):
    with open('2nd.csv', 'a', newline='') as csv_file:
        writer = csv_writer(
                csv_file, delimiter=' ',
                quotechar='|', quoting=QUOTE_MINIMAL
        )
        for name in zip_file.namelist():
            xml_tree = fromstring(zip_file.read(name))
            id_text = xml_tree.find('id').text
            for child in xml_tree.find('objects').getchildren():
                writer.writerow([
                    id_text,
                    child.get('name'),
                ])

def parse():
    jobs = []
    for file in listdir():
        if is_zipfile(file):
            zip_file = ZipFile(file)
            j1 = Process(target=parse_1st_csv, args=(zip_file,))
            j2 = Process(target=parse_2nd_csv, args=(zip_file,))

            jobs.extend([
                j1, j2
            ])

            j1.start()
            j2.start()
    for job in jobs:
        job.join()

if __name__ == '__main__':
    print('starting')
    start = clock()
    generate()
    parse()
    end = clock()
    print('ending \nworking time: ', end - start)





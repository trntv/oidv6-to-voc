'''Python Code to Convert OpenImage Dataset into VOC XML format. 

Author: https://github.com/AtriSaxena
Please see Read me file to know how to use this file.

'''

from xml.etree.ElementTree import Element, SubElement, Comment
import xml.etree.cElementTree as ET
from typing import NamedTuple, Iterable, List
from PIL import Image
import os
from pathlib import Path
import argparse
import csv

parser = argparse.ArgumentParser(
    description='Convert OIDv6 dataset to VOC XML format')
parser.add_argument('annotation',
                    type=str,
                    required=True,
                    nargs='*',
                    help='Annotation file(s), e.g. train-annotations-bbox.csv')
parser.add_argument(
    '--desc',
    type=str,
    required=True,
    help='Class description file, e.g. class-descriptions-boxable.csv')
parser.add_argument('--imgd',
                    type=str,
                    required=True,
                    help='Directory of dataset images')
parser.add_argument('--outd',
                    type=str,
                    default='converted.d',
                    help='Output directory')
args = parser.parse_args()


def parse_csv(csvfile):
    with open(csvfile) as f:
        csvr = csv.reader(f)
    return list(csvr)


desc = dict(parse_csv(args.desc))
outd = Path(args.outd)


class AnnotationRow(NamedTuple):
    imageid: str
    source: str
    labelname: str
    confidence: str
    xmin: str
    xmax: str
    ymin: str
    ymax: str
    isoccluded: str
    istruncated: str
    isgroupof: str
    isdepiction: str
    isinside: str


def convert_annfile(annfile):
    annl = parse_csv(annfile)[1:]
    imageids = [ann[0] for ann in annl]
    imageids = list(set(imageids))
    grouped_anns = map(map_anns_of_image, imageids)
    m = map(get_xml, grouped_anns)
    list(m)  # run get_xml


def map_anns_of_image(imageid: str, ann_list: List[AnnotationRow]):
    filt = lambda row: filter_ann_row(row, imageid)
    return filter(filt, ann_list)


def filter_ann_row(ann_row, imageid):
    return ann_row[0] == imageid


def get_xml(anns_of_image: List[AnnotationRow]):
    imageid = anns_of_image[0][0]
    filename = imageid + '.jpg'
    im = Image.open(filename)
    width, height = im.size

    top = Element('annotation')
    child = SubElement(top, 'folder')
    child.text = 'open_images_volume'

    child_filename = SubElement(top, 'filename')
    child_filename.text = filename

    child_source = SubElement(top, 'source')
    child_database = SubElement(child_source, 'database')
    child_database.text = 'Open Image Dataset v6'
    child_image = SubElement(child_source, 'image')
    child_image.text = anns_of_image[0][1]  # source

    child_size = SubElement(top, 'size')
    child_width = SubElement(child_size, 'width')
    child_width.text = str(width)
    child_height = SubElement(child_size, 'height')
    child_height.text = str(height)
    child_depth = SubElement(child_size, 'depth')
    child_depth.text = '3'

    child_seg = SubElement(top, 'segmented')
    child_seg.text = '0'

    def get_xml_object(ann_row: AnnotationRow):
        child_obj = SubElement(top, 'object')

        child_name = SubElement(child_obj, 'name')
        child_name.text = desc[ann_row[2]]  # labelname
        child_pose = SubElement(child_obj, 'pose')
        child_pose.text = 'Unspecified'
        child_trun = SubElement(child_obj, 'truncated')
        child_trun.text = ann_row[9]  # istruncated
        child_diff = SubElement(child_obj, 'difficult')
        child_diff.text = '0'

        child_bndbox = SubElement(child_obj, 'bndbox')

        child_xmin = SubElement(child_bndbox, 'xmin')
        child_xmin.text = str(int(ann_row[4] * width))  # xmin
        child_ymin = SubElement(child_bndbox, 'ymin')
        child_ymin.text = str(int(ann_row[6] * height))  # ymin
        child_xmax = SubElement(child_bndbox, 'xmax')
        child_xmax.text = str(int(ann_row[5] * width))  # xmax
        child_ymax = SubElement(child_bndbox, 'ymax')
        child_ymax.text = str(int(ann_row[7] * height))  # ymax

    # Iterate for each object in a image.
    m = map(get_xml_object, anns_of_image)
    list(m)

    tree = ET.ElementTree(top)
    save = outd / (imageid + '.xml')
    tree.write(save)

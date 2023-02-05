#!/usr/bin/env python

import collections
import datetime
import glob
import json
import os
import os.path as osp
import sys
import numpy as np
import PIL.Image
import labelme
import shutil

try:
    import pycocotools.mask
except ImportError:
    print('Please install pycocotools:\n\n    pip install pycocotools\n')
    sys.exit(1)


def main():
    sets = ['train2017','val2017','test2017']
    output_dir = './annotations'
    if osp.exists(output_dir):
        print('Output directory already exists:', output_dir)
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    print('Creating dataset:', output_dir)
    for set in sets:
        input_dir = './labelme/%s'%(set)
        filename = 'instances_%s'%(set)
        now = datetime.datetime.now()
        data = dict(
            info=dict(
                description=None,
                version=None,
                contributor=None,
                date_created=now.strftime('%Y-%m-%d %H:%M:%S.%f'),
            ),
            licenses=[dict(
                id=0,
                name=None,
            )],
            images=[
                # license, url, file_name, height, width, date_captured, id
            ],
            type='instances',
            annotations=[
                # segmentation, area, iscrowd, image_id, bbox, category_id, id
            ],
            categories=[
                # supercategory, id, name
            ],
        )

        class_name_to_id = {}
        for i, line in enumerate(open('labels.txt').readlines()):
            class_id = i - 1  # starts with -1
            class_name = line.strip()
            if class_id == -1:
                assert class_name == '__ignore__'
                continue
            class_name_to_id[class_name] = class_id
            data['categories'].append(dict(
                supercategory=None,
                id=class_id,
                name=class_name,
            ))
        out_ann_file = osp.join(output_dir,  filename+'.json')
        label_files = glob.glob(osp.join(input_dir, '*.json'))
        for image_id, label_file in enumerate(label_files):
            with open(label_file) as f:
                label_data = json.load(f)
            path=label_data['imagePath'].split("/") # 可能因为windows或ubuntu不同的系统用\\或/划分,详见前言三
            img_file = './%s/'%(set) + path[-1]
            img = np.asarray(PIL.Image.open(img_file))
            data['images'].append(dict(
                license=0,
                url=None,
                file_name=label_file.split('/')[-1].split('.')[0] + '.jpg',
                height=img.shape[0],
                width=img.shape[1],
                date_captured=None,
                id=image_id,
            ))
            masks = {}                                     # for area
            segmentations = collections.defaultdict(list)  # for segmentation
            for shape in label_data['shapes']:
                points = shape['points']
                label = shape['label']
                shape_type = shape.get('shape_type', None)
                mask = labelme.utils.shape_to_mask(
                    img.shape[:2], points, shape_type
                )

                if label in masks:
                    masks[label] = masks[label] | mask
                else:
                    masks[label] = mask

                points = np.asarray(points).flatten().tolist()
                segmentations[label].append(points)

            for label, mask in masks.items():
                cls_name = label.split('-')[0]
                if cls_name not in class_name_to_id:
                    continue
                cls_id = class_name_to_id[cls_name]

                mask = np.asfortranarray(mask.astype(np.uint8))
                mask = pycocotools.mask.encode(mask)
                area = float(pycocotools.mask.area(mask))
                bbox = pycocotools.mask.toBbox(mask).flatten().tolist()

                data['annotations'].append(dict(
                    id=len(data['annotations']),
                    image_id=image_id,
                    category_id=cls_id,
                    segmentation=segmentations[label],
                    area=area,
                    bbox=bbox,
                    iscrowd=0,
                ))

        with open(out_ann_file, 'w') as f:
            json.dump(data, f,indent=4)
        print(set + ' is done')


if __name__ == '__main__':
    main()




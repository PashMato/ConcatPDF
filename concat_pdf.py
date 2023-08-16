#!usr/bin/env python3

import os

import numpy as np
from fpdf import FPDF
from matplotlib import pyplot as plt

import argparse


def CreatePDF(input_dir: str, out_name: str, read_formats: tuple[str] = ("png", "jpeg"), w: int = 600, img_list=None):
    dir_path = os.path.expanduser(input_dir)

    all_img_paths = []
    if img_list is None:
        for file_name in os.listdir(dir_path):
            if file_name.split('.')[-1].lower() in read_formats:
                all_img_paths.append(f"{dir_path}/{file_name}")

        all_img_paths.sort()
    else:
        all_img_paths = img_list
    pdf = FPDF()  # open a new pdf

    for img_path in all_img_paths:
        size = np.array(plt.imread(img_path).T.shape[1:]) / 3
        size = (w * (size / size[0])).astype(int)
        pdf.add_page(format=tuple(size))
        pdf.image(img_path, x=0, y=0, w=size[0], h=size[1], keep_aspect_ratio=True)

    pdf.output(f"{dir_path}/{out_name}")  # Save Result


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, help="The Input dir")
    parser.add_argument('-w', '--write', type=str, help="Where to save the result")
    parser.add_argument("--read_formats", nargs="*", type=str, help="What formats to read from",
                        default=("png", "jpeg"))
    parser.add_argument('--width', type=int, help="The constant width of the pdf", default=600)
    parser.add_argument('--img_list', nargs="*", type=str, default=None,
                        help="the list of images (by order) by default reads from (--dir or -d)")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if None in (args.dir, args.write, args.read_formats):
        print("Run with -h or --help to get help")
        exit(0)

    CreatePDF(args.dir, args.write, read_formats=args.read_formats, w=args.width, img_list=args.img_list)


if __name__ == '__main__':
    main()

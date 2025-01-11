#!usr/bin/env python3

import os

import numpy as np
from IPython.core.page import page_dumb
from PyPDF2 import PdfMerger
from fpdf import FPDF

from matplotlib import pyplot as plt

import argparse


def CreatePDF(input_dir: str, out_name: str, read_formats: tuple[str] = ("png", "jpeg", "jpg"), w: int = 600, img_list=None, fit_into_page: bool = False) -> None:
    """
    A function that gets a directory name and extracts all the images to one PDF,
    she does so by creating a temporary folder with a pdf for each image and then merging them
    (not deleting the temp content if it exits beforehand).
    :param input_dir: the input dir name
    :param out_name: the output file name (saved in the input dir)
    :param read_formats: the read formats by (default png and jpg)
    :param w: the constant width of the PDF
    :param img_list: the list of images (by order) if None reads from input_dir else uses this list
    :param fit_into_page: fits the images into the page (constant ratio of [x, x * sqrt(2)])
    """

    dir_path = os.path.expanduser(input_dir)

    # extracting all the images we work on
    all_img_paths = []
    if img_list is None:
        for file_name in os.listdir(dir_path):
            if file_name.split('.')[-1].lower() in read_formats:
                all_img_paths.append(f"{dir_path}/{file_name}")

        all_img_paths.sort()
    else:
        all_img_paths = img_list

    # create the tmp file
    is_dir = os.path.isdir(f"{dir_path}/temp")
    os.makedirs(f"{dir_path}/temp", exist_ok=True)

    all_pdf_paths = []  # each image has its own pdf then they are merged
    for i, img_path in enumerate(all_img_paths):
        pdf = FPDF()  # open a new pdf
        img_size = np.array(plt.imread(img_path).T.shape[1:])  # read the image size from the image

        if fit_into_page:  # if we want constant width and height
            page_size = np.array([w, np.sqrt(2) * w])

            r = img_size / page_size  # r for ratio

            # fit the image in max size in the page (constant ratio)
            img_page_size = (img_size / img_size[r == np.max(r)] * page_size[r == np.max(r)]).astype(int)
            x, y = ((page_size - img_page_size) / 2).astype(int)  # center the image
            w, h = img_page_size
        else:  # if we want constant width but dynamic height
            page_size = (w * (img_size / img_size[0])).astype(int)
            x = y = 0
            w, h = page_size

        print(f"Page size: {w, h}, Image: '{img_path}'")

        # change the pdf size accordingly
        pdf.w, pdf.h = page_size
        pdf.k = 72.0 / 25.4  # the unit (inches)
        pdf.fw_pt, pdf.fh_pt = page_size * pdf.k

        pdf.add_page()
        pdf.image(img_path, x=x, y=y, w=w, h=h)

        all_pdf_paths.append(f"{dir_path}/temp/p{i}.pdf")
        pdf.output(f"{dir_path}/temp/p{i}.pdf")  # Save Result

    # Merge all the PDFs
    merger = PdfMerger()
    for filename in all_pdf_paths:
        merger.append(filename)

    # Save the final merged PDF
    merger.write(f"{dir_path}/{out_name}")
    merger.close()

    # removing all traces
    for filename in all_pdf_paths:
        os.remove(filename)

    if not is_dir:
        os.rmdir(f"{dir_path}/temp")


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, help="The Input dir")
    parser.add_argument('-o', '--file_out', type=str, help="What is The name of your output file")
    parser.add_argument('-f', '--fit', default=False,
                        help="fits the images into the page (constant ratio of [x, x * sqrt(2)])", action="store_true")
    parser.add_argument("--read_formats", nargs="*", type=str, help="What formats to read from",
                        default=("png", "jpeg", "jpg"))
    parser.add_argument('--width', type=int, help="The constant width of the pdf", default=600)
    parser.add_argument('--img_list', nargs="*", type=str, default=None,
                        help="the list of images (by order) by default reads from (--dir or -d)")

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if None in (args.dir, args.file_out, args.read_formats):
        print("Run with -h or --help to get help")
        exit(0)

    CreatePDF(args.dir, args.file_out, read_formats=args.read_formats, w=args.width, img_list=args.img_list, fit_into_page=args.fit)


if __name__ == '__main__':
    main()

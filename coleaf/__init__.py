#!/usr/bin/env python
import click
import os.path as op
import sys
import rawpy
import matplotlib.pyplot as plt
import imageio
import cv2 as cv

from . base import findByDepth

__author__ = ("Mengwei Jiang")
__copyright__ = "Copyright (c) 2022, Mengwei Jiang"
__email__ = "mengmengjiang.1105@gmail.com"
__status__ = "Development"
__version__ = "0.0.2"


@click.version_option(__version__, "-V", "--version")
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    pass 

from . import prepare as _prepare

@cli.command()
@click.argument(
    'image_path',

)
@click.option(
    '-c', '--crop',
    default=False,
    is_flag=True,
    help="crop the paper from backgroud.",
    show_default=True,
)
@click.option(
    '-g', '--height',
    default=21,
    type=float,
    help="the width of the background paper when cropped(cm).",
    show_default=True,
)
@click.option(
    '-l', '--length',
    default=29.7,
    type=float,
    help="the length of the background paper when cropped(cm).",
    show_default=True,
)
@click.option(
    '-r', '--remove_reflections',
    default=False,
    is_flag=True,
    help="remove the reflection on the glass.",
    show_default=True
)
@click.option(
    '-o', '--outdir',
    default=None,
    help="directory of output, default output into input pathway.",
    metavar="PATH"
)
def prepare(image_path, crop, height, length, remove_reflections, outdir):
    """
    Prepare the image or the folder with images.

    IMAGE_PATH: Path to the image or the folder with some images.

    When using a folder as input, do not add the -n option. 
    """
    if op.isdir(image_path):
        image_paths = findByDepth(image_path, suffix=['dng','jpg'])
        image_paths = filter(lambda x: not x.endswith(("_t.jpg", "_c.jpg", "_p.jpg", "_o.jpg")), image_paths)
        #print(list(image_paths))
        for p in image_paths:
            print(p)
            if p.endswith(".dng"):
                with rawpy.imread(p) as raw:
                    rgb = raw.postprocess()
                    raw_name = p.split(".")[0]
                    imageio.imwrite(raw_name+".jpg", rgb)
                    _prepare.main(raw_name+".jpg", crop, height, length, remove_reflections, outdir)
            else:
                _prepare.main(p, crop, height, length, remove_reflections, outdir)
    else:
        _prepare.main(image_path, crop, height, length, remove_reflections, outdir)
    #print (image_paths)
from . import leafarea as _leafarea

@cli.command()
@click.argument(
    'image_path',
)
@click.option(
    '-t', '--img_type',
    default="photo",
    help="the type of picture."
        "The original image taken with the <photo> parameter."
        "The memo scans pictures with <scanned> parameter",
    show_default=True,
    metavar="pthoto/scanned"
)
@click.option(
    '-g', '--height',
    default=21,
    type=float,
    help="the width of the background paper (cm).",
    show_default=True,
)
@click.option(
    '-l', '--length',
    default=29.7,
    type=float,
    help="the length of the background paper (cm).",
    show_default=True,
)
@click.option(
    '-n', '--name',
    default=None,
    type=str,
    help="sample name,default name is the picture name, "
        "no '_' or '.' in name. "
        "If you have already performed a prepare operation, "
        "the default is <sample name_operation name>. ",
)
@click.option(
    '-o', '--outdir',
    default=None,
    help="directory of output, defalut output into input pathway. ",
    metavar="PATH",
)
def leafarea(image_path, img_type, height, length, name, outdir):
    """
    Calculate the leaf erea.

    IMAGE_PATH: Path to the image or the folder with some images.

    When using a folder as input, do not add the -n option.
    """
    if op.isdir(image_path):
        image_paths = findByDepth(image_path, suffix=['jpg', 'dng'])
        
        image_paths = filter(lambda x: not x.endswith("_o.jpg"),image_paths)
        for p in image_paths:
            print(p)
            if p.endswith(".dng"):
                with rawpy.imread(p) as raw:
                    rgb = raw.postprocess()
                    raw_name = p.split(".")[0]
                    imageio.imwrite(raw_name+".jpg", rgb)
                    _leafarea.main(raw_name+".jpg", img_type, height, length, name, outdir)
            else:
                _leafarea.main(p, img_type, height, length, name, outdir)
    else:
        _leafarea.main(image_path, img_type, height, length, name, outdir)


from . import trichomes as _trichomes

@cli.command()
@click.argument(
    'image_path',
)
@click.option(
    '-n', '--name',
    default=None,
    type=str,
    help="sample name,default name is the picture name, "
        "no '_' or '.' in name. "
)
@click.option(
    '-o', '--outdir',
    default=None,
    help="directory of output, defalut output into input pathway. ",
    metavar="PATH",
)
def trichomes(image_path, name, outdir):
    """
    Count the number of trichomes on the leaves.

    IMAGE_PATH: Path to the image or the folder with some images.

    When using a folder as input, do not add the -n option,and need "> output.txt".
    """
    if op.isdir(image_path):
        image_paths = findByDepth(image_path, suffix=['tif'])
        image_paths = filter(lambda x: not x.endswith("_t.tif"), image_paths)

        for p in image_paths:
            print(p, end='\t', file=sys.stdout)
            _trichomes.main(p, name, outdir)
    else:
        _trichomes.main(image_path, name, outdir)
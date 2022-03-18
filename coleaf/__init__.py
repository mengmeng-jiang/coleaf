
import click

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
def prepare(image_path, crop, remove_reflections, outdir):
    _prepare.main(image_path, crop, remove_reflections, outdir)

import os
import click
from glob import glob
import itertools
import zlib


def crc32(fileName):
    with open(fileName, 'rb') as fh:
        hash = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            hash = zlib.crc32(s, hash)
        return "%08X" % (hash & 0xFFFFFFFF)


@click.command()
@click.argument("pattern", required=False, default="*.*")
def cli(pattern):

    files = glob(pattern)

    hash_list = [{"filename": i, "hash": crc32(i)} for i in files]

    grouped = itertools.groupby(hash_list, lambda x: x['hash'])

    to_delete_list = []

    for _, group in grouped:
        group = [x['filename'] for x in group]
        if len(group) == 1:
            continue

        click.echo('-'*20)
        min_index, _ = min(enumerate(group), key=lambda x: os.path.getmtime(x[1]))

        for idx, value in enumerate(group):
            if idx == min_index:
                click.echo(f"{' '*6} {value}")
            else:
                click.secho('DELETE', fg='red', nl=False)
                click.echo(f" {value}")
                to_delete_list.append(value)

    if not to_delete_list:
        click.echo('no duplicate files found.')
        return

    if click.confirm('\nDo you want to continue?', default=False):
        for i in to_delete_list:
            click.echo(f'deleting {i}')
            os.remove(i)


if __name__ == "__main__":
    cli()

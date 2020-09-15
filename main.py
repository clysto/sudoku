from json import loads
import os
import click
import requests
import json


def fetch_board():
    r = requests.get("https://sugoku.herokuapp.com/board?difficulty=hard")
    return r.text


def find_next_cell_to_fill(grid, i, j):
    for x in range(i, 9):
        for y in range(j, 9):
            if grid[x][y] == 0:
                return x, y
    for x in range(0, 9):
        for y in range(0, 9):
            if grid[x][y] == 0:
                return x, y
    return -1, -1


def is_valid(grid, i, j, e):
    row_ok = all([e != grid[i][x] for x in range(9)])
    if row_ok:
        column_ok = all([e != grid[x][j] for x in range(9)])
        if column_ok:
            sec_top_x, sec_top_y = 3 * (i // 3), 3 * (j // 3)
            for x in range(sec_top_x, sec_top_x + 3):
                for y in range(sec_top_y, sec_top_y + 3):
                    if grid[x][y] == e:
                        return False
            return True
    return False


def solve_sudoku(grid, i=0, j=0):
    i, j = find_next_cell_to_fill(grid, i, j)
    if i == -1:
        return True
    for e in range(1, 10):
        if is_valid(grid, i, j, e):
            grid[i][j] = e
            if solve_sudoku(grid, i, j):
                return True
            grid[i][j] = 0
    return False


@click.group()
def cli():
    pass


@cli.command()
@click.option("-o", "--output", type=click.File("w"), help="输出结果路径")
@click.argument(
    "file",
    type=click.File("r"),
)
def solve(output, file):
    content = file.read()
    grid = json.loads(content)["board"]
    solve_sudoku(grid)
    if output:
        output.write(json.dumps({"board": grid}, separators=(",", ":")))
    else:
        for row in grid:
            line = " ".join(map(lambda x: str(x), row))
            click.echo(line)


@cli.command()
@click.option(
    "-o", "--output", type=click.Path(writable=True), default="a.txt", help="输出结果路径"
)
@click.option("-n", "--number", type=int, default=1, help="生成个数")
def generate(output, number):
    if number > 1 and not os.path.isdir(output):
        click.echo("-o 应该一个目录路径", err=True)
        return

    if number == 1:
        file = open(output, "w")
        file.write(fetch_board())
        file.close()

    else:
        for i in range(number):
            file = open(os.path.join(output, f"{i}.txt"), "w")
            file.write(fetch_board())
            file.close()


@cli.command()
@click.argument("file", type=click.File("r"))
def show(file):
    content = file.read()
    data = json.loads(content)
    for row in data["board"]:
        line = " ".join(map(lambda x: str(x), row))
        click.echo(line)


@cli.command()
@click.argument("file", type=click.File("r"))
def debug(file):
    click.echo("数独:")
    content = file.read()
    data = json.loads(content)
    for row in data["board"]:
        line = " ".join(map(lambda x: str(x), row))
        click.echo(line)
    click.echo("解:")
    grid = json.loads(content)["board"]
    solve_sudoku(grid)
    for row in grid:
        line = " ".join(map(lambda x: str(x), row))
        click.echo(line)


if __name__ == "__main__":
    cli()

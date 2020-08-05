# coding: utf-8


# TODO ネストレベルに応じて識別子の長さを短くしたい
# TODO ネストレベルに応じてブロックの長さを短くしたい
# TODO if,forがネストしたときに直後に挿入される複数の空行を1つにまとめたい
# TODO ヨーダ記法に対応したい


import argparse
from generator import SampleCodeGenerator


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    code = SampleCodeGenerator().generate_file()
    print(code)


if __name__ == '__main__':
    main()

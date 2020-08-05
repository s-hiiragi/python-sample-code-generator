# coding: utf-8


import argparse
from generator import SampleCodeGenerator


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    code = SampleCodeGenerator().generate_file()
    print(code)


if __name__ == '__main__':
    main()

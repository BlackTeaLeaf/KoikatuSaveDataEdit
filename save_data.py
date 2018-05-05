#!/usr/bin/env python
import argparse
import io
import os
import struct
from pathlib import Path

from character import KoikatuCharacter

CHARA_HEADER = b'\x64\x00\x00\x00\x12\xe3\x80\x90KoiKatuChara\xe3\x80\x91'
CHARA_SEPARATOR = b'\xff' * 8

class KoikatuSaveData:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'rb') as file:
            self._load(file)


    def _load(self, file):
        self.b_unknown01 = file.read(7)
        self.school = self._read_utf8_string(file)

        self.b_unknown02 = file.read(17)

        # split character data
        chara_part = file.read()
        chara_data = chara_part.split(CHARA_HEADER)

        self.characters = []
        for data in chara_data:
            if data:
                chara = KoikatuCharacter(io.BytesIO(CHARA_HEADER + data), False)
                self.characters.append(chara)
                #print(f'chara: {chara.lastname} {chara.firstname} ({chara.nickname})')


    def _read_utf8_string(self, file):
        len_ = struct.unpack('b', file.read(1))[0]
        value = file.read(len_)
        return (value.decode('utf8'), len_)


    def _pack_utf8_string(self, string):
        len_ = struct.pack('b', string[1])
        binary = string[0].encode()
        return len_ + binary


    def replace(self, pos, character):
        self.characters[pos] = character


    def save(self, filename):
        with open(filename, 'wb') as out:
            out.write(self.b_unknown01)
            out.write(self._pack_utf8_string(self.school))
            out.write(self.b_unknown02)
            for chara in self.characters:
                chara.save(out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('save_data')

    args = parser.parse_args()

    # load save data
    save_data = KoikatuSaveData(args.save_data)

    print('school: ', save_data.school[0])

    # extract character data
    outdir = Path('cards')
    if not outdir.exists():
        os.makedirs(outdir)

    for i, chara in enumerate(save_data.characters):
        with open(outdir / f'char_{i:03}.png', 'wb') as pngfile:
            pngfile.write(chara.png)
        with open(outdir / f'char_{i:03}.char.dat', 'wb') as pngfile:
            pngfile.write(chara.chara_data)
        with open(outdir / f'char_{i:03}.additional.dat', 'wb') as pngfile:
            pngfile.write(chara.additional_data)


    # confirm serializing
    save_data.save(args.save_data + '_01.dat')
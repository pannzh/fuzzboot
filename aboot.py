"""
Author: Roee Hay / Aleph Research / HCL Technologies
"""

import json
import hashlib
import os
from serializable import Serializable
from log import *
from config import Config
import utils

bootloaders_by_device = {}
bootloaders_by_oem = {}
bootloaders = None


def get_bootloaders(path=Config.get_config().data_path):
    global bootloaders
    if bootloaders:
        return bootloaders

    bootloaders = []
    n = 0
    for f in os.listdir(path):
        if f.endswith(".json"):
            bl = ABOOT.create_from_json(os.path.join(path, f))
            bootloaders.append(bl)
            if bl.oem not in bootloaders_by_oem:
                bootloaders_by_oem[bl.oem] = []
            bootloaders_by_oem[bl.oem].append(bl)
            if bl.device not in bootloaders_by_device:
                bootloaders_by_device[bl.device] = []
            bootloaders_by_device[bl.device].append(bl)
            n+=1
    D("loaded %d bootloaders (%d devices, %d OEMs)", n, len(bootloaders_by_device), len(bootloaders_by_oem))
    return bootloaders


def by_oem(oem = None):
    all()

    if not oem:
        return bootloaders_by_oem

    try:
        D("bootloader.by_oem[%s]: %s", oem, bootloaders_by_oem[oem])
        return bootloaders_by_oem[oem]
    except KeyError:
        return []


def by_device(device = None):
    all()

    if not device:
        return bootloaders_by_device
    try:
        D("bootloader.by_device[%s]: %s", device, bootloaders_by_device[device])
        return bootloaders_by_device[device]
    except KeyError:
        return []


def all():
    if not bootloaders:
        get_bootloaders()

    return bootloaders


class ABOOT(Serializable):
    @classmethod
    def create_from_json(cls, path):
        data = json.load(open(path, "rb"))
        return ABOOT().set_data(data)

    @classmethod
    def create_from_bootloader_image(cls, fp, oem, device, build, src, name, strprefix=""):
        data = fp.read()
        sha256 = hashlib.sha256(data).hexdigest()
        D("SHA256 = %s", sha256)
        # strings = utils.get_strings(data, strprefix)
        strings = utils.shell_get_strings(fp.name, strprefix)
        return ABOOT().set_data({'src': src,
                                 'name': name,
                                 'sha256': sha256,
                                 'strings': strings,
                                 'oem': oem,
                                 'device': device,
                                 'build': build})

    def __repr__(self):
        return "%s/%s/%s" % (self.oem, self.device, self.build)

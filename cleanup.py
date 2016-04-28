import os
import sys
import hashlib


cleaned_up = 0


class Dupe:
    def __init__(self, path, top_level):
        self.hash = hash_file(path)
        self.path = path
        self.top_level = top_level


class DupeSet:
    dupes = []

    def get_hash(self):
        if len(self.dupes) == 0:
            return ''
        else:
            return self.dupes[0].hash

    def add_dupe(self, dupe):
        self.dupes.append(dupe)

    def delete_dupes(self):
        for dupe in self.dupes:
            if not dupe.top_level:
                os.remove(dupe.path)
                global cleaned_up
                cleaned_up += 1

    def print(self):
        for dupe in self.dupes:
            print(dupe.path)


class DuperDuper:
    dupe_sets = []

    def add_dupe(self, dupe):
        for dupeset in self.dupe_sets:
            if dupeset.get_hash() == dupe.hash:
                dupeset.add_dupe(dupe)
        if len(self.dupe_sets) == 0:
            new_set = DupeSet()
            self.dupe_sets.append(new_set)
            new_set.add_dupe(dupe)

    def delete(self):
        for dupeset in self.dupe_sets:
            # dupeset.delete_dupes()
            dupeset.print()


def hash_file(path):
    file_part = open(path, 'rb').read(1048576)
    hasher = hashlib.md5()
    hasher.update(file_part)
    return hasher.digest()


def build_hash_table(directory):
    duper_duper = DuperDuper()
    for dir_name, sub_dirs, file_list in os.walk(directory):
        for file_name in file_list:
            path = os.path.join(dir_name, file_name)
            if path == directory:
                duper_duper.add_dupe(Dupe(path, True))
            else:
                duper_duper.add_dupe(Dupe(path, False))
    duper_duper.delete()
    print(cleaned_up)

build_hash_table(os.path.expanduser("~\\Desktop\\" + sys.argv[1]))

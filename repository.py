import io
import tarfile
from datetime import datetime, timedelta

import requests


class Repository:
    def __init__(self):
        self.packages = {}
        self.last_update = None
        self.update_threshold = timedelta(hours=12)
        self.name = "arch4edu"
        self.mirror = "https://mirrors.tuna.tsinghua.edu.cn/arch4edu"
        self.arch = ["aarch64", "x86_64"]
        self.session = requests.session()

    def update(self):
        _packages = {}
        for arch in self.arch:
            content = self.session.get(
                f"{self.mirror}/{arch}/{self.name}.db.tar.gz"
            ).content
            content = io.BytesIO(content)
            tar = tarfile.open(fileobj=content, mode="r:gz")
            for member in tar.getmembers():
                if member.isfile():
                    f = tar.extractfile(member)
                    lines = f.read().decode("utf-8").split("\n")
                    arch = lines[lines.index("%ARCH%") + 1]
                    pkgname = lines[lines.index("%NAME%") + 1]
                    version = lines[lines.index("%VERSION%") + 1]
                    key = f"{arch}/{pkgname}"
                    if not key in _packages:
                        _packages[key] = (pkgname, version, arch)
        self.packages = _packages
        self.last_update = datetime.now()

    def search(self, package):
        if (
            self.last_update is None
            or datetime.now() - self.last_update > self.update_threshold
        ):
            self.update()
        result = [i for i in self.packages.values() if i[0] == package]
        return result


if __name__ == "__main__":
    repository = Repository()
    result = repository.search("yay")
    print("\n".join(" ".join(i) for i in result))

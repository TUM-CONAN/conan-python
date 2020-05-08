import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class PythonConan(ConanFile):
    name = "python"
    version = tools.get_env("GIT_TAG", "3.8.2")
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    description = "Next generation of the python high-level scripting language"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@camposs/stable")
        # self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("expat/2.2.5-r2@camposs/stable")
        self.requires("openssl/[>=1.1.1b]")
        self.requires("libffi/3.3@camposs/stable")
        self.requires("zlib/[>=1.2.11]@camposs/stable")
        self.requires("bzip2/1.0.6@camposs/stable")
        self.requires("sqlite3/[>=3.29.0]")

    def source(self):
        tools.get("https://www.python.org/ftp/python/{0}/Python-{0}.tar.xz".format(self.version))

    def build(self):
        args = [
            "--enable-shared",
            "--with-openssl=%s" % self.deps_cpp_info["openssl"].rootpath,
            "--with-computed-gotos",
            "--enable-optimizations",
            "--with-lto",
            "--enable-ipv6",
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-loadable-sqlite-extensions",
            "--without-ensurepip",
        ]
        with tools.chdir("Python-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            env_vars = autotools.vars
            # linux only / osx needs @executable_path / windows a different build system
            # env_vars['LDFLAGS'] = '-Wl,--rpath="%s"' % os.path.join(self.package_folder, "lib")
            autotools.configure(args=args, vars=env_vars)
            autotools.make()
            autotools.install()
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            majmin_ver = ".".join(self.version.split(".")[:2])
            os.symlink("python%s" % majmin_ver, "python")

    def package_info(self):
        self.env_info.PYTHON = os.path.join(self.package_folder, "bin", "python3")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.PYTHONHOME = self.package_folder
        majmin_ver = ".".join(self.version.split(".")[:2])
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python%s" % majmin_ver))

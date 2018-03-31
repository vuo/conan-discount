from conans import ConanFile, tools
import platform

class DiscountConan(ConanFile):
    name = 'discount'

    source_version = '2.1.6'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.pell.portland.or.us/~orc/Code/markdown/'
    license = 'http://www.pell.portland.or.us/~orc/Code/markdown/COPYRIGHT.html'
    description = 'A library for formatting text into HTML'
    source_dir = 'discount-%s' % source_version
    install_dir = '_install'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.9@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.pell.portland.or.us/~orc/Code/markdown/discount-%s.tar.bz2' % self.source_version,
                  sha256='702bb29e17e387f82e40fae062d5e4939bc6fb22dcf53e6109982a5faa110796')

        self.run('mv %s/COPYRIGHT %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        with tools.chdir(self.source_dir):
            flags = '-Oz'

            if platform.system() == 'Darwin':
                flags += ' -mmacosx-version-min=10.10'

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
                'CFLAGS': flags,
            }
            with tools.environment_append(env_vars):
                self.run('./configure.sh --prefix=../%s --shared --enable-all-features' % self.install_dir)
                self.run('make')
                self.run('make install')

        with tools.chdir(self.install_dir):
            if platform.system() == 'Darwin':
                self.run('install_name_tool -id @rpath/libmarkdown.dylib lib/libmarkdown.dylib')
            elif platform.system() == 'Linux':
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libmarkdown.so lib/libmarkdown.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include')
        self.copy('libmarkdown.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['markdown']

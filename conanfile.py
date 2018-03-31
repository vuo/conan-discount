from conans import ConanFile, tools

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

    def source(self):
        tools.get('http://www.pell.portland.or.us/~orc/Code/markdown/discount-%s.tar.bz2' % self.source_version,
                  sha256='702bb29e17e387f82e40fae062d5e4939bc6fb22dcf53e6109982a5faa110796')

    def build(self):
        with tools.chdir(self.source_dir):
            self.run('./configure.sh --prefix=../%s --shared --enable-all-features' % self.install_dir)
            self.run('make')
            self.run('make install')
            self.run('install_name_tool -id @rpath/libmarkdown.dylib ../%s/lib/libmarkdown.dylib' % self.install_dir)

    def package(self):
        self.copy('*.h', src='%s/include' % self.install_dir, dst='include')
        self.copy('*.dylib', src='%s/lib' % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['markdown']

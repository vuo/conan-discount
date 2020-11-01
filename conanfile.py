from conans import ConanFile, CMake, tools
import os
import platform

class DiscountConan(ConanFile):
    name = 'discount'

    source_version = '2.2.6'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://www.pell.portland.or.us/~orc/Code/markdown/'
    license = 'http://www.pell.portland.or.us/~orc/Code/markdown/COPYRIGHT.html'
    description = 'A library for formatting text into HTML'
    source_dir = 'discount-%s' % source_version
    build_dir = '_build'
    install_dir = '_install'
    exports_sources = '*.patch'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('http://www.pell.portland.or.us/~orc/Code/markdown/discount-%s.tar.bz2' % self.source_version,
                  sha256='ae68a4832ff8e620286304ec525c1fe8957be4d8f1e774588eb03d1c3deb74a7')

        tools.patch(patch_file='destructor.patch', base_path=self.source_dir)

        self.run('mv %s/COPYRIGHT %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        cmake = CMake(self)

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER']   = '%s/bin/clang'   % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz'
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
        cmake.definitions['BUILD_STATIC_LIBS'] = 'OFF'

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s/cmake' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

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

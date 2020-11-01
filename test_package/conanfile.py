from conans import ConanFile, CMake
import platform

class DiscountTestConan(ConanFile):
    generators = 'cmake'
    requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy('*', src='bin', dst='bin')
        self.copy('*', dst='lib', src='lib')

    def test(self):
        self.run('./bin/test_package')

        # Ensure we only link to system libraries and our own libraries.
        if platform.system() == 'Darwin':
            self.run('! (otool -L lib/libmarkdown.dylib | grep -v "^lib/" | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
            self.run('! (otool -L lib/libmarkdown.dylib | fgrep "libstdc++")')
            self.run('! (otool -l lib/libmarkdown.dylib | grep -A2 LC_RPATH | cut -d"(" -f1 | grep "\s*path" | egrep -v "^\s*path @(executable|loader)_path")')
        elif platform.system() == 'Linux':
            self.run('! (ldd lib/libmarkdown.so | grep -v "^lib/" | grep "/" | egrep -v "\s(/lib64/|(/usr)?/lib/x86_64-linux-gnu/)")')
            self.run('! (ldd lib/libmarkdown.so | fgrep "libstdc++")')
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

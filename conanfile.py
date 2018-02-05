#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class CPRConan(ConanFile):
    name = "cpr"
    version = "1.2.0"
    url = "https://github.com/whoshuu/cpr.git"
    license = "MIT"
    requires = "libcurl/7.56.1@bincrafters/stable"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "insecure_curl": [True, False],
               "use_ssl": [True, False],
               "use_system_curl": [True, False]}
    default_options = "shared=False", "libcurl:with_ldap=False", "insecure_curl=False", "use_ssl=True", "use_system_curl=False"
    generators = "cmake"
    exports_sources = "*" 

    def config(self):
        if self.options.use_ssl:
            self.options["libcurl"].with_openssl = True
        else:
            self.options["libcurl"].with_openssl = False

        if tools.os_info.is_macos:
            # This is hamfisted, but should work. The problem is that libcurl on OSX doesn't use OpenSSL, but it's own thing.
            # It's also guaranteed to be installed, so that's nice. Anyway, we need to link against the system libcurl on OSX
            # if we are using SSL. So let's just avoid having to build it all together unless specified.
            self.options.use_system_curl = True

    def requirements(self):
        if self.options.use_system_curl:
            if "libcurl" in self.requires:
                del self.requires["libcurl"]

    def build(self):
        cmake = CMake(self)
        cmake.definitions["INSECURE_CURL"] = self.options.insecure_curl
        cmake.definitions["USE_SYSTEM_CURL"] = True # Force CPR to not try to build curl itself from a git submodule
        cmake.definitions["BUILD_CPR_TESTS"] = False # unsure if wholesale disabling this is the right thing to do.
        cmake.definitions["CONAN"] = True # necessary for modifications to the CMakeFiles.txt to work

        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE")
        self.copy("*.h", dst="include", src="include")
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.use_system_curl:
            self.cpp_info.libs.append("curl")


# ==================================================================================================
# Project: 
# Exploring the performance of general matrix-multiplication.
#
# File information:
# Institution.... CPSLAB at KAIST <www.cps.kaist.ac.kr>
# Author......... Jaeyoung Ahn <qiqi67@kaist.ac.kr>
# Changed at..... 2019-10-25
# License........ MIT license
#
# ==================================================================================================

TARGET=x86

# Setting compiler options according to the target achitecture
ifeq ($(TARGET), arm)
	CXX = gcc
else
	ifeq ($(TARGET), x86)
		CXX = arm-starfishmllib32-linux-gnueabi-gcc
	endif
endif

BUILD_OPT = --sysroot=/opt/starfish-sdk-x86_64/5.0.0-20190307/sysroots/ca9v1-starfishmllib32-linux-gnueabi

# Folders
SRCDIR = src
BINDIR = bin
LIBDIR = lib
TESTDIR = test

#CPPSOURCES = shared_memory.c 
#BIN = shared_memory
CPPSOURCES = getGpuUtil_printf.c 
BIN = getGpuUtil_printf
#CPPSOURCES = getGpuUtil.c 
#BIN = getGpuUtil
# ==================================================================================================
# ==================================================================================================
# ==================================================================================================

# All (default target)
all: clean build

# C++ sources
build:
	$(CXX) $(BUILD_OPT) -o $(BIN) $(CPPSOURCES)

# Clean-up
clean:
	rm -f $(BIN)
	rm -f $(BIN).o

# ==================================================================================================

.PHONY: clean

# ==================================================================================================

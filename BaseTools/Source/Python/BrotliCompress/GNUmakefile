## @file
# GNU/Linux Makefile for BrotliCompress tool.
#
# Copyright (c) 2022, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

.PHONY: all
.PHONY: build
.PHONY: clean

ROOT_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

all: build

build:
	@cd $(ROOT_DIR)/../../C/BrotliCompress/brotli/ && python setup.py build_ext --build-lib $(ROOT_DIR)

clean:
	@cd $(ROOT_DIR)/../../C/BrotliCompress/brotli/ && python setup.py clean
	@find $(ROOT_DIR) -name '*.pyc' | xargs -r rm -v
	@find $(ROOT_DIR) -name '*.so' | xargs -r rm -v
	@find $(ROOT_DIR) -type d -name '__pycache__' | xargs -r rm -v -r

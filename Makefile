# Makefile for source rpm: log4j
# $Id$
NAME := log4j
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common

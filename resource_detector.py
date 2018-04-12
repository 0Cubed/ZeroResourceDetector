# !/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import codecs
import logging
import csv
import importlib
import re
import string
import locale
import json
import xml.etree.cElementTree as ET 
import pyparsing as PY
from enum import Enum, IntEnum
from datetime import datetime, timezone


__author__ = "Zero<zero-cubed@outlook.com>"
__version__ = "1.0.0"
__application__ = "resource detector"


BASE_LANGUAGE = "en-us"

STANDARDIZED_LANGUAGES = {
             #Tier0-------------------------------------------------------------------------------------------
             "en" : "en-us", "en-us" : "en-us", "1033" : "en-us", "english"     : "en-us", "en_us" : "en-us",
             #Tier1-------------------------------------------------------------------------------------------
             "de" : "de-de", "de-de" : "de-de", "1031" : "de-de", "german"      : "de-de", "de_de" : "de-de",
             "es" : "es-es", "es-es" : "es-es", "3082" : "es-es", "spanish"     : "es-es", "es_es" : "es-es", "es-mx" : "es-es",
             "fr" : "fr-fr", "fr-fr" : "fr-fr", "1036" : "fr-fr", "french"      : "fr-fr", "fr_fr" : "fr-fr",
             "ja" : "ja-jp", "ja-jp" : "ja-jp", "1041" : "ja-jp", "japanese"    : "ja-jp", "ja_jp" : "ja-jp",
             "zh" : "zh-cn", "zh-cn" : "zh-cn", "2052" : "zh-cn", "chinese"     : "zh-cn", "zh_cn" : "zh-cn", "zh-rcn" : "zh-cn", "zh-hans" : "zh-cn", "zh-chs" : "zh-cn", "zh_hans" : "zh-cn", "sc" : "zh-cn", "cn" : "zh-cn",
             #Tier2-------------------------------------------------------------------------------------------
             "ko" : "ko-kr", "ko-kr" : "ko-kr", "1042" : "ko-kr", "korean"      : "ko-kr", "ko_kr" : "ko-kr",
             "ru" : "ru-ru", "ru-ru" : "ru-ru", "1049" : "ru-ru", "russian"     : "ru-ru", "ru_ru" : "ru-ru",
             "tc" : "zh-tw", "zh-tw" : "zh-tw", "1028" : "zh-tw", "tw"          : "zh-tw", "zh_tw" : "zh-tw", "zh-rtw" : "zh-tw", "zh-hant" : "zh-tw", "zh-cht" : "zh-tw", "zh_hant" : "zh-tw",
             #Tier3-------------------------------------------------------------------------------------------
             "ar" : "ar-sa", "ar-sa" : "ar-sa", "1025" : "ar-sa", "arabic"      : "ar-sa", "ar_sa" : "ar-sa",
             "da" : "da-dk", "da-dk" : "da-dk", "1030" : "da-dk", "danish"      : "da-dk", "da_dk" : "da-dk",
             "he" : "he-il", "he-il" : "he-il", "1037" : "he-il", "hebrew"      : "he-il", "he_il" : "he-il",
             "it" : "it-it", "it-it" : "it-it", "1040" : "it-it", "italian"     : "it-it", "it_it" : "it-it",
             "nl" : "nl-nl", "nl-nl" : "nl-nl", "1043" : "nl-nl", "dutch"       : "nl-nl", "nl_nl" : "nl-nl",
             "no" : "no-no", "no-no" : "no-no", "1044" : "no-no", "norwegian"   : "no-no", "no_no" : "no-no", "nb-no" : "no-no", "nb" : "no-no", "nn-no" : "no-no", "nn" : "no-no",#TBD
             "pt" : "pt-br", "pt-br" : "pt-br", "1046" : "pt-br", "portuguese"  : "pt-br", "pt_br" : "pt-br", 
             "pt" : "pt-br", "pt-pt" : "pt-pt", "2070" : "pt-pt", "portuguese"  : "pt-br", "pt_pt" : "pt-pt", #Add some duplicate items to keep coding format
             "pl" : "pl-pl", "pl-pl" : "pl-pl", "1045" : "pl-pl", "polish"      : "pl-pl", "pl_pl" : "pl-pl",
             "sv" : "sv-se", "sv-se" : "sv-se", "1053" : "sv-se", "swedish"     : "sv-se", "sv_se" : "sv-se",
             #Others-----------------------------------------------------------------------------------------------
             "bg" : "bg-bg", "bg-bg" : "bg-bg",
             "lt" : "lt-lt", "lt-lt" : "lt-lt",
             "ca" : "ca-es", "ca-es" : "ca-es",
             "cs" : "cs-cz", "cs-cz" : "cs-cz",
             "cy" : "cy-gb", "cy-gb" : "cy-gb",
             "el" : "el-gr", "el-gr" : "el-gr",
             "fi" : "fi-fi", "fi-fi" : "fi-fi",
             "et" : "et-ee", "et-ee" : "et-ee",
             "hi" : "hi-in", "hi-in" : "hi-in",
             "hu" : "hu-hu", "hu-hu" : "hu-hu",
             "id" : "id-id", "id-id" : "id-id",
             "lv" : "lv-lv", "lv-lv" : "lv-lv",
             "ro" : "ro-ro", "ro-ro" : "ro-ro",
             "ru" : "ru-ru", "ru-ru" : "ru-ru",
             "sk" : "sk-sk", "sk-sk" : "sk-sk",
             "sl" : "sl-si", "sl-si" : "sl-si",
             "th" : "th-th", "th-th" : "th-th",
             "tr" : "tr-tr", "tr-tr" : "tr-tr",
             "uk" : "uk-ua", "uk-ua" : "uk-ua",
             "af" : "af-za", "af-za" : "af-za",
             "sq" : "sq-al", "sq-al" : "sq-al",
             "am" : "am-et", "am-et" : "am-et",
             "hy" : "hy-am", "hy-am" : "hy-am",
             "as" : "as-in", "as-in" : "as-in",
             "eu" : "eu-es", "eu-es" : "eu-es",
             "be" : "be-by", "be-by" : "be-by",
             "bn" : "bn-bd", "bn-bd" : "bn-bd", #TBD
             "ca" : "ca-es", "ca-es" : "ca-es", #TBD
             "gl" : "gl-es", "gl-es" : "gl-es",
             "ka" : "ka-ge", "ka-ge" : "ka-ge",
             "gu" : "gu-in", "gu-in" : "gu-in",
             "is" : "is-is", "is-is" : "is-is",
             "ga" : "ga-ie", "ga-ie" : "ga-ie",
             "xh" : "xh-za", "xh-za" : "xh-za",
             "zu" : "zu-za", "zu-za" : "zu-za",
             "kn" : "kn-in", "kn-in" : "kn-in",
             "kk" : "kk-kz", "kk-kz" : "kk-kz",
             "km" : "km-kh", "km-kh" : "km-kh",
             "rw" : "rw-rw", "rw-rw" : "rw-rw",
             "sw" : "sw-ke", "sw-ke" : "sw-ke",
             "lb" : "lb-lu", "lb-lu" : "lb-lu",
             "mk" : "mk-mk", "mk-mk" : "mk-mk",
             "ms" : "ms-bn", "ms-bn" : "ms-bn", #TBD
             "ml" : "ml-in", "ml-in" : "ml-in",
             "mt" : "mt-mt", "mt-mt" : "mt-mt",
             "mr" : "mr-in", "mr-in" : "mr-in",
             "ne" : "ne-np", "ne-np" : "ne-np",
             "or" : "or-in", "or-in" : "or-in",
             "fa" : "fa-ir", "fa-ir" : "fa-ir",
             "tn" : "tn-bw", "tn-bw" : "tn-bw", #TBD
             "si" : "si-lk", "si-lk" : "si-lk",
             "ta" : "ta-in", "ta-in" : "ta-in",
             "te" : "te-in", "te-in" : "te-in",
             "ti" : "ti-et", "ti-et" : "ti-et",
             "ur" : "ur-pk", "ur-pk" : "ur-pk",
             "vi" : "vi-vn", "vi-vn" : "vi-vn",
             "cy" : "cy-gb", "cy-gb" : "cy-gb",
             "wo" : "wo-sn", "wo-sn" : "wo-sn",
             "hr" : "hr-hr", "hr-hr" : "hr-hr", "hr-ba" : "hr-hr",  #TBD
             "sr" : "sr-Latn", "sr-Latn" : "sr-Latn", #TBD
             "bs" : "bs-cyrl", "bs-cyrl" : "bs-cyrl", #TBD
             "pa" : "pa-arab", "pa-arab" : "pa-arab", #TBD
             "mi" : "mi-latn", "mi-latn" : "mi-latn", #TBD
             "nso" : "nso-za", "nso-za" : "nso-za",
             "quz" : "quz-bo", "quz-bo" : "quz-bo", #TBD
             "prs" : "prs-af", "prs-af" : "prs-af", #TBD
             "kok" : "kok-in", "kok-in" : "kok-in",
             "fil" : "fil-latn", "fil-latn" : "fil-latn", #TBD
             "gb-latn" : "gb-gb", "gb-gb" : "gb-gb",
             "ig-latn" : "ig-ng", "ig-ng" : "ig-ng",
             "yo-latn" : "yo-ng", "yo-ng" : "yo-ng",
             "ky-cyrl" : "ky-kg", "ky-kg" : "ky-kg",
             "tk-cyrl" : "tk-latn", "tk-latn" : "tk-latn", #TBD
             "tt-arab" : "tt-cyrl", "tt-cyrl" : "tt-cyrl", #TBD
             "tg-arab" : "tg-cyrl", "tg-cyrl" : "tg-cyrl", #TBD
             "iu-cans" : "iu-latn", "iu-latn" : "iu-latn", #TBD
             "mn-cyrl" : "mn-mong", "mn-mong" : "mn-mong", #TBD
             "az-arab" : "az-arab-az", "az-arab-az" : "az-arab-az", #TBD
             "sr-cyrl" : "sr-cyrl-cs", "sr-cyrl-cs" : "sr-cyrl-cs", #TBD
             "quc-latn" : "qut-gt", "qut-gt" : "qut-gt", #TBD
             "chr-cher" : "chr-cher-us", "chr-cher-us" : "chr-cher-us", #TBD
             "uz-latn-uz" : "uz-latn", "uz-latn" : "uz-latn",
             "sd-arab-pk" : "sd-arab", "sd-arab" : "sd-arab", #TBD
             "ha-latn-ng" : "ha-latn", "ha-latn" : "ha-latn",
             "ku-arab-iq" : "ku-arab", "ku-arab" : "ku-arab",
             }

LANGUAGE_ENCODINGS = {
             #Tier0------------------------------------------------------
             "en-us" : "cp1252", #Use "cp1252" instead of "ascii" here because sometimes English resource file can be successfully opened with the former but not the later 
             #Tier1------------------------------------------------------
             "de-de" : "cp1252",
             "es-es" : "cp1252",
             "fr-fr" : "cp1252",
             "ja-jp" : "shift_jis", #"cp932"
             "zh-cn" : "cp936",
             #Tier2------------------------------------------------------
             "ko-kr" : "cp949",
             "ru-ru" : "cp1251",
             "zh-tw" : "big5", #"cp950"
             #Tier3------------------------------------------------------
             "ar-sa" : "cp1256",
             "da-dk" : "cp865",
             "he-il" : "cp1255",
             "it-it" : "ascii", #TBD
             "nl-nl" : "ascii", #TBD
             "no-no" : "cp865",
             "pt-br" : "cp860", 
             "pl-pl" : "ascii", #TBD
             "sv-se" : "ascii", #TBD
             }

TAB_WIDTH = 4

LOG = None


class Severity(Enum):
    warning =   "warning"
    error   =   "error"
    
    
class IssueCode(IntEnum):
    duplicate_key           =   2000
    missing_key             =   2001
    redundant_key           =   2002
    untranslated_value      =   2003
    unused_key              =   2004
    improperly_used_key     =   2005
    missing_file            =   2006
    redundant_file          =   2007
    unmatched_placeholder   =   2008
    format_error            =   2009
    encoding_error          =   2010


class IssueName(Enum):
    duplicate_key           =   "duplicate key"
    missing_key             =   "missing key"
    redundant_key           =   "redundant key"
    untranslated_value      =   "untranslated value"
    unused_key              =   "unused key"
    improperly_used_key     =   "undefined key"
    missing_file            =   "missing file"
    redundant_file          =   "redundant file"
    unmatched_placeholder   =   "unmatched placeholder"
    format_error            =   "format error"
    encoding_error          =   "encoding error"


class Description(Enum):
    duplicate_key           =   "duplicate key in resource file(s)"
    missing_key             =   "missing key in localized resource file(s)"
    redundant_key           =   "redundant key in localized resource file(s)"
    untranslated_value      =   "untranslated string value in localized resource file"
    unused_key              =   "unused key in resource file"
    improperly_used_key     =   "undefined resource key used in source code"
    missing_file            =   "missing resource file(s)"
    redundant_file          =   "redundant resource file(s)"
    unmatched_placeholder   =   "unmatched placeholder(s) in localized resource file"
    format_error            =   "string value with format error in resource file"
    encoding_error          =   "unknown or incorrect encoding of resource file"


class Context(Enum):
    duplicate_key           =   "key=\u2308{0}\u2309, language(s)=\u2308{1}\u2309"
    missing_key             =   "key=\u2308{0}\u2309, language(s)=\u2308{1}\u2309"
    redundant_key           =   "key=\u2308{0}\u2309, language(s)=\u2308{1}\u2309"
    untranslated_value      =   "key=\u2308{0}\u2309, value=\u2308{1}\u2309"
    unused_key              =   "key=\u2308{0}\u2309"
    improperly_used_key     =   "{0}"
    missing_file            =   "language(s)=\u2308{0}\u2309"
    redundant_file          =   "language(s)=\u2308{0}\u2309"
    unmatched_placeholder   =   "key=\u2308{0}\u2309, base value=\u2308{1}\u2309, localized value=\u2308{2}\u2309"
    format_error            =   "key=\u2308{0}\u2309, value=\u2308{1}\u2309"
    encoding_error          =   "{0}"
    

class Issue:
    def __init__(self, file, line, column_begin, column_begin_offset, column_end, severity, code, description, context, information = None):
        self.file= file
        self.line = line
        self.column_begin = column_begin
        self.column_begin_offset = column_begin_offset
        self.column_end = column_end
        self.code = code
        self.description = description
        self.severity = severity
        self.context = context
        self.information = information

    def write(self):
        issue = "file: {file}, ".format(file = self.file)
        if self.line or self.column_begin or self.column_end:
            issue += "line: {line}, column begin: {column_begin}, column end: {column_end}, ".format(line = self.line, column_begin = self.column_begin + self.column_begin_offset, column_end = self.column_end)
        issue += "issue: {description}, severity: {severity}, context: {context}".format(description = self.description.value, severity = self.severity.value, context = self.context.replace("\u2308", "").replace("\u2309", ""))
        if self.information:
            issue += ", information: {information}".format(information = self.information)
        LOG.info(issue)

    def write_with_position(self):
        LOG.info("file: {file}, line: {line}, column begin: {column_begin}, column end: {column_end}, issue: {description}, severity: {severity}, context: {context}".format(file = self.file, line = self.line, column_begin = self.column_begin + self.column_begin_offset, column_end = self.column_end, description = self.description.value, severity = self.severity.value, context = self.context.replace("\u2308", "").replace("\u2309", "")))

    def write_without_position(self):
        LOG.info("file: {file}, issue: {description}, severity: {severity}, context: {context}".format(file = self.file, description = self.description.value, severity = self.severity.value, context = self.context.replace("\u2308", "").replace("\u2309", "")))


class Issues:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.errors = []
        self.issue_count = 0
        self.warning_count = 0
        self.error_count = 0

    def add(self, issue):
        self.issues.append(issue)
        self.issue_count += 1
        if issue.severity == Severity.warning:
            self.warnings.append(issue)
            self.warning_count += 1
        elif issue.severity == Severity.error:
            self.errors.append(issue)
            self.error_count += 1
        else:
            pass

    def extend(self, issues_add):
        if not issues_add:
            return
        self.issues.extend(issues_add.issues)
        self.warnings.extend(issues_add.warnings)
        self.errors.extend(issues_add.errors)
        self.issue_count += issues_add.issue_count
        self.warning_count += issues_add.warning_count
        self.error_count += issues_add.error_count

    def get_issues(self):
        for issue in self.issues:
            yield issue

    def get_warnings(self):
        for warning in self.warnings:
            yield warning

    def get_errors(self):
        for error in self.errors:
            yield error


class BaseResFile:
    def __init__(self, directory, file, extension, language = None):
        self.directory = directory
        self.file = file
        self.extension = extension
        self.path = os.path.join(self.directory, self.file)
        if language:
            self.language = language
        else:
            self.language = self.get_language()
        self.keys = set()
        self.values = []
        self.key_value_pairs = {}
        #self.key_line_pairs = {}
        self.duplicate_keys = []
        self.escape_error_keys = []
        self.item_count = 0
        self.encoding_error = ""

    def reset_value_containers(self):
        self.keys = set()
        self.values = []
        self.key_value_pairs = {}
        #self.key_line_pairs = {}
        self.duplicate_keys = []
        self.escape_error_keys = []
        self.item_count = 0

    def get_language(self):
        sub_names = self.file.lower().split(".")
        try:
            sub_name = sub_names[-2]
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        except IndexError:
            pass
        for sub_name in sub_names:
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        sub_dirs = self.directory.lower().split(os.sep)
        try:
            sub_dir = sub_dirs[-1]
            if sub_dir in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_dir]
        except IndexError:
            pass
        #Is the following necessary? Do we need to decide whether the other sub directory is language id besides the last sub directory?
        for sub_dir in sub_dirs:
            if sub_dir in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_dir]
        return BASE_LANGUAGE

    def is_file(self):
        return os.path.isfile(self.path)

    def read(self):
        try:
            f = open(self.path, "rb")
            bin_data = f.read()
            f.close()
        except Exception as e:
            LOG.error("Cannot open file '{path}' to read: {exception}".format(path = self.path, exception = e))
            return None
        for bom, encoding in {codecs.BOM_UTF8 : "utf_8", codecs.BOM_UTF16_BE : "utf_16_be", codecs.BOM_UTF16_LE : "utf_16_le", codecs.BOM_UTF32_BE : "utf_32_be", codecs.BOM_UTF32_LE : "utf_32_le"}.items():
            if bin_data.startswith(bom):
                try:
                    return bin_data[len(bom):].decode(encoding)
                except UnicodeDecodeError:
                    #LOG.error("Cannot read file '{path}', the real encoding is not the same as {encoding} encoding detected by BOM".format(path = self.path, encoding = encoding))
                    self.encoding_error = "the real encoding is not the same as '{encoding}' encoding detected by BOM".format(encoding = encoding)
                    return None
        try:
            return bin_data.decode("utf_8")
        except UnicodeDecodeError:
            pass
        if self.language in LANGUAGE_ENCODINGS.keys():
            try:
                return bin_data.decode(LANGUAGE_ENCODINGS[self.language])
            except UnicodeDecodeError:
                pass
            try:
                return bin_data.decode("cp1252")#some localized resource files are not translated 
            except UnicodeDecodeError:
                #LOG.error("Cannot read file '{0}', encoding is unknown".format(self.path))
                self.encoding_error = "unknown encoding"
                return None
        else:
            #LOG.error("Cannot read file '{0}', encoding is unknown".format(self.path))
            self.encoding_error = "unknown encoding"
            return None

    def get_group_id(self):
        sub_names = self.file.split(".")
        file_adjusted = ""
        for sub_name in sub_names:
            if not sub_name.lower() in STANDARDIZED_LANGUAGES.keys():
                file_adjusted += sub_name
        #dir_adjusted = self.directory
        #base_name = os.path.basename(self.directory).lower()
        #if base_name in STANDARDIZED_LANGUAGES.keys():
        #    dir_adjusted = os.path.dirname(self.directory)
        #return file_adjusted, dir_adjusted
        #remove language in whatever position instead of the last position: add language position as the third id(the position set to 1 if there is no language)
        sub_dirs = self.directory.split(os.sep)
        dir_adjusted = sub_dirs
        index = 0
        for sub_dir in sub_dirs:
            if sub_dir.lower() in STANDARDIZED_LANGUAGES.keys():
                dir_adjusted.remove(sub_dir)
                break
            index += 1
        return file_adjusted, os.sep.join(dir_adjusted), index

    def parse(self, parsing_patterns = None):
        pass


class ResFileGroup:
    def __init__(self, base_res_file = None):
        self.res_files = {}
        self.localized_res_files = {}
        self.base_res_file = base_res_file
        #TODO: check whether the language of base_res_file is BASE_LANGUAGE 
        if base_res_file:
            self.res_files[base_res_file.language] = base_res_file

    def add_resource_file(self, res_file):
        #TODO: check the language of current file exists in group
        self.res_files[res_file.language] = res_file
        if res_file.language != BASE_LANGUAGE:
            self.localized_res_files[res_file.language] = res_file
        else:
            if self.base_res_file:
                LOG.warning("Two English resource files found in a group. If the languages of them are wrongly-determined, contact the tool author, otherwise remove unused resource file in source code or check the configuration file to make sure correct resource file is used. Two suspect resource files are:\n           '{base_file}'\n           '{current_file}'".format(base_file = self.base_res_file.path, current_file = res_file.path))
            self.base_res_file = res_file


class BaseResDetector:
    def __init__(self, dir_input, res_files_input, config_input, type_input):
        self.src_dir = dir_input
        self.config = config_input
        self.detect_languages = set()
        self.detect_issues = set()
        self.res_files = res_files_input
        self.res_file_type = type_input
        self.res_file_ext = self.res_files[0].extension
        self.res_file_groups = []
        self.issues = Issues()
        self.res_file_count = 0
        self.item_count = 0

    def detect(self):
        self.group_resource_files()
        self.parse_resource_files()
        self.filter_resource_file_groups()
        self.get_detect_languages()
        self.get_detect_issues()
        self.detect_duplicate_keys()
        self.detect_missing_keys()
        self.detect_redundant_keys()
        self.detect_untranslated_values()
        self.detect_unused_and_undefined_keys()
        self.detect_missing_resource_files()
        self.detect_redundant_resource_files()
        self.detect_unmatched_placeholders()
        self.detect_values_with_format_error()
        self.detect_encoding_errors()

    def print_group(self):
        for res_file_group in self.res_file_groups:
            for language, res_file in sorted(res_file_group.res_files.items()):
                res_file_info = res_file.path + "   " + language
                if res_file == res_file_group.base_res_file:
                    res_file_info += "------base------"
                LOG.info(res_file_info)
            LOG.info("************************************************************************************************************************")

    def write_configuration(self):
        self.group_resource_files()
        self.parse_resource_files()
        self.filter_resource_file_groups()
        self.get_detect_languages()
        self.get_detect_issues()
        config_file = open(file = self.config.config_file_path, mode = "a", encoding = "utf_8_sig")
        LOG.info("Writing configuration...")
        config_file.write(self.config.detector_switch_attrs[self.res_file_type] + " = True\n")
        config_file.write("{attr_name} = [{detect_issues}]\n".format(attr_name = self.config.detect_issues_attrs[self.res_file_type], detect_issues = ", ".join(['"{item}"'.format(item = item.value) for item in IssueName if item.value in self.detect_issues])))
        config_file.write(self.config.detect_languages_attrs[self.res_file_type] + " = [")
        for language in sorted(self.detect_languages):
            config_file.write("\"" + language + "\", ")
        config_file.write("]\n")
        config_file.write(self.config.fixed_res_groups_attrs[self.res_file_type] + " = True\n")
        config_file.write(self.config.res_groups_attrs[self.res_file_type] + " =\\\n[\n")
        for res_file_group in self.res_file_groups:
            config_file.write("{\n")
            for language, res_file in sorted(res_file_group.res_files.items()):
                config_file.write("\"" + language + "\" : R\"" + res_file.path + "\",\n")
            config_file.write("},\n")
        config_file.write("]\n\n\n")
        config_file.close()

    def group_resource_files(self):
        use_fixed_res_file_group = True
        if self.config.use_user_config:
            try:
                use_fixed_res_file_group = getattr(self.config.config_module, self.config.fixed_res_groups_attrs[self.res_file_type])
            except AttributeError:
                pass
        if self.config.use_user_config and use_fixed_res_file_group:
            LOG.info("Reading resource file group information from configuration file...")
            try:
                res_file_groups_config = getattr(self.config.config_module, self.config.res_groups_attrs[self.res_file_type])
            except AttributeError:
                LOG.critical("'{group_name}' is not defined in configuration file".format(group_name = self.config.res_groups_attrs[self.res_file_type]))
                quit_application(-1)
            for res_file_group_config in res_file_groups_config:
                res_file_group = ResFileGroup()
                for language_key, path in res_file_group_config.items():
                    absolute_path = os.path.join(self.src_dir, path)
                    directory = os.path.dirname(absolute_path)
                    file = os.path.basename(absolute_path)
                    if not file.endswith("." + self.res_file_ext):
                        LOG.critical("'{file}' is not a '{type}' resource file".format(file = absolute_path, type = self.res_file_ext))
                        quit_application(-1)
                    if not os.path.isfile(absolute_path):
                        LOG.critical("'{path}' does not exist".format(path = absolute_path))
                        quit_application(-1)
                    language = None
                    try:
                        language = STANDARDIZED_LANGUAGES[language_key]
                    except KeyError:
                        LOG.critical("'{language_key}' is not a valid language, please refer to the following: {standardized_languages}".format(language_key = language_key, standardized_languages = "'" + "', '".join(STANDARDIZED_LANGUAGES.keys()) + "'."))
                        quit_application(-1)
                    res_file = self.config.res_file_classes[self.res_file_type](directory , file, self.res_file_ext, language)
                    res_file_group.add_resource_file(res_file)
                self.res_file_groups.append(res_file_group)
        else:
            LOG.info("Grouping resource files...")
            id_group_pairs = {}
            for res_file in self.res_files:
                group_id = res_file.get_group_id()
                res_file_group = id_group_pairs.get(group_id)
                if res_file_group:
                    res_file_group.add_resource_file(res_file)
                else:
                    res_file_group = ResFileGroup()
                    res_file_group.add_resource_file(res_file)
                    id_group_pairs[group_id] = res_file_group
                    self.res_file_groups.append(res_file_group)        

    def get_detect_issues(self):
        if self.config.use_user_config:
            LOG.info("Reading issue types to be detected from configuration file...")
            self.detect_issues = getattr(self.config.config_module, self.config.detect_issues_attrs[self.res_file_type], self.config.default_detect_issues)
        else:
            LOG.info("Getting default issue types to be detected...")
            self.detect_issues = self.config.default_detect_issues

    def get_detect_languages(self):
        if self.config.use_user_config:
            LOG.info("Reading languages to be detected from configuration file...")
            try:
                self.detect_languages = set(getattr(self.config.config_module, self.config.detect_languages_attrs[self.res_file_type]))
            except AttributeError:
                LOG.critical("Cannot read languages from configuration files")
                quit_application(-1)
        else:
            LOG.info("Determining languages to be detected...")
            language_counts = {}
            max_count = 0
            for res_file_group in self.res_file_groups:
                num = len(res_file_group.res_files.keys())
                if num != 1:
                    if not num in language_counts.keys():
                        language_counts[num] = 0
                    language_counts[num] += 1
                    current_count = language_counts[num]
                    if current_count > max_count:
                        max_count = current_count
                        self.detect_languages = set(res_file_group.res_files.keys())
                    elif current_count == max_count:
                        current_languages = set(res_file_group.res_files.keys())
                        if len(current_languages) > len(self.detect_languages):
                            self.detect_languages = current_languages
                    else:
                        pass
            if max_count == 0:
                try:
                    self.detect_languages = set(self.res_file_groups[0].res_files.keys())
                except IndexError:
                    pass
        LOG.info("Detect language(s): {languages}".format(languages = " ".join(sorted(self.detect_languages))))
        
    def get_parsing_patterns(self):
        return None

    def parse_resource_files(self):
        LOG.info("Parsing resource files, which may take some time...")
        parsing_patterns = self.get_parsing_patterns()
        for res_file_group in self.res_file_groups:
            for language, res_file in res_file_group.res_files.items():
                res_file.parse(parsing_patterns)
                self.item_count += res_file.item_count

    def filter_resource_file_groups(self):
        LOG.info("Removing group where each file has no string...")
        temp_groups = list(self.res_file_groups)
        self.res_file_groups = []
        for res_file_group in temp_groups:
            qualified_flag = False
            for language, res_file in res_file_group.res_files.items():                
                if (res_file.item_count != 0) or res_file.encoding_error:
                    qualified_flag = True
            if qualified_flag:
                self.res_file_groups.append(res_file_group)
                self.res_file_count += len(res_file_group.res_files)
                
    def detect_missing_resource_files(self):
        if IssueName.missing_file.value not in self.detect_issues:
            return
        LOG.info("Detecting missing localized resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            missing_languages = self.detect_languages - set(res_file_group.res_files.keys())
            formatted_languages = "/".join(sorted(missing_languages))
            if formatted_languages:
                issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.missing_file, description = Description.missing_file, severity = Severity.warning, context = Context.missing_file.value.format(formatted_languages))
                self.issues.add(issue)
            
    def detect_redundant_resource_files(self):
        if IssueName.redundant_file.value not in self.detect_issues:
            return
        LOG.info("Detecting redundant localized resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            redundant_languages = set(res_file_group.res_files.keys()) - self.detect_languages
            formatted_languages = "/".join(sorted(redundant_languages))
            if formatted_languages:
                issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.redundant_file, description = Description.redundant_file, severity = Severity.warning, context = Context.redundant_file.value.format(formatted_languages))
                self.issues.add(issue)

    def detect_duplicate_keys(self):
        if IssueName.duplicate_key.value not in self.detect_issues:
            return
        LOG.info("Detecting duplicate keys in resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            key_languages = {}
            for language, res_file in sorted(res_file_group.res_files.items()):                
                for duplicate_key in res_file.duplicate_keys:
                    duplicate_languages = key_languages.get(duplicate_key, None)
                    if duplicate_languages:
                        key_languages[duplicate_key] = duplicate_languages + "/" + language
                    else:
                        key_languages[duplicate_key] = language
            for duplicate_key, duplicate_languages in sorted(key_languages.items()):
                issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.duplicate_key, description = Description.duplicate_key, severity = Severity.error, context = Context.duplicate_key.value.format(duplicate_key, duplicate_languages))
                self.issues.add(issue)

    def detect_missing_keys(self):
        if IssueName.missing_key.value not in self.detect_issues:
            return
        LOG.info("Detecting missing keys in localized resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            base_keys = base_res_file.keys
            key_languages = {}
            for language, res_file in sorted(res_file_group.localized_res_files.items()):
                missing_keys = base_keys - res_file.keys
                for missing_key in missing_keys:
                    missing_languages = key_languages.get(missing_key, None)
                    if missing_languages:
                        key_languages[missing_key] = missing_languages + "/" + language
                    else:
                        key_languages[missing_key] = language
            for missing_key, missing_languages in sorted(key_languages.items()):
                issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.missing_key, description = Description.missing_key, severity = Severity.error, context = Context.missing_key.value.format(missing_key, missing_languages))
                self.issues.add(issue)

    def detect_redundant_keys(self):
        if IssueName.redundant_key.value not in self.detect_issues:
            return
        LOG.info("Detecting redundant keys in localized resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            base_keys = base_res_file.keys
            key_languages = {}
            for language, res_file in sorted(res_file_group.localized_res_files.items()):
                redundant_keys = res_file.keys - base_keys
                for redundant_key in redundant_keys:
                    redundant_languages = key_languages.get(redundant_key, None)
                    if redundant_languages:
                        key_languages[redundant_key] = redundant_languages + "/" + language
                    else:
                        key_languages[redundant_key] = language
            for redundant_key, redundant_languages in sorted(key_languages.items()):
                issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.redundant_key, description = Description.redundant_key, severity = Severity.error, context = Context.redundant_key.value.format(redundant_key, redundant_languages))
                self.issues.add(issue)

    def is_translation_necessary(self, value):
        if not value:
            return False
        if value.isnumeric():
            return False
        #cannot make sure url is not necessary to be translated
        #if value.startswith("http://") or value.startswith("https://"):
            #return False
        return True

    def detect_untranslated_values(self):
        if IssueName.untranslated_value.value not in self.detect_issues:
            return
        LOG.info("Detecting untranslated values in resource files...")
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            base_keys = base_res_file.keys
            sorted_base_keys = sorted(base_keys)
            base_key_value_pairs = base_res_file.key_value_pairs
            for language, res_file in sorted(res_file_group.localized_res_files.items()):
                target_keys = res_file.keys
                target_key_value_pairs = res_file.key_value_pairs
                for key in sorted_base_keys:
                    if key in target_keys:
                        target_value = target_key_value_pairs[key]
                        if (base_key_value_pairs[key] == target_value) and self.is_translation_necessary(target_value):
                            issue = Issue(file = res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.untranslated_value, description = Description.untranslated_value, severity = Severity.warning, context = Context.untranslated_value.value.format(key, target_value))
                            self.issues.add(issue)

    def detect_values_with_format_error(self):
        if IssueName.format_error.value not in self.detect_issues:
            return
        LOG.info("Detecting string value format issues in resource files...")
        for res_file_group in self.res_file_groups:
            for language, res_file in sorted(res_file_group.res_files.items()):
                key_value_pairs = res_file.key_value_pairs
                for escape_error_key in res_file.escape_error_keys:
                    issue = Issue(file = res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.format_error, description = Description.format_error, severity = Severity.error, context = Context.format_error.value.format(escape_error_key, key_value_pairs[escape_error_key]))
                    self.issues.add(issue)

    def get_placeholder_pattern(self):
        return None

    def detect_unmatched_placeholders(self):
        if IssueName.unmatched_placeholder.value not in self.detect_issues:
            return
        LOG.info("Detecting unmatched placeholders in localized resource files...")
        placeholder_pattern = self.get_placeholder_pattern()
        if not placeholder_pattern:
            LOG.info("Placeholder pattern is not defined, skip detection")
            return  
        for res_file_group in self.res_file_groups:
            base_res_file = res_file_group.base_res_file
            if not base_res_file:
                continue
            base_key_value_pairs = base_res_file.key_value_pairs
            sorted_localized_res_files = sorted(res_file_group.localized_res_files.items())
            for base_key, base_value in sorted(base_key_value_pairs.items()):#If this sorting cosumes a lot of time, sorting detection result instead
                base_placeholders = {}
                #LOG.info("scanning string: {0}".format(base_value))
                for tokens, start, end in placeholder_pattern.scanString(base_value):
                    placeholder = tokens[0]
                    #LOG.info(placeholder)
                    if placeholder in base_placeholders.keys():
                        base_placeholders[placeholder] += 1
                    else:
                        base_placeholders[placeholder] = 1
                if not base_placeholders:
                    continue
                for language, res_file in sorted_localized_res_files:
                    target_keys = res_file.keys
                    target_key_value_pairs = res_file.key_value_pairs
                    target_placeholders = {}
                    if base_key in target_keys:
                        target_value = target_key_value_pairs[base_key]
                        for tokens, start, end in placeholder_pattern.scanString(target_value):
                            placeholder = tokens[0]
                            if placeholder in target_placeholders.keys():
                                target_placeholders[placeholder] += 1
                            else:
                                target_placeholders[placeholder] = 1
                        if not base_placeholders == target_placeholders:
                            #LOG.info(",".join(base_placeholders.keys()) + "---" + ",".join(target_placeholders.keys()))
                            issue = Issue(file = res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.unmatched_placeholder, description = Description.unmatched_placeholder, severity = Severity.error, context = Context.unmatched_placeholder.value.format(base_key, base_value, target_value))
                            self.issues.add(issue)

    def detect_unused_and_undefined_keys(self):
        pass
    
    def detect_encoding_errors(self):
        if IssueName.encoding_error.value not in self.detect_issues:
            return
        LOG.info("Detecting resource file encoding errors...")
        for res_file_group in self.res_file_groups:
            for language, res_file in sorted(res_file_group.res_files.items()):                
                if res_file.encoding_error:
                    issue = Issue(file = res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.encoding_error, description = Description.encoding_error, severity = Severity.error, context = Context.encoding_error.value.format(res_file.encoding_error))
                    self.issues.add(issue)        


class RcResFile(BaseResFile):
    def parse(self, parsing_patterns):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            string_table, key_value_pair = parsing_patterns
            for table_content_token, start_location, end_location in string_table.scanString(data):
                for tokens, start, end in key_value_pair.scanString(table_content_token[0]):
                    for token in tokens:            
                        key = token[0]
                        value = token[1]
                        pure_value = value[1:-1]
                        #compare values to decide whether it is duplicated, workaround for Receiver for Windows since there are many #ifdef statements
                        if key in self.keys and pure_value == self.key_value_pairs[key]:
                            self.duplicate_keys.append(key)
                        self.keys.add(key)
                        self.values.append(pure_value)
                        self.key_value_pairs[key] = pure_value
                        self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class RcResDetector(BaseResDetector):
    def get_parsing_patterns(self):
        key = PY.Word(PY.alphas + "_", PY.alphanums + "_") | PY.Word(PY.nums)
        value = PY.dblQuotedString
        define_patterns = PY.Regex(R"#ifdef.*") | PY.Regex(R"#ifndef.*") | PY.Regex(R"#elif.*") | PY.Regex(R"#endif.*") # add for Receiver for Windows
        key_value_pair = (PY.Group(key + value) | define_patterns.suppress()).ignore(PY.cppStyleComment).parseWithTabs()
        white_char = PY.Word(string.whitespace, exact = 1)
        string_table = (white_char + PY.Literal("STRINGTABLE") + white_char).suppress() + PY.SkipTo((white_char + PY.Literal("BEGIN") + white_char) | PY.Literal("{"), ignore = PY.dblQuotedString | PY.cppStyleComment | define_patterns, include = True).suppress() + PY.originalTextFor(PY.SkipTo((white_char + PY.Literal("END") + (white_char | PY.stringEnd)) | PY.Literal("}"), ignore = PY.dblQuotedString | PY.cppStyleComment | define_patterns, include = True))
        #string_table_sign = (white_char + PY.Literal("STRINGTABLE") + white_char).suppress() + PY.SkipTo(PY.Literal("{"), ignore = PY.dblQuotedString | PY.cppStyleComment | define_patterns, include = True).suppress() + PY.originalTextFor(PY.SkipTo(PY.Literal("}"), ignore = PY.dblQuotedString | PY.cppStyleComment | define_patterns, include = True))
        string_table = string_table.ignore(PY.cppStyleComment).parseWithTabs().leaveWhitespace()
        return string_table, key_value_pair
    
    def get_placeholder_pattern(self):
        #reference: http://msdn.microsoft.com/en-us/library/windows/desktop/ms679351%28v=vs.85%29.aspx, http://msdn.microsoft.com/en-us/library/56e442dc.aspx
        positive_integer = PY.Word("123456789", PY.nums)
        integer = PY.Literal("0") | positive_integer
        flags = PY.Word("-+ #0")
        width = integer | PY.Literal("*")
        precision = PY.Literal(".") + width
        type_prefix = PY.Literal("ll") | PY.Literal("l") | PY.Literal("I32") | PY.Literal("I64") | PY.Literal("I") | PY.Literal("h") | PY.Literal("w")
        type_flag = PY.Word("cCdiouxXeEfgGaAnpsSZ", exact = 1)
        format_string_body = PY.Optional(flags) + PY.Optional(width) + PY.Optional(precision) + PY.Optional(type_prefix) + type_flag
        special_characters = PY.Combine(PY.Literal("%") + PY.Word("0% .!nrt", exact = 1))
        format_string = PY.Combine(PY.Literal("%") + format_string_body)
        numbered_format_string = PY.Combine(PY.Literal("%") + positive_integer + PY.Optional(PY.Literal("!") + format_string_body + PY.Literal("!")))
        placeholder_pattern = PY.originalTextFor(numbered_format_string | format_string | special_characters)
        return placeholder_pattern


class Rc2ResFile(RcResFile):
    pass


class Rc2ResDetector(RcResDetector):
    pass


class McResFile(BaseResFile):
    #reference : http://msdn.microsoft.com/en-us/library/windows/desktop/dd996906(v=vs.85).aspx
    def parse(self, parsing_patterns):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            key_value_pair = parsing_patterns
            for tokens, start_location, end_location in key_value_pair.scanString(data):
                key = tokens[0]
                value = tokens[1]
                if key in self.keys:
                    self.duplicate_keys.append(key)
                self.keys.add(key)
                self.values.append(value)
                self.key_value_pairs[key] = value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class McResDetector(BaseResDetector):
    def get_parsing_patterns(self):
        comment = PY.Regex(R";/(?:\*(?:[^*]*;\*+)+?/|/[^\n]*(?:\n[^\n]*)*?(?:(?<!\\)|\Z))")
        #comment = PY.Regex(R";.*") #this kind of comments are used in some projects
        variable = PY.Word(PY.alphanums + "_", PY.alphanums + "_")
        message_key = PY.Literal("MessageId") + PY.Literal("=") + PY.Optional(PY.Optional(PY.Literal("+")) + variable)
        severity = PY.Literal("Severity") + PY.Literal("=") + variable
        facility = PY.Literal("Facility") + PY.Literal("=") + variable
        symbolic_name = (PY.Literal("SymbolicName") + PY.Literal("=")).suppress() + variable
        output_base = PY.Literal("OutputBase") + PY.Literal("=") + PY.Optional(PY.Literal("{")) + variable + PY.Optional(PY.Literal("}"))
        language = PY.Literal("Language") + PY.Literal("=") + variable
        message_value = PY.SkipTo(PY.lineStart + PY.Literal(".")).setParseAction(lambda s, l, t: t[0].strip())
        #comment out below pattern since severity/facility/symbolic items can be in any order in reality, not like MSDN says...
        #key_value_pair = message_key.suppress() + PY.Optional(severity).suppress() + PY.Optional(facility).suppress() + symbolic_name + PY.Optional(output_base).suppress() + PY.Optional(language).suppress() + message_value
        careless_item = language | severity | facility | output_base
        key_value_pair = message_key.suppress() + PY.ZeroOrMore(careless_item).suppress() + symbolic_name + PY.ZeroOrMore(careless_item).suppress() + message_value
        return key_value_pair.ignore(comment).parseWithTabs()
    
    def get_placeholder_pattern(self):
        #reference : http://msdn.microsoft.com/en-us/library/windows/desktop/dd996906(v=vs.85).aspx and the links ont the page
        positive_integer = PY.Word("123456789", PY.nums)
        integer = PY.Literal("0") | positive_integer
        flags = PY.Word("-#0")
        width = integer
        precision = PY.Literal(".") + PY.Optional(integer)
        type_flag = PY.Word("h", "cCdsSu", exact = 2) | PY.Word("l", "cCdisSuxX", exact = 2) | PY.Word("cCdipsSu", exact = 1)
        format_string_body = PY.Optional(flags) + PY.Optional(width) + PY.Optional(precision) + type_flag
        special_characters = PY.Combine(PY.Literal("%") + PY.Word("0.!%nbr", exact = 1))
        numbered_format_string = PY.Combine(PY.Literal("%") + positive_integer + PY.Optional(PY.Literal("!") + format_string_body + PY.Literal("!")))
        placeholder_pattern = PY.originalTextFor(numbered_format_string | special_characters)
        return placeholder_pattern


class ResxResFile(BaseResFile):
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            root = ET.fromstring(data)
            #escape_pattern = None # need to add whether there is an escape error, no need for now since parseError will be thrown in current implementation
            for elem in root.findall("data"):
                key = elem.get("name")
                if key is None:
                    continue
                #filter strings from all values parsed
                if ("." in key) and (not key.endswith(".Text")):
                    continue
                #if there is no child named "value" under "data", the actual value in C# project is null, we set it to "" in order to save effort to handle it
                #if there is no text in "value" node, the actual value in C# project is ""
                value = ""
                sub_elem = elem.find("value")
                if sub_elem != None:
                    value = "".join(sub_elem.itertext())
                if key in self.keys:
                    self.duplicate_keys.append(key)
                #if escape_pattern.match(value):
                #    self.escape_error_keys.append(key)
                self.keys.add(key)
                self.values.append(value)
                self.key_value_pairs[key] = value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class ResxResDetector(BaseResDetector):
    def is_translation_necessary(self, value):
        return (BaseResDetector.is_translation_necessary(self, value) and (not "PublicKeyToken" in value))

    def get_placeholder_pattern(self):
        return PY.Literal("{").suppress() + PY.Word(PY.nums) + PY.Literal("}").suppress()


class ReswResFile(ResxResFile):
    pass


class ReswResDetector(ResxResDetector):
    pass


class WxlResFile(BaseResFile):
    # Maybe the most effeicent way is to get the last five character of the pure file name when determining the language based on the file name
    def get_language(self):
        sub_names = self.file.lower().split(".")
        try:
            sub_name = sub_names[-2]
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        except IndexError:
            pass
        for sub_name in sub_names:
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        #sometimes the file name is like agee_zh-CN.wxl
        sub_names = self.file.lower().replace("." + self.extension, "").split("_")    
        try:
            sub_name = sub_names[-1]
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        except IndexError:
            pass
        for sub_name in sub_names:
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        #sometimes the file name is like Dmc-de-de.wxl
        try:
            sub_name = self.file.lower()[-9:-4]
            if sub_name in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_name]
        except Exception:
            pass
        sub_dirs = self.directory.lower().split(os.sep)
        try:
            sub_dir = sub_dirs[-1]
            if sub_dir in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_dir]
        except IndexError:
            pass
        #Is the following necessary? Do we need to decide whether the other sub directory is language id besides the last sub directory?
        for sub_dir in sub_dirs:
            if sub_dir in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_dir]
        return BASE_LANGUAGE

    def get_group_id(self):
        #Maybe the most efficient way to get adjusted file name is sef.file[0:-9]
        sub_names = self.file.split(".")
        file_adjusted = ""
        for sub_name in sub_names:
            if not sub_name.lower() in STANDARDIZED_LANGUAGES.keys():
                file_adjusted += sub_name
        #sometimes the file name is like agee_zh-CN.wxl
        if "".join(sub_names) == file_adjusted:
            file_adjusted = ""
            sub_names = self.file.replace("." + self.extension, "").split("_")
            for sub_name in sub_names:
                if not sub_name.lower() in STANDARDIZED_LANGUAGES.keys():
                    file_adjusted += sub_name
            file_adjusted = file_adjusted + "." + self.extension
        #sometimes the file name is like Dmc-de-de.wxl
        if ("_".join(sub_names) + "." + self.extension) == file_adjusted:
            file_adjusted = self.file[0:-9]
        sub_dirs = self.directory.split(os.sep)
        dir_adjusted = sub_dirs
        index = 0
        for sub_dir in sub_dirs:
            if sub_dir.lower() in STANDARDIZED_LANGUAGES.keys():
                dir_adjusted.remove(sub_dir)
                break
            index += 1
        return file_adjusted, os.sep.join(dir_adjusted), index

    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            root = ET.fromstring(data)
            #escape_pattern = None # need to add whether there is an escape error, no need for now since parseError will be thrown in current implementation
            for elem in root.iter():
                if elem.tag.endswith("String"):
                    key = elem.get("Id")
                    if key is None:
                        continue
                    value = "".join(elem.itertext())
                    if key in self.keys:
                        self.duplicate_keys.append(key)
                    #if escape_pattern.match(value):
                    #    self.escape_error_keys.append(key)
                    self.keys.add(key)
                    self.values.append(value)
                    self.key_value_pairs[key] = value
                    self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class WxlResDetector(BaseResDetector):
    def get_placeholder_pattern(self):
        variable = PY.Word(PY.alphas + "_", PY.alphanums + "_")
        number = PY.Literal("0") | PY.Word("123456789", PY.nums)
        placeholder_pattern = PY.originalTextFor((PY.Literal("[") + (variable | number) + PY.Literal("]")) | (PY.Literal("{") + PY.Literal("\\") + variable + PY.Literal("}")))
        return placeholder_pattern
        

class StrResFile(BaseResFile):
    def get_language(self):
        sub_names = os.path.basename(self.directory).lower().split(".")
        if len(sub_names) > 1:
            language = sub_names[-2]
            if language in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[language]
            else:
                for language in sub_names:
                    if language in STANDARDIZED_LANGUAGES.keys():
                        return STANDARDIZED_LANGUAGES[language]
                return BASE_LANGUAGE
        else:
            return BASE_LANGUAGE

    def get_group_id(self):
        return self.file, os.path.dirname(self.directory)

    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            variable = PY.Word(PY.alphas + "_", PY.alphanums + "_")
            key_pattern = variable | PY.dblQuotedString
            value_pattern = PY.dblQuotedString
            key_value_pair = key_pattern + PY.Literal("=").suppress() + value_pattern + PY.Literal(";").suppress()
            escape_pattern = re.compile(".*(?<!\\\)\".*")
            for token, start_location, end_location in key_value_pair.ignore(PY.cppStyleComment).scanString(data):
                key = token[0]
                value = token[1]
                pure_value = value[1:-1]
                if key in self.keys:
                    self.duplicate_keys.append(key)
                if escape_pattern.match(pure_value):
                    self.escape_error_keys.append(key)
                self.keys.add(key)
                self.values.append(pure_value)
                self.key_value_pairs[key] = pure_value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class StrResDetector(BaseResDetector):
    def get_placeholder_pattern(self):
        #reference: http://pubs.opengroup.org/onlinepubs/009695399/functions/printf.html, https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/Strings/Articles/formatSpecifiers.html
        #can only detect placeholders, do not make sure they are legal
        positive_integer = PY.Word("123456789", PY.nums)
        index = positive_integer + PY.Literal("$")
        flags = PY.Word("'-+ #0")
        width = positive_integer | (PY.Literal("*") + PY.Optional(positive_integer + PY.Literal("$")))
        precision = PY.Literal(".") + width
        length_modifier = PY.Literal("hh") | PY.Literal("ll") | PY.Word("hljztqL", exact = 1)
        conversion_specifier = PY.Word("@sdiouUxXfFeEgGaAcpnCS%", exact = 1)
        placeholder_pattern = PY.originalTextFor(PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(flags) + PY.Optional(width) + PY.Optional(precision) + PY.Optional(length_modifier) + conversion_specifier))
        return placeholder_pattern


class XibResFile(StrResFile):
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            self.keys.add("KeyPlaceholder")
            self.values.append("ValuePlaceholder")
            self.key_value_pairs["KeyPlaceholder"] = "ValuePlaceholder"
            self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class XibResDetector(BaseResDetector):
    def get_detect_issues(self):
        if self.config.use_user_config:
            LOG.info("Reading issue types to be detected from configuration file...")
            self.detect_issues = getattr(self.config.config_module, self.config.detect_issues_attrs[self.res_file_type], [])
        else:
            LOG.info("Getting default issue types to be detected...")
            self.detect_issues = []


class XmlResFile(BaseResFile):
    def get_language(self):
        sub_names = os.path.basename(self.directory).lower().split("-")
        count = len(sub_names)
        if count == 1:
            return BASE_LANGUAGE
        elif count > 1:
            for i in range(1, count):
                language = sub_names[i]
                if language in STANDARDIZED_LANGUAGES.keys():
                    result = STANDARDIZED_LANGUAGES[language]
                    if i + 1 < count and sub_names[i + 1].startswith("r"):
                        language = sub_names[i] + "-" + sub_names[i + 1]
                        if language in STANDARDIZED_LANGUAGES.keys():
                            result = STANDARDIZED_LANGUAGES[language]
                    return result
            return BASE_LANGUAGE
        else:
            LOG.critical("A fatal error occurred when determining the language of file '{path}'".format(path = self.path))
            quit_application(-1)

    def get_group_id(self):
        sub_names = os.path.basename(self.directory).lower().split("-")
        base_name_adjusted = ""
        count = len(sub_names)
        region_flag = False
        for i in range(count):
            sub_name = sub_names[i]
            if (not sub_name in STANDARDIZED_LANGUAGES.keys()) and (not region_flag):
                base_name_adjusted += sub_name
            elif not region_flag:
                if i + 1 < count and sub_names[i + 1].startswith("r"):
                    language = sub_name + "-" + sub_names[i + 1]
                    if language in STANDARDIZED_LANGUAGES.keys():
                        region_flag = True
            else:
                region_flag = False
        return self.file, base_name_adjusted, os.path.dirname(self.directory)

    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            def get_value_info(value):
                if value and len(value) >1:
                    if value[0] == '"' and value[-1] == '"':
                        return value[1:-1], '"'
                    elif value[0] == "'" and value[-1] == "'":
                        return value[1:-1], "'"
                    else:
                        return value, None
                else:
                    return value, None
            root = ET.fromstring(data)
            #apostrophe_pattern = re.compile(".*(?<!\\\)'.*")
            #quote_pattern = re.compile(".*(?<!\\\)\".*")
            for elem in root.iter():
                if elem.tag == "string":
                    key = elem.get("name")
                    if key is None:
                        continue
                    value = "".join(elem.itertext())
                    pure_value, opener_closer = get_value_info(value)
                    if key in self.keys:
                        self.duplicate_keys.append(key)
                    #if (apostrophe_pattern.match(value) and (value[0] != "\"" or value[-1] != "\"")) or (quote_pattern.match(value) and (value[0] != "'" or value[-1] != "'")):
                        #self.escape_error_keys.append(key)
                    self.keys.add(key)
                    self.values.append(pure_value)
                    self.key_value_pairs[key] = pure_value
                    self.item_count += 1
                elif elem.tag == "string-array":
                    key_prefix = elem.get("name")
                    if key_prefix is None:
                        continue
                    index = 0
                    for sub_elem in elem.findall("item"):
                        key = key_prefix + "#" + str(index)
                        index = index + 1
                        value = "".join(sub_elem.itertext())
                        pure_value, opener_closer = get_value_info(value)
                        if key in self.keys:
                            self.duplicate_keys.append(key)
                        self.keys.add(key)
                        self.values.append(pure_value)
                        self.key_value_pairs[key] = pure_value
                        self.item_count += 1
                elif elem.tag == "plurals":
                    key_prefix = elem.get("name")
                    if key_prefix is None:
                        continue
                    for sub_elem in elem.findall("item"):
                        quantity = sub_elem.get("quantity")
                        if quantity is None:
                            continue
                        key = key_prefix + "#" + quantity
                        value = "".join(sub_elem.itertext())
                        pure_value, opener_closer = get_value_info(value)
                        if key in self.keys:
                            self.duplicate_keys.append(key)
                        self.keys.add(key)
                        self.values.append(pure_value)
                        self.key_value_pairs[key] = pure_value
                        self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class XmlResDetector(BaseResDetector):        
    def get_placeholder_pattern(self):
        #reference : http://blog.csdn.net/weiyijijing/article/details/8082366
        #need to check official document in future
        positive_integer = PY.Word("123456789", PY.nums)
        index = positive_integer + PY.Literal("$")
        sign = PY.Word("+- 0,(#<")
        string_pattern = PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Literal("s"))
        integer_pattern = PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(sign) + PY.Optional(positive_integer) + PY.Word("doxX", exact = 1))
        float_pattern = PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(sign) + PY.Optional(positive_integer) + PY.Optional("." + positive_integer) + PY.Word("eEfgGaA", exact = 1))
        character_pattern = PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(PY.Literal("-")) + PY.Literal("c"))
        percent_pattern = PY.Literal("%%")
        newline_pattern = PY.Literal("%n")
        time_pattern = PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Literal("t") + PY.Word("cFDrTRHIklMSLNpzZsQBbhAaCYyjmde", exact = 1))
        placeholder_pattern = PY.originalTextFor(string_pattern | percent_pattern | newline_pattern | integer_pattern | float_pattern | character_pattern | time_pattern)
        return placeholder_pattern

class ProResFile(BaseResFile):
    def get_language(self):
        pure_name_end = 0 - len(".properties")
        sub_names = self.file[0:pure_name_end].lower().split("_")
        count = len(sub_names)
        if count == 1:
            if sub_names[0] in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[sub_names[0]]
            return BASE_LANGUAGE
        elif count > 1:
            language = sub_names[-2] + "-" + sub_names[-1]
            if language in STANDARDIZED_LANGUAGES.keys():
                return STANDARDIZED_LANGUAGES[language]
            else:
                language = sub_names[-1]
                if language in STANDARDIZED_LANGUAGES.keys():
                    return STANDARDIZED_LANGUAGES[language]
                else:
                    return BASE_LANGUAGE
        else:
            LOG.critical("A fatal error occurred when determining the language of file '{path}'".format(path = self.path))
            quit_application(-1)
            
    def get_group_id(self):
        pure_name_end = 0 - len(".properties")
        sub_names = self.file[0:pure_name_end].lower().split("_")
        file_adjusted = ""
        count = len(sub_names)
        if count == 1:
            if sub_names[0] not in STANDARDIZED_LANGUAGES.keys():
                file_adjusted = sub_names[0]
        elif count > 1:
            language = sub_names[-2] + "-" + sub_names[-1]
            if language in STANDARDIZED_LANGUAGES.keys():
                file_adjusted = "_".join(sub_names[0:-2])
            else:
                language = sub_names[-1]
                if language in STANDARDIZED_LANGUAGES.keys():
                    file_adjusted = "_".join(sub_names[0:-1])
                else:
                    file_adjusted = "_".join(sub_names[0:])
        else:
            LOG.critical("A fatal error occurred when determining the language of file '{path}'".format(path = self.path))
            quit_application(-1)
        return file_adjusted, self.directory
    
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            normal_white_spaces = " \t\f"
            white_spaces = " \t\f\r\n"
            comment_starts = "#!"
            key_terminators = ":=" + normal_white_spaces
            class LineType(Enum):
                comment =   0
                blank   =   1
                natural =   2
                logic   =   3
            def is_escape_character(line_string, index):
                if index < 0:
                    return False
                if line_string[index] != "\\":
                    return False
                index -= 1
                backslash_count = 1
                while index >= 0 and line_string[index] == "\\":
                    index -= 1
                    backslash_count += 1
                if backslash_count % 2:
                    return True
                else:
                    return False
            def get_line_information(line_string):
                line_type = None
                pure_len = len(line_string)
                for char in line_string:
                    if char not in white_spaces:
                        if char in comment_starts:
                            line_type = LineType.comment
                        else:
                            if line_string.endswith("\r\n"):
                                if is_escape_character(line_string, pure_len - 3):
                                    line_type = LineType.logic
                                    pure_len -= 3
                                    if line_string.lstrip(normal_white_spaces) == "\\\r\n":
                                        line_type = LineType.blank
                                        pure_len = 0
                                else:
                                    line_type = LineType.natural
                                    pure_len -= 2
                            elif line_string.endswith("\n") or line_string.endswith("\r"):
                                if is_escape_character(line_string, pure_len - 2):
                                    line_type = LineType.logic
                                    pure_len -= 2
                                    tailing_line_string = line_string.lstrip(normal_white_spaces)
                                    if tailing_line_string == "\\\n" or tailing_line_string == "\\\r":
                                        line_type = LineType.blank
                                        pure_len = 0
                                else:
                                    line_type = LineType.natural
                                    pure_len -= 1
                            else:
                                raise Exception("Unexpected line end detected")
                        break
                else:
                    line_type = LineType.blank
                    pure_len = 0
                return line_type, pure_len
            def parse_start_from_key(line_string, pure_len):
                key_start = 0
                value_end = 0
                value = ""
                is_key_uncompleted = False
                while key_start < pure_len:
                    if line_string[key_start] not in normal_white_spaces:
                        break
                    key_start += 1
                else:
                    raise Exception("No non-whitespace character found, this should not happen")
                key_end = key_start
                while key_end < pure_len:
                    if (line_string[key_end] in key_terminators) and (not is_escape_character(line_string, key_end - 1)):
                        break
                    key_end += 1
                else:
                    is_key_uncompleted = True
                    return line_string[key_start:key_end], value, is_key_uncompleted
                value_start = key_end
                symbol_not_found = True
                while value_start < pure_len:
                    if line_string[value_start] in normal_white_spaces:
                        value_start += 1
                    elif symbol_not_found and line_string[value_start] in "=:":
                        symbol_not_found = False
                        value_start += 1
                    else:
                        break
                if value_start == pure_len:
                    value_start = 0
                    value_end = 0
                else:
                    value_end = pure_len
                return line_string[key_start:key_end], line_string[value_start:value_end], is_key_uncompleted
            def parse_start_from_value(line_string, pure_len):
                value_start = 0
                value_end = 0
                while value_start < pure_len:
                    if line_string[value_start] in normal_white_spaces:
                        value_start += 1
                    else:
                        break
                if value_start == pure_len:
                    raise Exception("No non-whitespace character found, this should not happen")
                else:
                    value_end = pure_len
                return line_string[value_start:value_end]
            line_strings = data.splitlines(keepends = True)
            if not (line_strings[-1].endswith("\n") or line_strings[-1].endswith("\r")):
                line_strings[-1] += "\n"
            line_count = len(line_strings)
            line_index = 0
            last_line_type = LineType.natural
            is_key_uncompleted = True
            key = ""
            value = ""
            while line_index < line_count:
                line_string = line_strings[line_index]
                line_type, pure_len = get_line_information(line_string)
                if line_type == LineType.blank:
                    line_index += 1
                elif line_type == LineType.comment:
                    line_index += 1
                elif line_type == LineType.natural:
                    if last_line_type == LineType.natural:
                        key, value, is_key_uncompleted = parse_start_from_key(line_string, pure_len)
                        if key in self.keys:
                            self.duplicate_keys.append(key)
                        self.keys.add(key)
                        self.values.append(value)
                        self.key_value_pairs[key] = value
                        self.item_count += 1
                    elif last_line_type == LineType.logic:
                        if is_key_uncompleted:
                            partial_key, value, is_key_uncompleted = parse_start_from_key(line_string, pure_len)
                            key += partial_key
                            if key in self.keys:
                                self.duplicate_keys.append(key)
                            self.keys.add(key)
                            self.values.append(value)
                            self.key_value_pairs[key] = value
                            self.item_count += 1
                        else:
                            partial_value = parse_start_from_value(line_string, pure_len)
                            value += partial_value
                            if key in self.keys:
                                self.duplicate_keys.append(key)
                            self.keys.add(key)
                            self.values.append(value)
                            self.key_value_pairs[key] = value
                            self.item_count += 1
                    else:
                        raise Exception("Unexpected line type")
                    last_line_type = LineType.natural
                    line_index += 1
                elif line_type == LineType.logic:
                    if last_line_type == LineType.natural:
                        key, value, is_key_uncompleted = parse_start_from_key(line_string, pure_len)
                    elif last_line_type == LineType.logic:
                        if is_key_uncompleted:
                            partial_key, value, is_key_uncompleted = parse_start_from_key(line_string, pure_len)
                            key += partial_key
                        else:
                            partial_value = parse_start_from_value(line_string, pure_len)
                            value += partial_value
                    else:
                        raise Exception("Unexpected line type")
                    last_line_type = LineType.logic
                    line_index += 1
                else:
                    raise Exception("Unexpected line type, this should not happen")
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return

class ProResDetector(BaseResDetector):    
    #[TODO]http://docs.oracle.com/javase/tutorial/i18n/format/messageFormat.html, http://docs.oracle.com/javase/8/docs/api/java/text/MessageFormat.html
    def get_placeholder_pattern(self):
        return PY.Literal("{").suppress() + PY.Word(PY.nums) + PY.Literal("}").suppress()
    

class PoResFile(BaseResFile):  
    #reference: http://pology.nedohodnik.net/doc/user/en_US/ch-poformat.html & http://www.gnu.org/software/gettext/manual/html_node/index.html
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            #TODO Support plurals 
            string_pattern = PY.OneOrMore(PY.dblQuotedString.copy()).setParseAction(lambda s, l, t: "".join([i[1:-1] for i in t]))
            key_value_pair = PY.Optional(PY.Literal("msgctxt").suppress() + string_pattern) + PY.Literal("msgid").suppress() + string_pattern + PY.Literal("msgstr").suppress() + string_pattern
            for tokens, start, end in key_value_pair.ignore(PY.pythonStyleComment).parseWithTabs().scanString(data):
                if len(tokens) == 3:
                    key = tokens[0] + "#" + tokens[1]
                    value = tokens[2]
                else:
                    key = tokens[0]
                    value = tokens[1]                
                if key in self.keys:
                    self.duplicate_keys.append(key)
                self.keys.add(key)
                self.values.append(value)
                self.key_value_pairs[key] = value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class PoResDetector(BaseResDetector):
    #Since only this function is overrided and the logic is the same as that in StrResDetector, this class can derive StrResDetector to reuse code
    def get_placeholder_pattern(self):
        #reference: http://pubs.opengroup.org/onlinepubs/009695399/functions/printf.html
        positive_integer = PY.Word("123456789", PY.nums)
        index = positive_integer + PY.Literal("$")
        flags = PY.Word("'-+ #0")
        width = positive_integer | (PY.Literal("*") + PY.Optional(positive_integer + PY.Literal("$")))
        precision = PY.Literal(".") + width
        length_modifier = PY.Literal("hh") | PY.Literal("ll") | PY.Word("hljztqL", exact = 1)
        conversion_specifier = PY.Word("@sdiouUxXfFeEgGaAcpnCS%", exact = 1)
        placeholder_pattern = PY.originalTextFor(PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(flags) + PY.Optional(width) + PY.Optional(precision) + PY.Optional(length_modifier) + conversion_specifier))
        return placeholder_pattern
    

class TokResFile(BaseResFile):
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            digit_value = PY.Word(string.digits + string.punctuation + string.whitespace).leaveWhitespace().parseWithTabs()
            key_value_pair = PY.originalTextFor(PY.Literal("[[") + (PY.Word(PY.nums) + PY.Literal("|")) * 5 + PY.dblQuotedString + PY.Literal("]]")) + PY.Literal("=").suppress() + PY.SkipTo(PY.lineEnd)
            for tokens, start, end in key_value_pair.parseWithTabs().scanString(data):
                key = tokens[0]
                value = tokens[1]
                if not value:
                    continue    
                try:
                    digit_value.parseString(value, parseAll = True)
                except PY.ParseException:
                    pass
                else:
                    continue            
                if key in self.keys:
                    self.duplicate_keys.append(key)
                self.keys.add(key)
                self.values.append(value)
                self.key_value_pairs[key] = value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return
        

class TokResDetector(BaseResDetector):
    #Since only this function is overrided and the logic is the same as that in StrResDetector, this class can derive StrResDetector to reuse code
    def get_placeholder_pattern(self):
        #reference: http://pubs.opengroup.org/onlinepubs/009695399/functions/printf.html
        positive_integer = PY.Word("123456789", PY.nums)
        index = positive_integer + PY.Literal("$")
        flags = PY.Word("'-+ #0")
        width = positive_integer | (PY.Literal("*") + PY.Optional(positive_integer + PY.Literal("$")))
        precision = PY.Literal(".") + width
        length_modifier = PY.Literal("hh") | PY.Literal("ll") | PY.Word("hljztqL", exact = 1)
        conversion_specifier = PY.Word("@sdiouUxXfFeEgGaAcpnCS%", exact = 1)
        placeholder_pattern = PY.originalTextFor(PY.Combine(PY.Literal("%") + PY.Optional(index) + PY.Optional(flags) + PY.Optional(width) + PY.Optional(precision) + PY.Optional(length_modifier) + conversion_specifier))
        return placeholder_pattern


class JsResFile(BaseResFile):
    def get_language(self):
        base_name = os.path.basename(self.directory).lower()
        if base_name == "root":
            return BASE_LANGUAGE
        elif base_name in STANDARDIZED_LANGUAGES.keys():
            return STANDARDIZED_LANGUAGES[base_name]
        else:
            LOG.critical("'{language}' is not pre-defined in {application}, please contact tool author".format(language = base_name, application = __application__))
            quit_application(-1)

    def get_group_id(self):
        return self.file, os.path.dirname(self.directory)

    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        try:
            key_pattern = (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t))
            value_pattern = PY.SkipTo((PY.Literal(",") | PY.Literal("\r\n") | PY.Literal("}")), include = False, ignore = PY.quotedString|PY.cppStyleComment).setParseAction(lambda t: t[0].rstrip("\r\n").rstrip(",").strip(" \t"))
            comment = PY.cppStyleComment
            key_value_pattern = (key_pattern | (PY.Literal("\"").suppress() + key_pattern + PY.Literal("\"").suppress()) | (PY.Literal("'").suppress() + key_pattern + PY.Literal("'").suppress())) + PY.Literal(":").suppress() + value_pattern
            escape_pattern = re.compile("'.*(?<!\\\)'.*'|\".*(?<!\\\)\".*\"")
            for tokens, start, end in key_value_pattern.ignore(comment).scanString(data):
                key = tokens[0]
                value = tokens[1]
                pure_value = value[1:-1]
                if key in self.keys:
                    self.duplicate_keys.append(key)
                if escape_pattern.match(value):
                    if not "+" in value:
                        self.escape_error_keys.append(key)
                    else:
                        for sub_string in value.split("+"):
                            if escape_pattern.match(sub_string.strip(" \t")):
                                self.escape_error_keys.append(key)
                self.keys.add(key)
                self.values.append(pure_value)
                self.key_value_pairs[key] = pure_value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return


class JsResDetector(BaseResDetector):
    def get_placeholder_pattern(self):
        return PY.Combine(PY.Literal("#").suppress() + PY.Word(PY.alphanums, PY.alphanums + "-") + PY.Literal("#").suppress())

    def get_res_keys_and_src_keys(self):
        res_keys = set()
        for res_file_group in self.res_file_groups:
            if res_file_group.base_res_file:
                res_keys = res_keys | res_file_group.base_res_file.keys                               
        src_keys = set()
        src_key_info = []
        res_folder_pattern = os.sep + "nls" + os.sep
        for root, dirs, files in os.walk(self.src_dir):
            if not res_folder_pattern in (root + os.sep):
                for file in files:
                    for extension in ["js", "htm", "html"]:
                        if file.endswith(extension):
                            src_file = BaseSrcFile(root, file, extension)
                            for key, start, end in src_file.get_resource_keys():
                                src_keys.add(key)
                                src_key_info.append((key, src_file, start, end))
        return res_keys, src_keys, src_key_info

    def detect_unused_and_undefined_keys(self):
        detect_unused_key = True if IssueName.unused_key.value in self.detect_issues else False
        detect_improper_used_key = True if IssueName.improperly_used_key.value in self.detect_issues else False
        if detect_unused_key:
            LOG.info("Detecting unused keys in resource files, which may take some time...")
            res_keys, src_keys, src_key_info = self.get_res_keys_and_src_keys()
        elif detect_improper_used_key:
            LOG.info("Detecting undefined resource keys in source code, which may take some time...")
            res_keys, src_keys, src_key_info = self.get_res_keys_and_src_keys()
        else:
            return
        if detect_unused_key:
            for res_file_group in self.res_file_groups:
                base_res_file = res_file_group.base_res_file
                if not base_res_file:
                    continue
                missing_keys = base_res_file.keys - src_keys
                for missing_key in sorted(missing_keys):
                    issue = Issue(file = base_res_file.path, line = 0, column_begin = 0, column_begin_offset = 0, column_end = 0, code = IssueCode.unused_key, description = Description.unused_key, severity = Severity.warning, context = Context.unused_key.value.format(missing_key))
                    self.issues.add(issue)
        if detect_improper_used_key:
            if detect_unused_key:
                LOG.info("Detecting undefined resource keys in source code...")
            for key, src_file, start, end in src_key_info:
                if not key in res_keys:
                    column_begin, column_begin_offset = src_file.get_column_number_with_offset(start)
                    issue = Issue(file = src_file.path, line = src_file.get_line_number(start), column_begin = column_begin, column_begin_offset = column_begin_offset, column_end = src_file.get_column_number(end), code = IssueCode.improperly_used_key, description = Description.improperly_used_key, severity = Severity.error, context = Context.improperly_used_key.value.format(src_file.get_line(start).strip("\r")))
                    self.issues.add(issue)

class JsonResFile(BaseResFile):    
    def parse(self, parsing_patterns = None):
        data = self.read()
        if not data:
            LOG.warning("There is no data in file '{path}'".format(path = self.path))
            return
        def flat_dict(prefix, json_dict):
            for key, value in json_dict.items():
                key = key if not prefix else prefix + "." + key
                if type(value) == str:
                    yield key, value
                elif type(value) == dict:
                    for sub_key, sub_value in flat_dict(key, value):
                        yield sub_key, sub_value
                else:
                    LOG.warning("Non-dict/str type found when getting key-value pairs from json file '{path}'".format(path = self.path))
        try:
            for key, value in flat_dict("", json.loads(data)):
                if key in self.keys:
                    self.duplicate_keys.append(key)
                self.keys.add(key)
                self.values.append(value)
                self.key_value_pairs[key] = value
                self.item_count += 1
        except Exception as e:
            LOG.error("An error occurred when parsing key-value pairs from file '{path}': {exception}".format(path = self.path, exception = e))
            self.reset_value_containers()
            return

class JsonResDetector(BaseResDetector):
    def get_placeholder_pattern(self):
        return PY.Literal("{").suppress() + PY.Word(PY.nums) + PY.Literal("}").suppress()

class BaseSrcFile:
    def __init__(self, directory, file, extension):
        self.directory = directory
        self.file = file
        self.extension = extension
        self.path = os.path.join(directory, file)
        self.code = self.read()

    def read(self):
        try:
            f = open(self.path, "rb")
            bin_data = f.read()
            f.close()
        except Exception as e:
            LOG.error("Cannot open file '{path}' to read: {exception}".format(path = self.path, exception = e))
            return None
        for bom, encoding in {codecs.BOM_UTF8 : "utf_8", codecs.BOM_UTF16_BE : "utf_16_be", codecs.BOM_UTF16_LE : "utf_16_le", codecs.BOM_UTF32_BE : "utf_32_be", codecs.BOM_UTF32_LE : "utf_32_le"}.items():
            if bin_data.startswith(bom):
                try:
                    return bin_data[len(bom):].decode(encoding)
                except UnicodeDecodeError:
                    LOG.error("Cannot read file '{path}', the real encoding is not the same as {encoding} encoding detected by BOM".format(path = self.path, encoding = encoding))
                    return None
        try:
            return bin_data.decode("utf_8")
        except UnicodeDecodeError:
            pass
        try:
            return bin_data.decode("cp1252")
        except UnicodeDecodeError:
            pass
        try:
            return bin_data.decode(locale.getpreferredencoding())
        except UnicodeDecodeError:
            LOG.error("Cannot read file '{path}', encoding is unknown".format(path = self.path))
            return None
    
    def get_line_number(self, location):
        return self.code.count("\n", 0, location) + 1

    def get_column_number(self, location):
        try:
            if self.code[location] == "\n":
                return 1
            else:
                return location - self.code.rfind("\n", 0, location)
        except IndexError:
            return 0

    def get_column_number_with_offset(self, location):
        try:
            if self.code[location] == "\n":
                return 1, 0
            else:
                column_start = self.code.rfind("\n", 0, location) 
                return location - column_start, self.code.count("\t", column_start + 1, location) * (TAB_WIDTH - 1)
        except IndexError:
            return 0, 0
        
    def get_code_snippet(self, start, end):
        return self.code[start:end]

    def get_line(self, location):
        last_new_line = self.code.rfind("\n", 0, location)
        next_new_line = self.code.find("\n", location)
        if next_new_line >= 0:
            return self.code[(last_new_line + 1):next_new_line]
        else:
            return self.code[(last_new_line + 1):]

    def get_resource_keys(self):
        if not self.code:
            return None
        target = None        
        if self.extension == "js":
            #resource_key = (((PY.Literal("Locale") + PY.Optional(PY.Word(PY.alphas))) | PY.Literal("html")) + PY.Literal(".")).suppress() + (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t)) + PY.NotAny(PY.Word(PY.alphanums + "_")).suppress()
            resource_key = ((PY.CaselessLiteral("locale") + PY.Optional(PY.Word(PY.alphanums + "_")) + PY.Literal(".") + PY.Optional(PY.Word(PY.alphas) + PY.Literal("."))) | (PY.Literal("html") + PY.Literal("."))).suppress() + (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t)) + PY.NotAny(PY.Word(PY.alphanums + "_")).suppress()
            #resource_key = ((PY.Literal("getLocalizationData()") + PY.Literal(".") + PY.Word(PY.alphas)) | (PY.Word(PY.alphas) + PY.Literal(".") + PY.Optional(PY.Word(PY.alphas) + PY.Literal(".")))).suppress() + (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t)) + PY.NotAny(PY.Word(PY.alphanums + "_")).suppress()
            comment = PY.cppStyleComment
            string_parser = PY.quotedString
            target = resource_key.ignore(comment | string_parser).parseWithTabs()
        elif self.extension == "htm" or self.extension == "html":
            resource_key = (PY.Literal("{") *(2, 3)).suppress() + (PY.Literal("Locale.") | PY.Literal("html.") | PY.Literal("locale.html.")).suppress() + (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t)) + (PY.Literal("}") *(2, 3)).suppress()
            #resource_key = (PY.Word(PY.alphanums + "_") + PY.Literal(".")).suppress() + (PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_") + PY.ZeroOrMore(PY.Literal("_") + PY.Word(string.ascii_uppercase, string.ascii_uppercase + PY.nums + "_"))).setParseAction(lambda t: "".join(t))
            comment = PY.htmlComment
            target = resource_key.ignore(comment).parseWithTabs() 
        else:
            pass
            #target = PY.NoMatch
        for tokens, start, end in target.scanString(self.code):
            yield tokens[0], start, end


class Configuration:
    def __init__(self, dir_input):
        self.config_module_dir = dir_input
        self.config_file_name = "resource_detector_config.py"
        self.config_module_name = "resource_detector_config"
        self.config_file_path = os.path.join(self.config_module_dir, self.config_file_name)
        self.config_module = self.get_config_module()
        self.use_user_config = True if self.config_module else False
        self.support_res_exts = ["resx", "resw", "rc", "rc2", "mc", "wxl", "strings", "xml", "js", "properties", "po", "tok", "xib", "json"]
        self.support_res_types = ["resx", "resw", "rc", "rc2", "mc", "wxl", "strings", "xml", "js", "properties", "po", "tok", "xib", "json"]
        self.detector_switch_attrs = \
        {
         "resx"                 : "USE_RESX_DETECTOR", 
         "resw"                 : "USE_RESW_DETECTOR", 
         "rc"                   : "USE_RC_DETECTOR", 
         "rc2"                  : "USE_RC2_DETECTOR", 
         "mc"                   : "USE_MC_DETECTOR", 
         "wxl"                  : "USE_WXL_DETECTOR", 
         "strings"              : "USE_STR_DETECTOR", 
         "xml"                  : "USE_XML_DETECTOR", 
         "js"                   : "USE_JS_DETECTOR", 
         "properties"           : "USE_PRO_DETECTOR", 
         "po"                   : "USE_PO_DETECTOR", 
         "tok"                  : "USE_TOK_DETECTOR", 
         "xib"                  : "USE_XIB_DETECTOR",
         "json"                 : "USE_JSON_DETECTOR",
        }
        self.detect_issues_attrs = \
        {
         "resx"                 : "RESX_DETECT_ISSUES", 
         "resw"                 : "RESW_DETECT_ISSUES", 
         "rc"                   : "RC_DETECT_ISSUES", 
         "rc2"                  : "RC2_DETECT_ISSUES", 
         "mc"                   : "MC_DETECT_ISSUES", 
         "wxl"                  : "WXL_DETECT_ISSUES", 
         "strings"              : "STR_DETECT_ISSUES", 
         "xml"                  : "XML_DETECT_ISSUES", 
         "js"                   : "JS_DETECT_ISSUES", 
         "properties"           : "PRO_DETECT_ISSUES", 
         "po"                   : "PO_DETECT_ISSUES", 
         "tok"                  : "TOK_DETECT_ISSUES", 
         "xib"                  : "XIB_DETECT_ISSUES",
         "json"                 : "JSON_DETECT_ISSUES",
        }
        self.fixed_res_groups_attrs = \
        {
         "resx"                 : "USE_FIXED_RESX_RES_FILE_GROUPS", 
         "resw"                 : "USE_FIXED_RESW_RES_FILE_GROUPS", 
         "rc"                   : "USE_FIXED_RC_RES_FILE_GROUPS", 
         "rc2"                  : "USE_FIXED_RC2_RES_FILE_GROUPS", 
         "mc"                   : "USE_FIXED_MC_RES_FILE_GROUPS", 
         "wxl"                  : "USE_FIXED_WXL_RES_FILE_GROUPS", 
         "strings"              : "USE_FIXED_STR_RES_FILE_GROUPS", 
         "xml"                  : "USE_FIXED_XML_RES_FILE_GROUPS", 
         "js"                   : "USE_FIXED_JS_RES_FILE_GROUPS", 
         "properties"           : "USE_FIXED_PRO_RES_FILE_GROUPS", 
         "po"                   : "USE_FIXED_PO_RES_FILE_GROUPS", 
         "tok"                  : "USE_FIXED_TOK_RES_FILE_GROUPS", 
         "xib"                  : "USE_FIXED_XIB_RES_FILE_GROUPS",
         "json"                 : "USE_FIXED_JSON_RES_FILE_GROUPS",
        }
        self.res_groups_attrs = \
        {
         "resx"                 : "RESX_RES_FILE_GROUPS", 
         "resw"                 : "RESW_RES_FILE_GROUPS", 
         "rc"                   : "RC_RES_FILE_GROUPS", 
         "rc2"                  : "RC2_RES_FILE_GROUPS", 
         "mc"                   : "MC_RES_FILE_GROUPS", 
         "wxl"                  : "WXL_RES_FILE_GROUPS", 
         "strings"              : "STR_RES_FILE_GROUPS", 
         "xml"                  : "XML_RES_FILE_GROUPS", 
         "js"                   : "JS_RES_FILE_GROUPS", 
         "properties"           : "PRO_RES_FILE_GROUPS", 
         "po"                   : "PO_RES_FILE_GROUPS", 
         "tok"                  : "TOK_RES_FILE_GROUPS", 
         "xib"                  : "XIB_RES_FILE_GROUPS",
         "json"                 : "JSON_RES_FILE_GROUPS",
        }
        self.detect_languages_attrs = \
        {
         "resx"                 : "RESX_DETECT_LANGUAGES", 
         "resw"                 : "RESW_DETECT_LANGUAGES", 
         "rc"                   : "RC_DETECT_LANGUAGES", 
         "rc2"                  : "RC2_DETECT_LANGUAGES", 
         "mc"                   : "MC_DETECT_LANGUAGES", 
         "wxl"                  : "WXL_DETECT_LANGUAGES", 
         "strings"              : "STR_DETECT_LANGUAGES", 
         "xml"                  : "XML_DETECT_LANGUAGES", 
         "js"                   : "JS_DETECT_LANGUAGES", 
         "properties"           : "PRO_DETECT_LANGUAGES", 
         "po"                   : "PO_DETECT_LANGUAGES", 
         "tok"                  : "TOK_DETECT_LANGUAGES", 
         "xib"                  : "XIB_DETECT_LANGUAGES",
         "json"                 : "JSON_DETECT_LANGUAGES",
        }
        self.detector_classes = \
        {
         "resx"                 : ResxResDetector, 
         "resw"                 : ReswResDetector, 
         "rc"                   : RcResDetector, 
         "rc2"                  : Rc2ResDetector, 
         "mc"                   : McResDetector, 
         "wxl"                  : WxlResDetector, 
         "strings"              : StrResDetector, 
         "xml"                  : XmlResDetector, 
         "js"                   : JsResDetector, 
         "properties"           : ProResDetector, 
         "po"                   : PoResDetector, 
         "tok"                  : TokResDetector, 
         "xib"                  : XibResDetector,
         "json"                 : JsonResDetector,
         }
        self.res_file_classes = \
        {
         "resx"                 : ResxResFile, 
         "resw"                 : ReswResFile, 
         "rc"                   : RcResFile, 
         "rc2"                  : Rc2ResFile, 
         "mc"                   : McResFile, 
         "wxl"                  : WxlResFile, 
         "strings"              : StrResFile, 
         "xml"                  : XmlResFile, 
         "js"                   : JsResFile, 
         "properties"           : ProResFile, 
         "po"                   : PoResFile, 
         "tok"                  : TokResFile, 
         "xib"                  : XibResFile,
         "json"                 : JsonResFile,
         }
        self.default_detect_issues = {issue_name.value for issue_name in IssueName if issue_name != IssueName.untranslated_value}
        self.ignore_issues_attr = "IGNORE_ISSUES"
   
    def get_config_module(self):
        if not os.path.isfile(self.config_file_path):
            return None
        if not self.config_module_dir in sys.path:
            sys.path.insert(0, self.config_module_dir)
        if not self.config_module_name in sys.modules:
            try:
                config = importlib.__import__(self.config_module_name)
                del sys.path[0]
                return config
            except ImportError as ie:
                del sys.path[0]
                LOG.critical("Cannot import configuration file: {import_error}".format(import_error = ie))
                quit_application(-1)
            except Exception as e:
                del sys.path[0]
                LOG.critical("Cannot import configuration file: {exception}".format(exception = e))
                quit_application(-1)   


class ResourceDetector:
    def __init__(self, arguments):
        self.args = arguments
        self.src_dir = self.get_absolute_path(arguments.directory)
        self.res_files = {}
        self.res_file_count = 0
        self.issues = Issues()
        self.begin_time = datetime.utcnow()
        self.end_time = datetime.utcnow()
        self.file_count = 0
        self.item_count = 0
        self.config = Configuration(self.src_dir)

    def get_absolute_path(self, dir_input):
        scan_dir = os.path.abspath(dir_input)
        if not os.path.isdir(scan_dir):
            LOG.critical("The input scan directory '{directory}' is not valid, please have a check".format(directory = scan_dir))
            quit_application(-1)
        return scan_dir
    
    def run(self):
        if self.args.generate_config:
            self.write_configuration()
        else:
            self.detect()
            self.filter_issues()
            self.end_time = datetime.utcnow()
            self.display_summary_result()
            self.write_result_for_user() 
            self.write_result_for_ignoring()
            self.write_result_for_platform()
    
    def get_resource_files(self):
        LOG.info("Filtering resource files in '{directory}'...".format(directory = self.src_dir))
        for res_type in self.config.support_res_types:
            self.res_files[res_type] = []
        res_file_count = 0
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                self.file_count += 1
                for ext in self.config.support_res_exts:
                    if file.endswith("." + ext):
                        if ext == "xml":
                            if "values" in os.path.basename(root):
                                self.res_files[ext].append(self.config.res_file_classes[ext](root, file, ext))
                            else:
                                continue
                        elif ext == "js":
                            if os.path.dirname(root).endswith("nls"):
                                self.res_files[ext].append(self.config.res_file_classes[ext](root, file, ext))
                            else:
                                continue
                        elif ext == "json":
                            if ("locales" == os.path.basename(root)) or ("_locales" in root.lower().split(os.sep)):
                                self.res_files[ext].append(self.config.res_file_classes[ext](root, file, ext))
                            else:
                                continue
                        else:
                            self.res_files[ext].append(self.config.res_file_classes[ext](root, file, ext))
                        res_file_count += 1
        LOG.info("Filtered {0} resource files from {1} files".format(res_file_count, self.file_count))
    
    def detect(self):
        LOG.info("Start running {application} to scan '{src_dir}'".format(application = __application__, src_dir = self.src_dir))
        if self.config.use_user_config:
            self.get_resource_files()
            LOG.info("Configuration file '{config_file}' exists, start detecting with this configuration file".format(config_file = self.config.config_file_path))
            LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
            for res_type in self.config.support_res_types:
                res_files = self.res_files.get(res_type)
                if not res_files:
                    continue
                try:
                    detector_switch = getattr(self.config.config_module, self.config.detector_switch_attrs[res_type])
                    if detector_switch == True:
                        try:
                            LOG.info("Start running {res_type} {application} with configuration".format(res_type = res_type, application = __application__))
                            res_detector = self.config.detector_classes[res_type](self.src_dir, res_files, self.config, res_type)
                            res_detector.detect()
                            self.issues.extend(res_detector.issues)
                            self.item_count += res_detector.item_count
                            self.res_file_count += res_detector.res_file_count
                            LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                        except Exception as e:
                            LOG.critical("An error occurred when running {res_type} {application}: {exception}".format(res_type = res_type, application = __application__, exception = e))
                            LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                            quit_application(-1)
                except AttributeError:
                    pass
        else:
            self.get_resource_files()
            LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
            for res_type in self.config.support_res_types:
                res_files = self.res_files.get(res_type)
                if res_files:
                    try:
                        LOG.info("Start running {res_type} {application}".format(res_type = res_type, application = __application__))
                        res_detector = self.config.detector_classes[res_type](self.src_dir, res_files, self.config, res_type)
                        res_detector.detect()
                        self.issues.extend(res_detector.issues)
                        self.item_count += res_detector.item_count
                        self.res_file_count += res_detector.res_file_count
                        LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                    except Exception as e:
                        LOG.critical("An error occurred when running {res_type} {application}: {exception}".format(res_type = res_type, application = __application__, exception = e))
                        LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                        quit_application(-1)
        
    def write_configuration(self):
        LOG.info("Start generating a new configuration file: '{config_file}'".format(config_file = self.config.config_file_path))
        try:
            output_file = open(file = self.config.config_file_path, mode = "w", encoding = "utf_8_sig")
        except Exception as e:
            LOG.critical("Cannot open '{config_file}' to write configuration content: {exception}".format(config_file = self.config.config_file_path, exception = e))
            quit_application(-1)
        self.get_resource_files()
        LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
        try:
            output_file.write("# !/usr/bin/env python\n# -*- coding: utf-8 -*-\n")
            output_file.write("# configuration file generated time(utc): {time_now}\n\n\n".format(time_now = datetime.utcnow()))
            output_file.close()
        except Exception as e:
            LOG.critical("An error occurred when writing configuration to '{config_file}': {exception}".format(config_file = self.config.config_file_path, exception = e))
            quit_application(-1)
        for res_type in self.config.support_res_types:
            res_files = self.res_files.get(res_type)
            if res_files:
                try:
                    LOG.info("Start writing configuration related to {res_type} files".format(res_type = res_type))
                    res_detector = self.config.detector_classes[res_type](self.src_dir, res_files, self.config, res_type)
                    res_detector.write_configuration()
                    LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                except Exception as e:
                    LOG.critical("An error occurred when writing configuration related to {ext} files: {exception}".format(ext = res_type, exception = e))
                    LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
                    quit_application(-1)
        try:
            output_file = open(file = self.config.config_file_path, mode = "a", encoding = "utf_8_sig")
            output_file.write("#Copy the issues you want to ignore from detection result to the set, each issue item should be like the example below: R'''issue''',\n")
            output_file.write("#You can also use -i option to generate the ignore issue patterns which can be directly copied and used here\n")
            output_file.write("{ignore_issues_attr} =\\\n".format(ignore_issues_attr = self.config.ignore_issues_attr) + "{\n")
            output_file.write("#R'''{issue_string}''',\n".format(issue_string = R"D:\Code\TestCode\StudioArthur\Installers\Console\LocalizedResources\zh-cn.wxl, 0, 0, unmatched placeholder(s) in localized resource file, error, key=WelcomeEulaDlg_Title, value=[ProductName] 安装程序"))
            output_file.write("}")
            output_file.close()
        except Exception as e:
            LOG.critical("Cannot open '{config_file}' to write configuration content: {exception}".format(config_file = self.config.config_file_path, exception = e))
            quit_application(-1)
        LOG.info("Configuration file '{config_file}' has been generated, customize it and run {application} again".format(config_file = self.config.config_file_path, application = __application__))

    def filter_issues(self):
        if not self.config.use_user_config:
            return
        ignore_issues = getattr(self.config.config_module, self.config.ignore_issues_attr, set())
        if not ignore_issues:
            return
        LOG.info("Filtering detected issues...")
        LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
        remaining_issues = Issues()
        for issue in self.issues.get_issues():
            issue_for_user = "{file}, {line_begin}, {column_begin}, {description}, {severity}, {context}".format(file = issue.file, line_begin = issue.line, column_begin = issue.column_begin + issue.column_begin_offset, description = issue.description.value, severity = issue.severity.value, context = issue.context.replace("\u2308", "").replace("\u2309", "").strip())
            if not issue_for_user in ignore_issues:
                remaining_issues.add(issue)
            else:
                ignore_issues.remove(issue_for_user)
        self.issues = remaining_issues                
    
    def display_summary_result(self):
        LOG.info("Detection result summary:")
        LOG.info("Start time:            {start_time}".format(start_time = self.begin_time.replace(tzinfo = timezone.utc).astimezone()))
        LOG.info("End time:              {end_time}".format(end_time = self.end_time.replace(tzinfo = timezone.utc).astimezone()))
        LOG.info("Time cost(hh:mm:ss):   {duration}".format(duration = self.end_time - self.begin_time))
        LOG.info("File(s) scanned:       {file_count}".format(file_count = self.res_file_count))
        LOG.info("Item(s) scanned:       {item_count}".format(item_count = self.item_count))
        LOG.info("Issue(s) detected:     {issue_count}".format(issue_count = self.issues.issue_count))
        LOG.info("Error(s) detected:     {error_count}".format(error_count = self.issues.error_count))
        LOG.info("Warning(s) detected:   {warning_count}".format(warning_count = self.issues.warning_count))
        LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
        
    def write_result_for_platform(self):
        try:
            if self.args.summary:
                LOG.info("Writing summary detection result for platform...")
                summary_file = self.args.summary
                if not summary_file.endswith(".csv"):
                    summary_file = summary_file + ".csv"
                with open(summary_file, "w", encoding = "utf_8_sig", newline = "") as fw:
                    summary_writer = csv.writer(fw)
                    summary_writer.writerow(["files", "errors", "warnings", "items", "begin", "end", "name", "version"])
                    summary_writer.writerow([self.res_file_count, self.issues.error_count, self.issues.warning_count, self.item_count, self.begin_time, self.end_time, __application__, __version__])     
                #LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
            if self.args.details:
                LOG.info("Writing detailed detection result for platform...")
                details_file = self.args.details
                if not details_file.endswith(".csv"):
                    details_file = details_file + ".csv"
                with open(details_file, "w", encoding = "utf_8_sig", newline = "") as fw:
                    details_writer = csv.writer(fw)
                    details_writer.writerow(["file", "line", "column", "columnEnd", "severity", "code", "context"])
                    for issue in self.issues.get_issues():
                        details_writer.writerow([os.path.relpath(issue.file, self.src_dir).replace("\\", "/"), issue.line, issue.column_begin, issue.column_end, issue.severity.value, issue.code.value, issue.context])            
                #LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
        except Exception as e:
            LOG.critical("An error occurred when writing detection result for platform: {exception}".format(exception = e))
            quit_application(-1)
    
    def write_result_for_user(self):
        if self.args.output:
            try:
                LOG.info("Writing detection result...")
                output_file = open(file = self.args.output, mode = "w", encoding = "utf_8_sig")
                output_file.write("Detection result summary:\n")
                output_file.write("Tool name:             {tool_name}\n".format(tool_name = __application__))
                output_file.write("Tool version:          {tool_version}\n".format(tool_version = __version__))
                output_file.write("Source directory:      {src_dir}\n".format(src_dir = self.src_dir))
                output_file.write("Start time:            {start_time}\n".format(start_time = self.begin_time.replace(tzinfo = timezone.utc).astimezone()))
                output_file.write("End time:              {end_time}\n".format(end_time = self.end_time.replace(tzinfo=timezone.utc).astimezone()))
                output_file.write("Time cost(hh:mm:ss):   {duration}\n".format(duration = self.end_time - self.begin_time))
                output_file.write("File(s) scanned:       {file_count}\n".format(file_count = self.res_file_count))
                output_file.write("Item(s) scanned:       {item_count}\n".format(item_count = self.item_count))
                output_file.write("Issue(s) detected:     {issue_count}\n".format(issue_count = self.issues.issue_count))
                output_file.write("Error(s) detected:     {error_count}\n".format(error_count = self.issues.error_count))
                output_file.write("Warning(s) detected:   {warning_count}\n".format(warning_count = self.issues.warning_count))
                output_file.write("---------------------------------------------------------------------------------------------------------------------------------------------------------\n")
                output_file.write("File, Line, Column, Issue, Severity, Context\n")
                for issue in self.issues.get_issues():
                    output_file.write("{file}, {line_begin}, {column_begin}, {description}, {severity}, {context}\n".format(file = issue.file, line_begin = issue.line, column_begin = issue.column_begin + issue.column_begin_offset, description = issue.description.value, severity = issue.severity.value, context = issue.context.replace("\u2308", "").replace("\u2309", "").strip()))
                output_file.close()
                #LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
            except Exception as e:
                LOG.critical("An error occurred when writing detection result to '{output_file}': {exception}".format(output_file = self.args.output, exception = e))
                quit_application(-1)
    
    def write_result_for_ignoring(self):
        if self.args.ignore_pattern:
            try:
                LOG.info("Writing ignore issue patterns...")
                output_file = open(file = self.args.ignore_pattern, mode = "w", encoding = "utf_8_sig")
                for issue in self.issues.get_issues():
                    issue_pattern = "{file}, {line_begin}, {column_begin}, {description}, {severity}, {context}".format(file = issue.file, line_begin = issue.line, column_begin = issue.column_begin + issue.column_begin_offset, description = issue.description.value, severity = issue.severity.value, context = issue.context.replace("\u2308", "").replace("\u2309", "").strip())
                    output_file.write(repr(issue_pattern) + ",\n")
                output_file.close()
                #LOG.info("---------------------------------------------------------------------------------------------------------------------------------------")
            except Exception as e:
                LOG.critical("An error occurred when writing ignore issue patterns to '{output_file}': {exception}".format(output_file = self.args.ignore_pattern, exception = e))
                quit_application(-1)


def initialize(arguments):
    try:
        global LOG  
        LOG = logging.getLogger(__name__)
        LOG.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(levelname)s]: %(message)s")
        if arguments.log:
            file_handler = logging.FileHandler(filename = arguments.log, mode = 'w', encoding = "utf_8_sig", delay = False)
            file_handler.setFormatter(formatter)
            LOG.addHandler(file_handler)
        stream_handler = logging.StreamHandler(stream = sys.stdout)
        stream_handler.setFormatter(formatter)
        LOG.addHandler(stream_handler)
    except Exception as e:
        print("[CRITICAL]: An error occurred when initializing logging: {exception}".format(exception = e))
        print("[INFO]: {application} exited abnormally".format(application = __application__))
        sys.exit(-1)
    if arguments.tab:
        if arguments.tab.isdigit():
            try:
                global TAB_WIDTH
                TAB_WIDTH = int(arguments.tab)
            except ValueError:
                LOG.critical("Argument 'tab' is not valid, please have a check")
                quit_application(-1)
        else:
            LOG.critical("Argument 'tab' is not valid, please have a check")
            quit_application(-1)


def quit_application(state):
    if state == -1:
        LOG.info("{application} exited abnormally".format(application = __application__))
    else:
        LOG.info("{application} exited normally".format(application = __application__))
    sys.exit(state)


def parse_arguments(arguments):
    arg_parser = argparse.ArgumentParser(description = "resource detector: detect g11n/i18n issues in resource files")
    arg_parser.add_argument("directory", help = "specify the source code directory to be scanned")
    arg_parser.add_argument("-o", "--output", metavar = "result.txt", help = "specify the output file where detection result will be written")
    arg_parser.add_argument("-g", "--generate_config", action = "store_true", help = "generate configuration file named 'resource_detector_config.py' in the directory to be scanned")
    arg_parser.add_argument("-l", "--log", metavar = "log.txt", help = "specify the log file")
    arg_parser.add_argument("-t", "--tab", metavar = "4", help = "specify the tab width to make sure the column number is correctly calculated, default value is 4")
    arg_parser.add_argument("-i", "--ignore_pattern", metavar = "ignore_patterns.txt", help = "specify the file where ignore issue patterns will be written")
    arg_parser.add_argument("-s", "--summary", metavar = "summary.csv", help = "specify the csv file where summary detection result will be written")
    arg_parser.add_argument("-d", "--details", metavar = "details.csv", help = "specify the csv file where detailed detection result will be written")
    arg_parser.add_argument("-v", "--version", action = "version", version = __version__)
    return arg_parser.parse_args(arguments)


def main(argv):
    arguments = parse_arguments(argv[1:])
    initialize(arguments)
    resource_detector = ResourceDetector(arguments)
    resource_detector.run()
    return 0


if __name__ == "__main__":
    result = main(sys.argv)
    quit_application(result)
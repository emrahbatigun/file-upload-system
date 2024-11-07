import os

from django.conf import settings
from pprint import pprint
from django.templatetags.static import static
from importlib import import_module, util


class LayoutConfig:

    # Variables
    htmlAttributes = {}
    htmlClasses = {}

    # Keep page level assets
    javascriptFiles = []
    cssFiles = []
    vendorFiles = []

    @staticmethod
    def init():
        LayoutConfig.htmlAttributes = {}
        LayoutConfig.htmlClasses = {}

        LayoutConfig.javascriptFiles = []
        LayoutConfig.cssFiles = []
        LayoutConfig.vendorFiles = []

    def addHtmlAttribute(scope, name, value):
        LayoutConfig.htmlAttributes.setdefault(scope, {})
        LayoutConfig.htmlAttributes[scope][name] = value

    def addHtmlAttributes(scope, attributes):
        LayoutConfig.htmlAttributes.setdefault(scope, {})
        for key in attributes:
            LayoutConfig.htmlAttributes[scope][key] = attributes[key]

    def addHtmlClass(scope, value):
        LayoutConfig.htmlClasses.setdefault(scope, [])
        if value not in LayoutConfig.htmlClasses[scope]:
            LayoutConfig.htmlClasses[scope].append(value)

    @staticmethod
    def getName():
        return settings.NAME

    def printHtmlAttributes(scope):
        attributes = []
        if scope in LayoutConfig.htmlAttributes:
            for key in LayoutConfig.htmlAttributes[scope]:
                attributes.append('{}="{}"'.format(key, LayoutConfig.htmlAttributes[scope][key]))

        return ' '.join(attributes)

    def printHtmlClasses(scope, full = True):
        if not LayoutConfig.htmlClasses:
            return ''

        classes = ''
        if scope in LayoutConfig.htmlClasses:
            classes = ' '.join(LayoutConfig.htmlClasses[scope])

        if (full):
            return 'class="{}"'.format(classes)
        else:
            return classes

    def getSvgIcon(path, classNames = 'svg-icon', folder='media/icons/'):
        svg = open('.' + LayoutConfig.asset(folder + path)).read()
        output = '<span class="{}">{}</span>'.format(classNames, svg)
        return output

    def asset(path):
        return static(path)

    def extendCssFilename(path):
        return path

    @staticmethod
    def includeFavicon():
        return static(settings.LAYOUT_ASSETS['favicon'])

    @staticmethod
    def includeFonts():
        content = ''
        for url in settings.LAYOUT_ASSETS['fonts']:
            content += '<link rel="stylesheet" href="{}">'.format(url)

        return content

    def getGlobalAssets(type):
        files = []
        for file in settings.LAYOUT_ASSETS[type]:
            if type == 'css':
                # Modify css file name suffix based on the RTL or dark mode settings
                files.append(LayoutConfig.extendCssFilename(file))
            else:
                files.append(file)

        return files

    def addVendors(vendors):
        for value in vendors:
            if value not in LayoutConfig.vendorFiles:
                LayoutConfig.vendorFiles.append(value)

    def addVendor(vendor):
        # Skip duplicate entry
        if vendor not in LayoutConfig.vendorFiles:
            LayoutConfig.vendorFiles.append(vendor)

    def addJavascriptFile(file):
        # Skip duplicate entry
        if file not in LayoutConfig.javascriptFiles:
            LayoutConfig.javascriptFiles.append(file)

    def addCssFile(file):
        if file not in LayoutConfig.cssFiles:
            LayoutConfig.cssFiles.append(file)

    def getVendors(type):
        files = []
        for vendor in LayoutConfig.vendorFiles:
            if type in settings.LAYOUT_VENDORS[vendor]:
                if settings.LAYOUT_VENDORS[vendor][type] not in files:
                    for path in settings.LAYOUT_VENDORS[vendor][type]:
                        files.append(LayoutConfig.addStatic(path))

        return files

    def setLayout(view, context = {}):
        LayoutConfig.htmlAttributes = {}
        LayoutConfig.htmlClasses = {}

        layout = os.path.splitext(view)[0]
        layout = layout.split('/')[0]

        module = 'templates.{}.bootstrap.{}'.format(settings.LAYOUT_DIR.replace('/', '.'), layout)

        if not util.find_spec(module) == None:
            Bootstrap = LayoutConfig.importClass(module, 'Bootstrap{}'.format(layout.title().replace('-', '')))
            Bootstrap.init(context)
        else:
            module = 'templates.{}.bootstrap.default'.format(settings.LAYOUT_DIR.replace('/', '.'))
            Bootstrap = LayoutConfig.importClass(module, 'BootstrapDefault')
            Bootstrap.init(context)

        return '{}/{}'.format(settings.LAYOUT_DIR, view)

    def importClass(fromModule, importClassName):
        pprint('Loading {} from {}'.format(importClassName, fromModule))
        module = import_module(fromModule)
        return getattr(module, importClassName)

    def addStatic(path):
        if '//' in path:
            return path
        return LayoutConfig.asset(path)

from django.utils.safestring import mark_safe
from django import template
from file_upload_system.layout_config import LayoutConfig

register = template.Library()


@register.simple_tag
def includeFonts():
    return mark_safe(LayoutConfig.includeFonts())


@register.simple_tag
def includeFavicon():
    return mark_safe(LayoutConfig.includeFavicon())


@register.simple_tag
def getSvgIcon(path, classNames='svg-icon', folder='media/icons/'):
    return mark_safe(LayoutConfig.getSvgIcon(path, classNames, folder))


@register.simple_tag
def printHtmlClasses(scope):
    return mark_safe(LayoutConfig.printHtmlClasses(scope))


@register.simple_tag
def printHtmlAttributes(scope):
    return mark_safe(LayoutConfig.printHtmlAttributes(scope))


@register.simple_tag
def getGlobalAssets(type):
    return LayoutConfig.getGlobalAssets(type)


@register.simple_tag
def getCustomJs():
    return LayoutConfig.javascriptFiles


@register.simple_tag
def getCustomCss():
    return LayoutConfig.cssFiles


@register.simple_tag
def getVendors(type):
    return LayoutConfig.getVendors(type)


@register.simple_tag
def asset(path):
    return LayoutConfig.asset(path)


@register.simple_tag
def addHtmlAttribute(scope, name, value):
    LayoutConfig.addHtmlAttribute(scope, name, value)
    return ''


@register.simple_tag
def addHtmlAttributes(scope, attributes):
    LayoutConfig.addHtmlAttributes(scope, attributes)
    return ''


@register.simple_tag
def addHtmlClass(scope, value):
    LayoutConfig.addHtmlClass(scope, value)
    return ''


@register.simple_tag
def getHtmlAttribute(scope, attribute):
    return LayoutConfig.htmlAttributes[scope][attribute]

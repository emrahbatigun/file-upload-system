from file_upload_system.layout_config import LayoutConfig


class BootstrapDefault:

    def init(context):
        BootstrapDefault.initAssets(context)

        return context

    def initAssets(context):
        LayoutConfig.addJavascriptFile('js/widgets.bundle.js')

        return context

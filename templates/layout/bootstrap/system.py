from file_upload_system.layout_config import LayoutConfig


class KTBootstrapSystem:

    def init(context):
        LayoutConfig.addHtmlClass('body', 'app-blank')
        LayoutConfig.addHtmlClass("body", "bgi-size-cover bgi-position-center bgi-no-repeat")

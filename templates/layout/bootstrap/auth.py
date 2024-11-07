from file_upload_system.layout_config import LayoutConfig


class BootstrapAuth:

    def init(context):
        LayoutConfig.addHtmlClass('body', 'app-blank')

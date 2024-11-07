from file_upload_system.layout_config import LayoutConfig


class Bootstrap:

    @staticmethod
    def init_layout():
        LayoutConfig.addHtmlAttribute('body', 'id', 'kt_app_body')
        LayoutConfig.addHtmlAttribute('body', 'data-kt-name', LayoutConfig.getName())

    @staticmethod
    def init():
        Bootstrap.init_layout()

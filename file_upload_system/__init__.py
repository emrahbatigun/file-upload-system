from .bootstrap import Bootstrap
from file_upload_system.layout_config import LayoutConfig


class Layout:
    def init(context):
        LayoutConfig.init()

        context.update(
            {
                'layout': LayoutConfig.setLayout('default.html', context),
            }
        )

        Bootstrap.init()

        # Return context
        return context

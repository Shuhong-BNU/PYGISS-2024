# ui/mapWidget_components/render.py
# 功能：提供地图渲染的相关功能，将各种渲染混合类组合在一起

from .baseRender import BaseRenderMixin
from .layerManager import LayerManagerMixin
from .renderUtils import RenderUtilsMixin

class RenderMixin(BaseRenderMixin, LayerManagerMixin, RenderUtilsMixin):
    """
    组合渲染相关的所有功能，包括基本渲染、图层管理和渲染工具的功能。
    """
    pass

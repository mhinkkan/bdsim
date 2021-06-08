# PyQt5 imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# BdEdit imports
from bdsim.bdedit.Icons import *


# =============================================================================
#
#   Defining the GraphicsBlock Class, which is inherited by all Blocks and
#   controls the graphical appearance of each Block.
#
# =============================================================================
class GraphicsBlock(QGraphicsItem):
    """
    The ``GraphicsBlock`` Class extends the ``QGraphicsItem`` Class from PyQt5.
    This class is responsible for graphically drawing Blocks within the GraphicsScene.
    Using the provided Block dimensions, it specifies the Blocks' shape and colour.
    """

    # -----------------------------------------------------------------------------
    def __init__(self, block, parent=None):
        """
        This method initializes an instance of the ``GraphicsBlock`` Class.
        It inherits the dimensions of its Block, and defines its shape and colour.

        :param block: the Block this GraphicsBlock instance relates to
        :type block: Block, required
        :param parent: the parent widget this class instance belongs to (None)
        :type parent: NoneType, optional, defaults to None
        """

        super().__init__(parent)
        # The block properties are inherited from the provided block
        self.block = block
        self.icon = self.block.icon
        self.width = self.block.width
        self.height = self.block.height

        # The color mode of the block is also stored (Light or Dark mode)
        self.mode = self.block.scene.grScene.mode

        # Internal variable which dictate whether a title needs to be drawn
        # The first time the Block is drawn, this is True, then it is set to
        # False, and only changed to True when the title is called to update
        self._draw_title = True

        # These dimensions are not updated
        self._default_width = self.block.width
        self._default_height = self.block.height

        # Pen thickness and block-related spacings are defined
        self.edge_size = 10.0           # How rounded the rectangle corners are
        self.title_height = 25.0        # How many pixels underneath the block the title is displayed at
        self._padding = 5.0             # Minimum distance inside the block that things should be displayed at
        self._line_thickness = 3.0              # Thickness of the block outline by default
        self._selected_line_thickness = 5.0     # Thickness of the block outline on selection

        # Colours for pens are defined, and the text font is set
        self._default_title_color = Qt.black    # Title colour (set to Light mode by default)
        self._pen_selected = QPen(QColor("#FFFFA637"), self._selected_line_thickness)
        self._title_font = QFont("Ubuntu", 10)

        # Methods called to:
        # * draw the title for the block
        # * check current colour mode the block should display in (Light/Dark)
        # * further initialize necessary block settings
        self.initTitle()
        self.checkMode()
        self.initUI()

    # -----------------------------------------------------------------------------
    def initUI(self):
        """
        This method sets flags to allow for this Block to be movable and selectable.
        """

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    # -----------------------------------------------------------------------------
    def initTitle(self):
        """
        This method initializes a QGraphicsTextItem which will graphically represent
        the title (name) of this Block.
        """

        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._default_title_color)
        self.title_item.setFont(self._title_font)

    # -----------------------------------------------------------------------------
    def titleLength(self):
        """
        This method calculates and returns the length of this Blocks' title in pixels.

        :return: the pixel length of this Blocks' title
        :rtype: int
        """

        # Using the font of the text and the block's title, determine the length of the
        # title in terms of pixels
        title_pixel_len = QFontMetrics(self._title_font).width(self.block.title)

        # As the block width is an even number (100 pixels), to center properly, the
        # width of the title must also be even
        # If title width is odd, add 1 pixel to it to make it even
        if title_pixel_len % 2 != 0:
            title_pixel_len += 1
        return title_pixel_len

    # -----------------------------------------------------------------------------
    def getTitle(self):
        """
        This method returns the current title of this Block.

        :return: Block title
        :rtype: str
        """

        return self.block.title

    # -----------------------------------------------------------------------------
    def setTitle(self):
        """
        This method updates this Blocks' graphical title to the stored title of the Block.
        """

        # Once the title has been set, this method will handle redrawing the title
        # Hence the title doesn't need to be redrawn after
        self._draw_title = False

        # Graphical title is set to the block's title is set
        self.title_item.setPlainText(self.block.title)

        # Title length is found (using self.titleLength()), and centered under the block
        self.title_item.setPos((self.width - self._padding - self.titleLength()) / 2, self.height + self._padding)

        # The GraphicsBlock instance is called to be updated
        self.update()

    # -----------------------------------------------------------------------------
    def checkMode(self):
        """
        This method checks the mode of the GraphicsScene's background (Light, Dark)
        and updates the colour mode of the pens and brushes used to paint this Block.
        """

        # If dark mode is selected, draw blocks tailored to dark mode
        if self.mode == "Dark":
            self._title_color = Qt.white
            self._pen_default = QPen(Qt.white, self._line_thickness)
            self._brush_background = QBrush(Qt.white)
        # Else light or off mode is selected (No off mode for blocks), draw blocks tailored to light mode
        else:
            self._title_color = Qt.black
            self._pen_default = QPen(QColor("#7F000000"), self._line_thickness)
            self._brush_background = QBrush(QColor("#FFE1E0E8"))

        self.title_item.setDefaultTextColor(self._title_color)

    # -----------------------------------------------------------------------------
    def updateMode(self, value):
        """
        This method updates the mode of the Block to the provided value (should only
        ever be "Light", "Dark" or "Off").

        :param value: current mode of the GraphicsScene's background ("Light", "Dark", "Off")
        :type value: str, required
        """

        if value in ["Light", "Dark", "Off"]:
            self.mode = value
            self.checkMode()
            self.update()
        else:
            print("Block mode not supported.")

    # -----------------------------------------------------------------------------
    def checkBlockHeight(self):
        """
        This method checks if the current height of the Block is enough to fit all
        the Sockets that are to be drawn, while following the set socket spacing.
        It also handles the resizing of the Block (if there isn't enough space for
        all the sockets), ensuring the sockets are evenly spaced while following
        the set socket spacing.
        """

        # The offset distance from the top of the Block to the first Socket.
        # The same offset is used for from the bottom of the Block to the last Socket.
        socket_spacer = self._padding + self.edge_size + self.title_height

        # This code grabs the coordinates ([x,y]) of last input and output sockets if any exist
        if self.block.inputs:
            last_input = self.block.inputs[-1].getSocketPosition()
        else:
            last_input = [0, 0]

        if self.block.outputs:
            last_output = self.block.outputs[-1].getSocketPosition()
        else:
            last_output = [0, 0]

        # The max height of the Block could depend on either the input or output sockets
        # Hence the max height of both types are found (max height is the height at which
        # the last socket should be placed, in order for sockets to be evenly spaced)

        # Max height of input/output sockets - adds socket_spacer height to height of last input/output socket
        max_input_socket_height = last_input[1] + socket_spacer
        max_output_socket_height = last_output[1] + socket_spacer

        # Max block height (determined by which ever has more sockets - inputs or outputs)
        max_block_height = max(max_input_socket_height, max_output_socket_height)

        # If max_block_height is greater than the default block height, set current_block_height to max_block_height
        # Otherwise keep it at the default block height
        if max_block_height > self._default_height:
            self.block.height = max_block_height
        else:
            self.block.height = self._default_height

        # Update the internal height of the GraphicsBlock to the updated height of the Block
        self.height = self.block.height
        self.update()

    # -----------------------------------------------------------------------------
    def boundingRect(self):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by ``GraphicsBlock``
        which returns the area within which the GraphicsBlock can be interacted with.
        When a mouse click event is detected within this area, this will trigger logic
        that relates to a Block (that being, selecting/deselecting, moving, deleting,
        flipping or opening a parameter window).

        :return: a rectangle within which the Block can be interacted with
        :rtype: QRectF
        """

        return QRectF(
            0,
            0,
            self.width,
            self.height
        )

    # -----------------------------------------------------------------------------
    def paint(self, painter, style, widget=None):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by ``GraphicsBlock``.
        This method is automatically called by the GraphicsView Class whenever even
        a slight user-interaction is detected within the Scene.

        Before drawing, the dimensions of the Block are checked, to ensure they can
        hold all the necessary Sockets. Then the following are drawn in order:

        - the title of the block
        - the fill of the block (a rounded rectangle)
        - the outline of the block (a rounded rectangle)
        - the icon of the block (if one exists)

        :param painter: a painter (paint brush) that paints and fills the shape of this GraphicsBlock
        :type painter: QPainter, automatically recognized and overwritten from this method
        :param style: style of the painter (isn't used but must be defined)
        :type style: QStyleOptionGraphicsItem, automatically recognized from this method
        :param widget: the widget this class is being painted on (None)
        :type widget: NoneType, optional, defaults to None
        """

        # Block dimensions are checked for to ensure there's enough space for all sockets
        self.checkBlockHeight()

        # Title will be redrawn, if needed
        if self._draw_title:
            self.setTitle()

        # Background (fill) of the block is drawn
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height, self.edge_size,
                                    self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # Outline of the block is drawn
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

        # Icon of the block is drawn overtop the blocks' background
        icon_item = QPixmap(self.icon).scaledToWidth(50) if self.icon else QPixmap(self.icon)   # Icons are scaled down to 50 pixels
        target = QRect((self.width-icon_item.width())/2, (self.height-icon_item.height())/2, self.width, self.height)
        source = QRect(0, 0, self.width, self.height)
        painter.drawPixmap(target, icon_item, source)

    # -----------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by
        ``GraphicsBlock`` to detect, and assign logic to a right mouse press event.

        Currently a detected mouse press event on the GraphicsBlock will select
        or deselect it.

        - If selected, the GraphicsBlock will be sent to front and will appear on
          top of other blocks.
        - Additionally, if the right mouse button is pressed and a GraphicsBlock
          is selected, a parameter window will be toggled for this Block.

        :param event: a mouse press event (Left, Middle or Right)
        :type event: QMousePressEvent, automatically recognized by the inbuilt function
        """

        # When the current GraphicsBlock is pressed on, it is sent to the front
        # of the work area (in the GraphicsScene)
        self.block.setFocusOfBlocks()

        # If the GraphicsBlock is currently selected when the right mouse button
        # is pressed, the parameter window will be toggled (On/Off)
        if event.button() == Qt.RightButton:
            if self.isSelected():
                self.block.toggleParamWindow()

        super().mousePressEvent(event)

    # -----------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by
        ``GraphicsBlock`` to detect, and assign logic to mouse movement.

        Currently, the following logic is applied to the Block on mouse movement:

        - a detected mouse move event on this GraphicsBlock will enforce grid-snapping
          on the selected GraphicsBlock (making it move only in increments of the same
          size as the smaller grid squares of the background).

        - the selected GraphicsBlock will be prevented from moving outside the maximum
          zoomed out border of the work area (the GraphicsScene).

        - the connection points of any wires connected to the selected block AND any
          other block it is connected to, will be updated, as the block is moved around.

        :param event: a mouse movement event
        :type event: QMouseMoveEvent, automatically recognized by the inbuilt function
        """

        super().mouseMoveEvent(event)

        # The x,y position of the mouse cursor is grabbed, and is restricted to update
        # every 20 pixels (the size of the smaller grid squares, as defined in GraphicsScene)
        x = round(self.pos().x() / 20) * 20
        y = round(self.pos().y() / 20) * 20
        pos = QPointF(x, y)
        # The position of this GraphicsBlock is set to the restricted position of the mouse cursor
        self.setPos(pos)

        # 20 is the width of the smaller grid squares
        # This logic prevents the selected QGraphicsBlock from being dragged outside
        # the border of the work area (GraphicsScene)
        padding = 20
        if self.pos().x() < self.scene().sceneRect().x() + padding:
            # left
            self.setPos(self.scene().sceneRect().x() + padding, self.pos().y())

        if self.pos().y() < self.scene().sceneRect().y() + padding:
            # top
            self.setPos(self.pos().x(), self.scene().sceneRect().y() + padding)

        if self.pos().x() > (self.scene().sceneRect().x() + self.scene().sceneRect().width() - self.width - padding):
            # right
            self.setPos(self.scene().sceneRect().x() + self.scene().sceneRect().width() - self.width - padding, self.pos().y())

        if self.pos().y() > (self.scene().sceneRect().y() + self.scene().sceneRect().height() - self.height - self.title_height - padding):
            # bottom
            self.setPos(self.pos().x(), self.scene().sceneRect().y() + self.scene().sceneRect().height() - self.height - self.title_height - padding)

        # Finally, update the connected wires of all Blocks that are affected by this Block being moved
        for block in self.block.scene.blocks:
            if block.grBlock.isSelected():
                block.updateConnectedEdges()


class GraphicsSocketBlock(QGraphicsItem):
    """
    The ``GraphicsSocketBlock`` Class extends the ``QGraphicsItem`` Class from PyQt5.
    This class is responsible for graphically drawing Connector Blocks within the
    GraphicsScene.
    """

    # -----------------------------------------------------------------------------
    def __init__(self, block, parent=None):
        """
        This method initializes an instance of the ``GraphicsSocketBlock`` Class
        (otherwise known as the Graphics Class of the Connector Block).

        :param block: the Connector Block this GraphicsSocketBlock instance relates to
        :type block: Connector Block
        :param parent: the parent widget this class instance belongs to (None)
        :type parent: NoneType, optional, defaults to None
        """

        super().__init__(parent)
        self.block = block
        self.icon = self.block.icon

        self._draw_title = True

        self.width = self.block.width
        self.height = self.block.height

        # As the connector block consists of two sockets (1 input, 1 output) which
        # use the following commands in determining where they need to be placed,
        # these commands must be included, but are set to 0 as no shape is drawn for
        # the connector block, aside from these two sockets.
        self.edge_size = 0
        self.title_height = 0
        self._padding = 0

        # Definition for the line thickness when the Connector block is selected
        # Internal padding is half this value
        # Corner rounding is by how many pixels the corners are rounded of the selected box that is drawn
        self._selected_line_thickness = 5.0
        self._internal_padding = 2.5
        self._corner_rounding = 10

        # Color of the selected line is set
        self._pen_selected = QPen(QColor("#FFFFA637"), self._selected_line_thickness)   # Orange

        # Further initialize necessary Connector Block settings
        self.initUI()

    # -----------------------------------------------------------------------------
    def initUI(self):
        """
        This method sets flags to allow for this Connector Block to be movable and selectable.
        """

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        # When first created, the Connector block spawns highlighted
        self.setSelected(True)

    # -----------------------------------------------------------------------------
    def boundingRect(self):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by ``GraphicsSocketBlock``
        which returns the area within which the GraphicsSocketBlock can be interacted with.
        When a mouse click event is detected within this area, this will trigger logic
        that relates to a Block (that being, selecting/deselecting, moving, deleting,
        flipping or opening a parameter window. Or if its Sockets are clicked on,
        this will trigger a wire to be created or ended).

        :return: a rectangle within which the Block can be interacted with
        :rtype: QRectF
        """

        W = self.width
        P = self._internal_padding
        return QRectF(
            1 - W - P,
            1 - W - P,
            3 * W + P,
            2 * W + P
        ).normalized()

        # Alternative selection area that is larger, but will overlap wires directly
        # one grid block step above the connector block, when the connector block is
        # selected.
        # return QRectF(
        #     1 - 1.5 * W - P,
        #     1 - 1.5 * W - P,
        #     4 * W + P,
        #     3 * W + P
        # ).normalized()

    # -----------------------------------------------------------------------------
    def paint(self, painter, style, widget=None):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by
        ``GraphicsSocketBlock`` (otherwise referred to as the Graphics Class of
        the Connector Block. This method is automatically called by the GraphicsView
        Class whenever even a slight user-interaction is detected within the Scene.

        When the Connector Block is selected, this method will draw an orange
        outline around the Connector Block, within which it can be interacted with.

        :param painter:a painter (paint brush) that paints and fills the shape of this GraphicsSocketBlock
        :type painter: QPainter, automatically recognized and overwritten from this method
        :param style: style of the painter (isn't used but must be defined)
        :type style: QStyleOptionGraphicsItem, automatically recognized from this method
        :param widget: the widget this class is being painted on (None)
        :type widget: NoneType, optional, defaults to None
        """

        if self.isSelected():
            # Draws orange outline around the Connector Block when it is selected
            path_outline = QPainterPath()
            # The size of the rectangle drawn, is dictated by the boundingRect (interactive area)
            path_outline.addRoundedRect(self.boundingRect(), self._corner_rounding, self._corner_rounding)
            painter.setPen(self._pen_selected)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path_outline.simplified())

    # -----------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by
        ``GraphicsSocketBlock`` to detect, and assign logic to a right mouse press event.

        Currently a detected mouse press event on the GraphicsSocketBlock will
        select or deselect it.

        Additionally if selected, the GraphicsBlock will be sent to front and will
        appear on top of other blocks.

        :param event: a mouse press event (Left, Middle or Right)
        :type event: QMousePressEvent, automatically recognized by the inbuilt function
        """

        # When the current GraphicsSocketBlock is pressed on, it is sent to the front
        # of the work area (in the GraphicsScene)
        self.block.setFocusOfBlocks()

    # -----------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        """
        This is an inbuilt method of QGraphicsItem, that is overwritten by
        ``GraphicsSocketBlock`` to detect, and assign logic to mouse movement.

        Currently, the following logic is applied to the Connector Block on mouse movement:

        - a detected mouse move event on this GraphicsSocketBlock will enforce
          grid-snapping on the selected GraphicsSocketBlock (making it move only
          in increments of the same size as the smaller grid squares of the background).

        - the selected GraphicsSocketBlock will be prevented from moving outside the
          maximum zoomed out border of the work area (the GraphicsScene).

        - the connection points of any wires connected to the selected Connector Block AND any
          other block it is connected to, will be updated, as the block is moved around.

        :param event: a mouse movement event
        :type event: QMouseMoveEvent, automatically recognized by the inbuilt function
        """

        super().mouseMoveEvent(event)

        # The x,y position of the mouse cursor is grabbed, and is restricted to update
        # every 20 pixels (the size of the smaller grid squares, as defined in GraphicsScene)
        x = round(self.pos().x() / 20) * 20
        y = round(self.pos().y() / 20) * 20
        pos = QPointF(x, y)
        self.setPos(pos)

        # 20 is the width of the smaller grid squares
        # This logic prevents the selected GraphicsSocketBlock from being dragged outside
        # the border of the work area (GraphicsScene)
        padding = 20
        if self.pos().x() < self.scene().sceneRect().x() + padding:
            # left
            self.setPos(self.scene().sceneRect().x() + padding, self.pos().y())

        if self.pos().y() < self.scene().sceneRect().y() + padding:
            # top
            self.setPos(self.pos().x(), self.scene().sceneRect().y() + padding)

        if self.pos().x() > (self.scene().sceneRect().x() + self.scene().sceneRect().width() - self.width - padding):
            # right
            self.setPos(self.scene().sceneRect().x() + self.scene().sceneRect().width() - self.width - padding, self.pos().y())

        if self.pos().y() > (self.scene().sceneRect().y() + self.scene().sceneRect().height() - self.height - self.title_height - padding):
            # bottom
            self.setPos(self.pos().x(), self.scene().sceneRect().y() + self.scene().sceneRect().height() - self.height - self.title_height - padding)

        # Finally, update the connected wires of all Blocks that are affected by this Connector Block being moved
        for block in self.block.scene.blocks:
            if block.grBlock.isSelected():
                block.updateConnectedEdges()

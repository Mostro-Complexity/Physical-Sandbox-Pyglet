from math import sin, cos, pi, sqrt
import pyglet
from pyassimp import *
from pyglet import image
from pyglet.gl import *


def vec(*args):
    return (GLfloat * len(args))(*args)


# 导入模型
scene = load('face.obj')


class GameEventHandler(object):
    mouse_down = False
    mouse_orig_pos = [0, 0]
    rx, ry = 0, 0
    track = []  # 物体运行的轨迹点

    def on_mouse_drag(self, mouse_curr_x, mouse_curr_y, dx, dy, buttons, modifiers):
        if self.mouse_down:
            self.rx += mouse_curr_x - self.mouse_orig_pos[0]
            self.ry += 0.03 * (mouse_curr_y - self.mouse_orig_pos[1])
            if self.ry > 1.0:
                self.ry = 1.0
            elif self.ry < -1.0:
                self.ry = -1.0
            self.mouse_orig_pos[0] = mouse_curr_x
            self.mouse_orig_pos[1] = mouse_curr_y
        else:
            self.rx, self.ry = 0, 0

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.mouse_down = True
        self.mouse_orig_pos[0] = x
        self.mouse_orig_pos[1] = y
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        pass

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        position = (sin(integral_drift[0] / 2) / sqrt(integral_drift[0]),
                    cos(integral_drift[1] / 2) / sqrt(integral_drift[1]))
        self.track.append(position)

        gluLookAt(1.5 * cos(pi / 180 * self.rx), -self.ry, 1.5 * sin(pi / 180 * self.rx)
                  , 0, 0, 0, 0, 1, 0)

        glPushMatrix()
        glTranslatef(position[0], position[1], 0)
        ball.draw()
        glPopMatrix()

        glColor3f(1, 1, 1)
        glBegin(GL_LINE_STRIP)
        for v in self.track:
            glVertex3f(start[0] + v[0], start[1] + v[1], start[2])
        glEnd()

    def on_key_press(self, symbol, modifiers):
        pass

    @staticmethod
    def on_resize(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70., width / float(height), .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED


def scene_init():
    # One-time GL setup
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)  # 启用混合功能，将图形颜色同周围颜色相混合
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_POLYGON_SMOOTH)  # 多边形抗锯齿
    # glHint(GL_POLYGON_SMOOTH, GL_NICEST)

    glEnable(GL_LINE_SMOOTH)  # 线抗锯齿
    # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    glEnable(GL_POINT_SMOOTH)  # 点抗锯齿
    # glHint(GL_POINT_SMOOTH, GL_NICEST)

    # 材质如何设置？
    properties = scene.materials[0].properties
    ambient = properties['ambient']
    diffuse = properties['diffuse']
    specular = properties['specular']
    emission = properties['emissive']

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, properties['shininess'])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, vec(ambient[0], ambient[1], ambient[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vec(diffuse[0], diffuse[1], diffuse[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(specular[0], specular[1], specular[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(emission[0], emission[1], emission[2], 0))
    pass


class TextureEnableGroup(pyglet.graphics.Group):
    @staticmethod
    def set_state():
        glEnable(GL_TEXTURE_2D)

    @staticmethod
    def unset_state():
        glDisable(GL_TEXTURE_2D)


class TextureBindGroup(pyglet.graphics.Group):
    def __init__(self, texture, texture_enable_group):
        super(TextureBindGroup, self).__init__(parent=texture_enable_group)
        texture.target = GL_TEXTURE_2D
        self.texture = texture

    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        pass

    # No unset_state method required.
    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture.id == other.texture.id and
                self.texture.target == other.texture.target and
                self.parent == other.parent)

    def __hash__(self):
        return hash((self.texture.id, self.texture.target))


def update(dt):
    delta_x = 5 * dt
    delta_y = 5 * dt
    delta_z = 5 * dt
    integral_drift[0] += delta_x
    integral_drift[1] += delta_y
    integral_drift[2] += delta_z
    pass


def start_pos(scene):
    """

    :param scene: Scene object with model data(Scene对象)
    :return: start position of model(模型初始位置)
    """
    x_range = [0, 0]
    y_range = [0, 0]
    z_range = [0, 0]
    for m in scene.meshes:
        if x_range[1] < m.vertices[:, 0].max():
            x_range[1] = m.vertices[:, 0].max()
        if x_range[0] > m.vertices[:, 0].min():
            x_range[0] = m.vertices[:, 0].min()
        if y_range[1] < m.vertices[:, 1].max():
            y_range[1] = m.vertices[:, 1].max()
        if y_range[0] > m.vertices[:, 1].min():
            y_range[0] = m.vertices[:, 1].min()
        if z_range[1] < m.vertices[:, 2].max():
            z_range[1] = m.vertices[:, 2].max()
        if z_range[0] > m.vertices[:, 2].min():
            z_range[0] = m.vertices[:, 2].min()

    return (x_range[0] + x_range[1]) / 2, \
           (y_range[0] + y_range[1]) / 2, \
           (z_range[0] + z_range[1]) / 2


window = pyglet.window.Window(resizable=True)  # , config=config)
scene_init()  # 灯光和整体材质设置
ball = pyglet.graphics.Batch()
integral_drift = [0.1, 0.1, 0.1]  # 位移的度量总和
window.push_handlers(GameEventHandler())
pyglet.app.event_loop.clock.schedule(update)
text_image = image.load('brmarble.png')
text_bind_group = TextureBindGroup(text_image.get_texture(),
                                   TextureEnableGroup())

for m in scene.meshes:
    m.vertices /= 500  # 缩放比例

start = start_pos(scene)

for m in scene.meshes:  # 导入模型数据
    ball.add(m.vertices.shape[0], GL_TRIANGLES, text_bind_group,
             ('v3f/static', m.vertices.reshape(-1).tolist()),
             ('t3f/static', m.texturecoords.reshape(-1).tolist()))
    pass

pyglet.app.run()

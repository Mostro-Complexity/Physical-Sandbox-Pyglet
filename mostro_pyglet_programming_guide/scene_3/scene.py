from math import sin, cos, pi

import pyglet
from pyassimp import *
from pyglet import image
from pyglet.gl import *


def vec(*args):
    return (GLfloat * len(args))(*args)


window = pyglet.window.Window(resizable=True)  # , config=config)

# 导入模型
scene = load('ball.obj')


class GameEventHandler(object):
    mouse_down = False
    mouse_orig_pos = [0, 0]
    rx, ry = 0, 0

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
        glTranslatef(sin(position[0] / 2), cos(position[1] / 2), 0)
        gluLookAt(1.5 * cos(pi / 180 * self.rx), -self.ry, 1.5 * sin(pi / 180 * self.rx)
                  , 0, 0, 0, 0, 1, 0)
        ball.draw()

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
    def set_state(self):
        glEnable(GL_TEXTURE_2D)

    def unset_state(self):
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
    position[0] += delta_x
    position[1] += delta_y
    position[2] += delta_z
    pass


scene_init()
ball = pyglet.graphics.Batch()
position = [0, 0, 0]

window.push_handlers(GameEventHandler())
pyglet.app.event_loop.clock.schedule(update)
text_image = image.load('paperbag.png')

for m in scene.meshes:  # 导入模型数据
    m.vertices /= 100  # 缩放比例
    text_bind_group = TextureBindGroup(text_image.get_texture(),
                                       TextureEnableGroup())

    ball.add(m.vertices.shape[0], GL_TRIANGLES, text_bind_group,
             ('v3f/static', m.vertices.reshape(-1).tolist()),
             ('t3f/static', m.texturecoords.reshape(-1).tolist()))
    pass

pyglet.app.run()

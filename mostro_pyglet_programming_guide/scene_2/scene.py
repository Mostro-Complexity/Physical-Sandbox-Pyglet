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


def update(dt):
    global delta
    delta[0] = 5 * dt
    delta[1] = 5 * dt
    delta[2] = 5 * dt
    position[0] += delta[0]
    position[1] += delta[1]
    position[2] += delta[2]
    pass


class GameEventHandler(object):
    @staticmethod
    def on_key_press(symbol, modifiers):
        print('Key pressed in game')
        return True

    @staticmethod
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        global rx, ry
        rx += x - mouse_orig_pos[0]
        ry += 0.03 * (y - mouse_orig_pos[1])
        if ry > 1.0:
            ry = 1.0
        elif ry < -1.0:
            ry = -1.0
        mouse_orig_pos[0] = x
        mouse_orig_pos[1] = y

    @staticmethod
    def on_draw():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # glTranslatef(3 * sin(position[0]), 3 * cos(position[1]), -100)
        glTranslatef(0, 0, -100)
        gluLookAt(1.5 * cos(pi / 180 * rx), -ry, 1.5 * sin(pi / 180 * rx), 0, 0, 0, 0, 1, 0)
        ball.draw()

    @staticmethod
    def on_resize(width, height):
        # Override the default on_resize handler to create a 3D projection
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

    # Uncomment this line for a wireframe view
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    # Define a simple function to create ctypes arrays of floats:

    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

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


scene_init()
ball = pyglet.graphics.Batch()
delta = [0, 0, 0]
position = [0, 0, 0]

mouse_orig_pos = [0, 0]
rx, ry = 0, 0

window.push_handlers(GameEventHandler())
pyglet.app.event_loop.clock.schedule(update)
text_image = image.load('paperbag.png')

for m in scene.meshes:  # 导入模型数据
    text_bind_group = TextureBindGroup(text_image.get_texture(),
                                       TextureEnableGroup())

    ball.add(m.vertices.shape[0], GL_TRIANGLES, text_bind_group,
             ('v3f/static', m.vertices.reshape(-1).tolist()),
             ('t3f/static', m.texturecoords.reshape(-1).tolist()))
    pass

pyglet.app.run()

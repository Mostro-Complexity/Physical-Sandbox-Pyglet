"""Displays a rotating torus using the pyglet.graphics API.

This example is very similar to examples/opengl.py, but uses the
pyglet.graphics API to construct the indexed vertex arrays instead of
using OpenGL calls explicitly.  This has the advantage that VBOs will
be used on supporting hardware automatically.

The vertex list is added to a batch, allowing it to be easily rendered
alongside other vertex lists with minimal overhead.
"""

import pyglet
from pyassimp import *
from pyglet import image
from pyglet.gl import *

window = pyglet.window.Window(resizable=True)  # , config=config)

# 导入模型
scene = load('ball.obj')


@window.event
def on_resize(width, height):
    # Override the default on_resize handler to create a 3D projection
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED


def update(dt):
    global dx, dy, dz
    rx += dt * 1
    ry += dt * 80
    rz += dt * 30
    rx %= 360
    ry %= 360
    rz %= 360


pyglet.app.event_loop.clock.schedule(update)
background_image = image.load('paperbag.png')
texture = background_image.get_texture()


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -50)
    glRotatef(dz, 0, 0, 1)
    glRotatef(dy, 0, 1, 0)
    glRotatef(dx, 1, 0, 0)
    glEnable(texture.target)  # typically target is GL_TEXTURE_2D
    glBindTexture(texture.target, texture.id)
    batch.draw()
    glDisable(texture.target)


def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)
    # glColor3f(1, 0, 0)
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
    def vec(*args):
        return (GLfloat * len(args))(*args)

    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

    # 材质如何设置？
    material = scene.meshes[0].material
    ambient = material.properties['ambient']
    diffuse = material.properties['diffuse']
    specula = material.properties['specular']
    emissiver = material.properties['emissive']

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material.properties['shininess'])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, vec(ambient[0], ambient[1], ambient[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, vec(diffuse[0], diffuse[1], diffuse[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(specula[0], specula[1], specula[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(emissiver[0], emissiver[1], emissiver[2], 0))
    pass


class Torus:
    def __init__(self, batch, group=None):
        for m in scene.meshes:
            self.vertex_list = batch.add(m.vertices.shape[0], GL_TRIANGLES, group,
                                         ('v3f/static', m.vertices.reshape(-1).tolist()),
                                         ('t3f/static', m.texturecoords.reshape(-1).tolist()))
            pass
        pass

    def delete(self):
        self.vertex_list.delete()


class TextureEnableGroup(pyglet.graphics.Group):
    def set_state(self):
        glEnable(GL_TEXTURE_2D)

    def unset_state(self):
        glDisable(GL_TEXTURE_2D)


texture_enable_group = TextureEnableGroup()


class TextureBindGroup(pyglet.graphics.Group):
    def __init__(self, texture):
        super(TextureBindGroup, self).__init__(parent=texture_enable_group)
        texture.target = GL_TEXTURE_2D
        self.texture = texture

    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)

    # No unset_state method required.
    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.texture.id == other.texture.id and
                self.texture.target == other.texture.target and
                self.parent == other.parent)

    def __hash__(self):
        return hash((self.texture.id, self.texture.target))


setup()
batch = pyglet.graphics.Batch()
dx = dy = dz = 0
image = pyglet.image.load('paperbag.png')

torus = Torus(batch=batch, group=TextureBindGroup(image.get_texture()))

pyglet.app.run()

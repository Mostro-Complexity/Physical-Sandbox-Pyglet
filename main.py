from math import sin, cos, pi

import numpy as np
from pyglet.gl import *

from mostro.modeling import *
from mostro.simulation import gravity, runge_kutta_generator
from universe import *

r_A = [0, 1, 1.2]
r_B = [1.8, 0, 1.32]
r_C = [1.54, 1.86, 0]
v_A = [0, 0, 0]
v_B = [0, 0, 0]
v_C = [0, 0, 0]


class GameEventHandler(object):
    mouse_down = False
    mouse_orig_pos = [0, 0]
    # rx,ry为每次拖动的变化量，ix,iy为积累的拖动变化量
    rx, ry, ix, iy = 0, 0, 0, 0

    camera = Camera(np.array([-2., -2., -2.]), np.zeros(3))
    # 开始时间t=0,步长为1
    gen = runge_kutta_generator(np.array([r_A + v_A + r_B + v_B + r_C + v_C]), 0, 1, gravity)

    def on_mouse_drag(self, mouse_curr_x, mouse_curr_y, dx, dy, buttons, modifiers):
        if self.mouse_down:
            self.rx = mouse_curr_x - self.mouse_orig_pos[0]
            self.ry = mouse_curr_y - self.mouse_orig_pos[1]
        else:
            self.rx, self.ry = 0, 0

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.mouse_down = True
        self.mouse_orig_pos[0] = x
        self.mouse_orig_pos[1] = y
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_down = False
        self.ix += self.rx
        self.iy += self.ry
        self.rx = 0
        self.ry = 0
        pass

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        self.camera.look_at((self.rx, self.ry), (self.ix, self.iy))

        Y = next(self.gen)
        position = np.r_[Y[0:3], Y[6:9], Y[12:15]]
        # print(position)

        planets[0].move(position[0:3], True)
        planets[1].move(position[3:6], True)
        planets[2].move(position[6:9], True)

        glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)
        glVertex3f(100, 0, 0)
        glEnd()

        glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 100, 0)
        glEnd()

        glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_LINE_STRIP)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 100)
        glEnd()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.W:
            print('W')
            self.camera.location += 0.1 * self.camera.sight
        if symbol == pyglet.window.key.S:
            print('S')
            self.camera.location -= 0.1 * self.camera.sight
        if symbol == pyglet.window.key.A:
            # 头顶到视角的叉乘
            print('A')
        if symbol == pyglet.window.key.D:
            # 视角到头顶的叉乘
            print('D')
        pass

    @staticmethod
    def on_resize(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30., width / float(height), .1, 1000.)
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
    properties = model.scene.materials[0].properties
    ambient = properties['ambient']
    diffuse = properties['diffuse']
    specular = properties['specular']
    emission = properties['emissive']

    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, properties['shininess'])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, array(ambient[0], ambient[1], ambient[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, array(diffuse[0], diffuse[1], diffuse[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, array(specular[0], specular[1], specular[2], 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, array(emission[0], emission[1], emission[2], 0))
    pass


if __name__ == '__main__':
    window = pyglet.window.Window(resizable=True, caption='Sandbox of planet movement')  # , config=config)

    model = Model('face.obj', 'brmarble.png', 500)
    planets = [Planet(model, np.array(v_A), np.array(r_A)), Planet(model, np.array(v_B), np.array(r_B)),
               Planet(model, np.array(v_C), np.array(r_C))]
    scene_init()  # 灯光和整体材质设置

    window.push_handlers(GameEventHandler())
    pyglet.app.event_loop.clock.schedule(Planet.update)

    pyglet.app.run()

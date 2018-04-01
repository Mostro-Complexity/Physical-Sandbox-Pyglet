from math import cos, sin
from pyassimp import *
from pyglet import image
from pyglet.gl import *


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


class Model(object):
    def __init__(self, filename, text_filename, dim=500):
        """

        :param filename: filename of obj file（obj文件）
        :param text_filename: png filename（png文件）
        :param dim: reduce times（缩小倍数）
        """
        self.scene = load(filename)  # 导入模型
        for m in self.scene.meshes:
            m.vertices /= dim  # 缩放比例
        self.integral_drift = [0.1, 0.1, 0.1]  # 位移的度量总和
        text_image = image.load(text_filename)
        self.text_bind_group = TextureBindGroup(text_image.get_texture(),
                                                TextureEnableGroup())
        self.start_location = self.get_start_pos()
        self.batch = pyglet.graphics.Batch()
        for m in self.scene.meshes:  # 导入模型数据
            self.batch.add(m.vertices.shape[0], GL_TRIANGLES, self.text_bind_group,
                           ('v3f/static', m.vertices.reshape(-1).tolist()),
                           ('t3f/static', m.texturecoords.reshape(-1).tolist()))
            pass

    def update(self, dt):
        delta_x = 5 * dt
        delta_y = 5 * dt
        delta_z = 5 * dt
        self.integral_drift[0] += delta_x
        self.integral_drift[1] += delta_y
        self.integral_drift[2] += delta_z
        pass

    def get_start_pos(self):
        """

        :return: start position of model(模型初始位置)
        """
        x_range = [0, 0]
        y_range = [0, 0]
        z_range = [0, 0]
        for m in self.scene.meshes:
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

        return numpy.array(
            [(x_range[0] + x_range[1]) / 2, (y_range[0] + y_range[1]) / 2, (z_range[0] + z_range[1]) / 2])


class Camera(object):
    def __init__(self, location, sight):
        self.location = location
        self.sight = sight

    def look_at(self, drag, total):
        self.sight[0] = cos((total[1] + drag[1]) / 180) * sin((total[0] + drag[0]) / 180)
        self.sight[1] = cos((total[1] + drag[1]) / 180) * cos((total[0] + drag[0]) / 180)
        self.sight[2] = sin((total[1] + drag[1]) / 180)  # 方向向量

        gluLookAt(self.location[0], self.location[1], self.location[2]
                  , self.sight[0] + self.location[0],
                  self.sight[1] + self.location[1],
                  self.sight[2] + self.location[2], 0, 0, 1)


def array(*args):
    return (GLfloat * len(args))(*args)

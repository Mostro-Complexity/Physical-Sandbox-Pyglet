from pyglet.gl import *


class Planet(object):
    def __init__(self, model, velocity, location, quality, track_len=200):
        """

        :param model: 模型
        :param velocity: 初始速度
        :param location: 初始位置
        :param quality: 质量
        :param track_len: 轨迹长度
        """
        self.model = model
        self.start_velocity = velocity
        self.start_location = location
        self.quality = quality
        self.track = []  # 行星轨迹
        self.track_len = track_len

    def move(self, position, trace=False):
        if len(self.track) < self.track_len:  # 数组限制长度
            self.track.append(position)
        else:
            self.track.append(position)
            self.track.pop(0)

        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        self.model.batch.draw()
        glPopMatrix()
        # print(position)

        # 轨迹
        if trace:
            glLineWidth(2)
            glColor3f(1, 1, 1)
            glBegin(GL_LINE_STRIP)
            for v in self.track:
                # glVertex3f(self.model.start_location[0] +v[0], self.model.start_location[1] +v[1],
                #            self.model.start_location[2]+v[2])
                glVertex3f(self.model.start_location[0] + v[0], self.model.start_location[1] + v[1],
                           self.model.start_location[2] + v[2])

            glEnd()

    def update(self):
        pass

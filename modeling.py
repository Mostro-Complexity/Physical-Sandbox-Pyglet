import numpy as np
from pyassimp import *
from pyglet.gl import *
from ctypes import *


class Model(object):
    def __init__(self, filename):
        self.scene = load(filename)
        assert len(self.scene.meshes)
        mesh = self.scene.meshes[0]
        assert len(mesh.vertices)
        self.vertices = mesh.vertices

        self.x_bound = (np.min(mesh.vertices[:, 0]), np.max(mesh.vertices[:, 0]))
        self.y_bound = (np.min(mesh.vertices[:, 1]), np.max(mesh.vertices[:, 1]))
        self.z_bound = (np.min(mesh.vertices[:, 2]), np.max(mesh.vertices[:, 2]))
        self.x_range = self.x_bound[1] - self.x_bound[0]
        self.y_range = self.y_bound[1] - self.y_bound[0]
        self.z_range = self.z_bound[1] - self.z_bound[0]
        pass

    def draw(self):
        pass


class Surface(Model):
    def __init__(self, filename):
        super().__init__(filename)
        pass

    def draw(self):
        glBegin(GL_TRIANGLES)
        for i in range(self.vertices.shape[0]):
            glVertex3f(self.vertices[i, 0] / self.x_range,
                       self.vertices[i, 1] / self.y_range,
                       self.vertices[i, 2] / self.z_range)
            pass
        glEnd()
        pass


class Mesh(Model):
    def __init__(self, filename):
        super().__init__(filename)
        pass

    def draw(self):
        glBegin(GL_LINE_STRIP)
        for i in range(self.vertices.shape[0]):
            glVertex3f(self.vertices[i, 0] / self.x_range,
                       self.vertices[i, 1] / self.y_range,
                       self.vertices[i, 2] / self.z_range)
            pass
        glEnd()
        pass


vertex_shader_src = \
    b'''
    layout(location = 0) in vec3 position;
    layout(location = 1) in vec2 textCoord;
    layout(location = 2) in vec3 normal;
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    out vec2 TextCoord;
    void main()
    {
        gl_Position = projection * view * model * vec4(position, 1.0);
        TextCoord = textCoord;
    }
    '''

fragment_shader_src = \
    b"""
    #version 330 core
    in vec2 TextCoord;
    uniform sampler2D texture_diffuse0;
    uniform sampler2D texture_diffuse1;
    uniform sampler2D texture_diffuse2;
    uniform sampler2D texture_specular0;
    uniform sampler2D texture_specular1;
    uniform sampler2D texture_specular2;
    out vec4 color;
    void main()
    {
        color = texture(texture_diffuse0, TextCoord);
    }
    """


class Shader(object):
    program_id = None

    def __init__(self):
        shader_id = (glCreateShader(GL_VERTEX_SHADER),
                     glCreateShader(GL_FRAGMENT_SHADER))
        glShaderSource(shader_id[0], 1, cast(vertex_shader_src, POINTER(c_char)), cast(0,POINTER(c_int)))
        glShaderSource(shader_id[1], 1, cast(fragment_shader_src, POINTER(c_char)), cast(0,POINTER(c_int)))
        glCompileShader(shader_id[0])
        glCompileShader(shader_id[1])
        status=cast(c_int*2,POINTER(c_int))
        glGetShaderiv(shader_id[0], GL_COMPILE_STATUS, status)
        print(status)
        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, shader_id[0])
        glAttachShader(self.program_id, shader_id[1])
        glLinkProgram(self.program_id)
        glDetachShader(self.program_id, shader_id[0])
        glDetachShader(self.program_id, shader_id[1])
        glDeleteShader(shader_id[0])
        glDeleteShader(shader_id[1])
        pass

    def use(self):
        glUseProgram(self.program_id)
        pass

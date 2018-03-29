import numpy as np


def gravity(t, r):
    """

    :param t: Time
    :param r: Position and speed of planet
    :return: Next position and speed
    """
    G = 6.67e-11
    m = [5.965e4, 5.965e4, 5.965e4]
    r__a, r__b, r__c = np.zeros((2, 3)), np.zeros((2, 3)), np.zeros((2, 3))

    r__a[0, :] = r[0: 3]
    r__a[1, :] = r[3: 6]
    r__b[0, :] = r[6: 9]
    r__b[1, :] = r[9: 12]
    r__c[0, :] = r[12: 15]
    r__c[1, :] = r[15: 18]

    dy = np.zeros(18)

    dy[0: 6] = np.r_[r__a[1, :],
                     G * m[1] * (r__b[0, :] - r__a[0, :]) / np.linalg.norm(r__b[0, :] - r__a[0, :]) ** 3 + G * m[
                         2] * (
                         r__c[0, :] - r__a[0, :]) / np.linalg.norm(r__c[0, :] - r__a[0, :]) ** 3]

    dy[6: 12] = np.r_[r__b[1, :],
                      G * m[0] * (r__a[0, :] - r__b[0, :]) / np.linalg.norm(r__a[0, :] - r__b[0, :]) ** 3 + G * m[
                          2] * (
                          r__c[0, :] - r__b[0, :]) / np.linalg.norm(r__c[0, :] - r__b[0, :]) ** 3]

    dy[12: 18] = np.r_[r__c[1, :],
                       G * m[0] * (r__a[0, :] - r__c[0, :]) / np.linalg.norm(r__a[0, :] - r__c[0, :]) ** 3 + G * m[
                           1] * (
                           r__b[0, :] - r__c[0, :]) / np.linalg.norm(r__b[0, :] - r__c[0, :]) ** 3]

    return dy


def runge_kutta(y0, x, func, *args):
    h = x[1] - x[0]
    y = np.zeros((x.shape[0], y0.shape[1]))
    y[0, :] = y0

    for i in range(1, x.shape[0]):
        k1 = func(x[i - 1], y[i - 1, :])
        k2 = func(x[i - 1] + h / 2, y[i - 1, :] + h * k1 / 2)
        k3 = func(x[i - 1] + h / 2, y[i - 1, :] + h * k2 / 2)
        k4 = func(x[i - 1] + h, y[i - 1, :] + h * k3)
        y[i, :] = y[i - 1, :] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6

    return y


def runge_kutta_generator(y0, x0, h, func, *args):
    y = np.zeros((2, y0.shape[1]))
    y[0, :] = y0
    y[1, :] = y0

    while True:
        y[0, :] = y[1, :]
        k1 = func(x0, y[0, :])
        k2 = func(x0 + h / 2, y[0, :] + h * k1 / 2)
        k3 = func(x0 + h / 2, y[0, :] + h * k2 / 2)
        k4 = func(x0 + h, y[0, :] + h * k3)
        y[1, :] = y[0, :] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x0 += h
        yield y[1, :]


if __name__ == '__main__':
    r_A = [0, 1e2, 1.2e1]
    r_B = [1.8e1, 0, 1.32 * 1e2]
    r_C = [1.54 * 1e3, 1.86 * 1e2, 0]
    v_A = [0, 0, 0]
    v_B = [0, 0, 0]
    v_C = [0, 0, 0]

    # y = runge_kutta(np.array([r_A + v_A + r_B + v_B + r_C + v_C]), np.arange(0, 100, 5), gravity)
    y = runge_kutta_generator(np.array([r_A + v_A + r_B + v_B + r_C + v_C]), 0, 1, gravity)

    for i in range(10):
        r = y.__next__()
        print(r)

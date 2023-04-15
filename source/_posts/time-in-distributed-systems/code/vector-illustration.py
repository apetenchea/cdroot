from manim import *


def generate_points(num, distance):
    points = []
    start = Dot()
    points.append(start)
    for i in range(1, num):
        point = Dot().next_to(points[-1], RIGHT, distance)
        points.append(point)
    return VGroup(*points)


class CausalBroadcastIllustration(Scene):
    def construct(self):
        dist = 1.5
        num = 8
        shift = (num - 1) * dist / 2
        a = generate_points(num, dist)
        a.shift(shift * LEFT + 2 * UP)
        la = Line(a[0], a[-1])
        b = generate_points(num, dist)
        b.shift(shift * LEFT)
        lb = Line(b[0], b[-1])
        c = generate_points(num, dist)
        c.shift(shift * LEFT + 2 * DOWN)
        lc = Line(c[0], c[-1])

        txt_left = 3
        lbl_a = Text("A", color=WHITE).next_to(a[0], LEFT * txt_left)
        lbl_b = Text("B", color=WHITE).next_to(b[0], LEFT * txt_left)
        lbl_c = Text("C", color=WHITE).next_to(c[0], LEFT * txt_left)

        lbl_scale = 0.6
        m1_txt = "(1, 0, 0)"
        m1_ab_start = Text(m1_txt, color=BLUE).scale(lbl_scale).next_to(a[0], UP)
        m1_ab_end = Text(m1_txt, color=BLUE).scale(lbl_scale).next_to(b[1], DOWN)
        m1_ab = DashedLine(a[0], b[1], color=GREEN)
        m1_ac_end = Text(m1_txt, color=BLUE).scale(lbl_scale).next_to(c[-2], DOWN)
        m1_ac = DashedLine(a[0], c[-2], color=GREEN)

        m2_txt = "(1, 1, 0)"
        m1_ba_start = Text(m2_txt, color=BLUE).scale(lbl_scale).next_to(b[2], DOWN)
        m1_ba_end = Text(m2_txt, color=BLUE).scale(lbl_scale).next_to(a[3], UP)
        m1_ba = DashedLine(b[2], a[3], color=GREEN)
        m1_bc_end = Text(m2_txt, color=GRAY).scale(lbl_scale).next_to(c[4], DOWN)
        m1_bc = DashedLine(b[2], c[4], color=GRAY)

        m3_txt = "(1, 1, 0)"
        m3 = Text(m3_txt, color=BLUE).scale(lbl_scale).next_to(c[-1], DOWN)
        m3_arrow = CurvedArrow(start_point=c[4].get_top(), end_point=c[-1].get_top(), angle=-60 * DEGREES, color=GRAY)

        self.add(a, b, c, la, lb, lc, lbl_a, lbl_b, lbl_c,
                 m1_ab_start, m1_ab_end, m1_ab, m1_ac_end, m1_ac,
                 m1_ba_start, m1_ba_end, m1_ba, m1_bc_end, m1_bc,
                 m3, m3_arrow)


class VectorClocksIllustration(Scene):
    def construct(self):
        radius = 1
        tex_scale = 1
        wait_time = 2

        a = Circle(color=RED, radius=radius)
        a.shift(4 * LEFT + 2 * UP)
        a_lbl = Text("1", color=GREEN).scale(tex_scale).next_to(a, UP)
        a_val = MathTex("(0,0,0)", color=WHITE).scale(tex_scale).move_to(a.get_center())

        b = Circle(color=RED, radius=radius)
        b.shift(4 * RIGHT + 2 * UP)
        b_lbl = Text("3", color=GREEN).scale(tex_scale).next_to(b, UP)
        b_val = MathTex("(0,0,0)", color=WHITE).scale(tex_scale).move_to(b.get_center())

        c = Circle(color=RED, radius=radius)
        c.shift(2 * DOWN)
        c_lbl = Text("2", color=GREEN).scale(tex_scale).next_to(c, UP)
        c_val = MathTex("(0,0,0)", color=WHITE).scale(tex_scale).move_to(c.get_center())

        self.add(a, a_lbl, a_val, b, b_lbl, b_val, c, c_lbl, c_val)
        self.wait(wait_time)

        # m1
        c_010 = Arrow(self.get_position_on_circle(c.get_center(), LEFT, UP),
                      self.get_position_on_circle(a.get_center(), RIGHT, DOWN),
                      color=GREEN)
        c_update = MathTex("(0,1,0)", color=WHITE).scale(tex_scale).move_to(c.get_center())
        self.play(Transform(c_val, c_update), GrowArrow(c_010))
        self.wait(wait_time)
        a_update = MathTex("(0,1,0)", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(a_val, a_update), FadeOut(c_010))
        self.wait(wait_time / 2)
        a_update = MathTex("(1,1,0)", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(a_val, a_update))
        self.wait(wait_time)

        # m2
        a_210 = Arrow(a.get_center() + RIGHT,
                      b.get_center() + LEFT,
                      color=GREEN)
        a_update = MathTex("(2,1,0)", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(a_val, a_update), GrowArrow(a_210))
        self.wait(wait_time)
        b_update = MathTex("(2,1,0)", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update), FadeOut(a_210))
        self.wait(wait_time / 2)
        b_update = MathTex("(2,1,1)", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update))
        self.wait(wait_time)

        # m3
        a_310 = Arrow(self.get_position_on_circle(a.get_center(), RIGHT, DOWN),
                      self.get_position_on_circle(c.get_center(), LEFT, UP),
                      color=GREEN)
        a_update = MathTex("(3,1,0)", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(a_val, a_update), GrowArrow(a_310))
        self.wait(wait_time)
        c_update = MathTex("(3,1,0)", color=WHITE).scale(tex_scale).move_to(c.get_center())
        self.play(Transform(c_val, c_update), FadeOut(a_310))
        self.wait(wait_time / 2)
        c_update = MathTex("(3,2,0)", color=WHITE).scale(tex_scale).move_to(c.get_center())
        self.play(Transform(c_val, c_update))
        self.wait(wait_time)

        # m4
        c_330 = Arrow(self.get_position_on_circle(c.get_center(), RIGHT, UP),
                      self.get_position_on_circle(b.get_center(), LEFT, DOWN),
                      color=GREEN)
        c_update = MathTex("(3,3,0)", color=WHITE).scale(tex_scale).move_to(c.get_center())
        self.play(Transform(c_val, c_update), GrowArrow(c_330))
        self.wait(wait_time)
        b_update = MathTex("(3,3,1)", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update), FadeOut(c_330))
        self.wait(wait_time / 2)
        b_update = MathTex("(3,3,2)", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update))
        self.wait(wait_time)

        # Fade out
        self.play(FadeOut(a), FadeOut(a_lbl), FadeOut(a_val),
                  FadeOut(b), FadeOut(b_lbl), FadeOut(b_val),
                  FadeOut(c), FadeOut(c_lbl), FadeOut(c_val))
        self.wait()

        self.create_transition_image()
        self.wait(wait_time)

    def create_transition_image(self):
        dist = 1.5
        num = 8
        shift = (num - 1) * dist / 2
        a = generate_points(num, dist)
        a.shift(shift * LEFT + 2 * UP)
        la = Line(a[0], a[-1])
        b = generate_points(num, dist)
        b.shift(shift * LEFT + 2 * DOWN)
        lb = Line(b[0], b[-1])
        c = generate_points(num, dist)
        c.shift(shift * LEFT)
        lc = Line(c[0], c[-1])

        lbl_scale = 0.6
        m1_start = Text("(0, 1, 0)", color=BLUE).scale(lbl_scale).next_to(c[0], DOWN)
        m1_end = Text("(1, 1, 0)", color=BLUE).scale(lbl_scale).next_to(a[1], UP)
        m1 = Arrow(c[0], a[1], color=GREEN)

        m2_start = Text("(2, 1, 0)", color=BLUE).scale(lbl_scale).next_to(a[2], UP)
        m2_end = Text("(2, 1, 1)", color=BLUE).scale(lbl_scale).next_to(b[3], DOWN)
        m2 = Arrow(a[2], b[3], color=GREEN)

        m3_start = Text("(3, 1, 0)", color=BLUE).scale(lbl_scale).next_to(a[4], UP)
        m3_end = Text("(3, 2, 0)", color=BLUE).scale(lbl_scale).next_to(c[5], DOWN)
        m3 = Arrow(a[4], c[5], color=GREEN)

        m4_start = Text("(3, 3, 0)", color=BLUE).scale(lbl_scale).next_to(c[6], UP)
        m4_end = Text("(3, 3, 2)", color=BLUE).scale(lbl_scale).next_to(b[7], DOWN)
        m4 = Arrow(c[6], b[7], color=GREEN)

        txt_left = 3
        lbl_a = Text("1", color=WHITE).next_to(a[0], LEFT * txt_left)
        lbl_b = Text("3", color=WHITE).next_to(b[0], LEFT * txt_left)
        lbl_c = Text("2", color=WHITE).next_to(c[0], LEFT * txt_left)

        self.play(FadeIn(a), FadeIn(b), FadeIn(c),
                  FadeIn(la), FadeIn(lb), FadeIn(lc),
                  FadeIn(m1_start), FadeIn(m1_end), FadeIn(m1),
                  FadeIn(m2_start), FadeIn(m2_end), FadeIn(m2),
                  FadeIn(m3_start), FadeIn(m3_end), FadeIn(m3),
                  FadeIn(m4_start), FadeIn(m4_end), FadeIn(m4),
                  FadeIn(lbl_a), FadeIn(lbl_b), FadeIn(lbl_c))

    @staticmethod
    def get_position_on_circle(c, h, v):
        """
        :param c: center of circle
        :param h: horizontal direction (LEFT or RIGHT)
        :param v: vertical direction (UP or DOWN)
        :return: position on the circle, corresponding to the given directions
        """
        pi_4 = np.pi / 4
        return c + np.sin(pi_4) * h + np.cos(pi_4) * v

from manim import *


class OutOfSyncIllustration(MovingCameraScene):
    def construct(self):
        radius = 1
        vertical = 3
        horizontal = 6
        tex_scale = 1.5

        a = Circle(color=RED, radius=radius)
        a.shift(vertical * UP + horizontal * LEFT)
        a_lbl = MathTex("A", color=GREEN).scale(tex_scale).next_to(a, UP)
        a_val = MathTex(42, color=WHITE).scale(tex_scale).move_to(a.get_center())

        b = Circle(color=RED, radius=radius)
        b.shift(vertical * UP + horizontal * RIGHT)
        b_lbl = MathTex("B", color=GREEN).scale(tex_scale).next_to(b, UP)
        b_val = MathTex(42, color=WHITE).scale(tex_scale).move_to(b.get_center())

        c1 = Circle(color=BLUE, radius=radius)
        c1.shift(vertical * DOWN + horizontal * LEFT)
        c1_lbl = MathTex("C_1", color=GREEN).scale(tex_scale).next_to(c1, DOWN)
        c1_val = MathTex("+1", color=WHITE).scale(tex_scale).move_to(c1.get_center())

        c2 = Circle(color=BLUE, radius=radius)
        c2.shift(vertical * DOWN + horizontal * RIGHT)
        c2_lbl = MathTex("C_2", color=GREEN).scale(tex_scale).next_to(c2, DOWN)
        c2_val = MathTex("*2", color=WHITE).scale(tex_scale).move_to(c2.get_center())

        self.camera.frame.save_state()
        self.camera.frame.scale(1.5)

        self.add(a, a_lbl, a_val, b, b_lbl, b_val, c1, c1_lbl, c1_val, c2, c2_lbl, c2_val)
        self.wait()

        c1_arrow = Arrow(c1.get_top(), a.get_bottom(), color=GREEN)
        c2_arrow = Arrow(c2.get_top(), b.get_bottom(), color=GREEN)
        self.play(GrowArrow(c1_arrow), GrowArrow(c2_arrow))
        self.wait()

        a_update = MathTex(43, color=WHITE).scale(tex_scale).move_to(a.get_center())
        b_update = MathTex(84, color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(a_val, a_update), Transform(b_val, b_update))
        self.wait()

        a_arrow = Arrow(a.get_center() + np.sin(np.pi / 4) * RIGHT + np.cos(np.pi / 4) * UP,
                        b.get_center() + np.sin(np.pi / 4) * LEFT + np.cos(np.pi / 4) * UP, color=GREEN)
        a_arrow_tex = MathTex("+1", color=WHITE).next_to(a_arrow, UP)
        b_arrow = Arrow(b.get_center() + np.sin(np.pi / 4) * LEFT + np.cos(np.pi / 4) * DOWN,
                        a.get_center() + np.sin(np.pi / 4) * RIGHT + np.cos(np.pi / 4) * DOWN, color=GREEN)
        b_arrow_tex = MathTex("*2", color=WHITE).next_to(b_arrow, DOWN)
        self.play(GrowArrow(a_arrow), GrowArrow(b_arrow), FadeIn(a_arrow_tex), FadeIn(b_arrow_tex))
        self.wait()

        a_update = MathTex(86, color=WHITE).scale(tex_scale).move_to(a.get_center())
        b_update = MathTex(85, color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(a_val, a_update), Transform(b_val, b_update))
        self.wait(3)


class PreconditionTrueIllustration(Scene):
    def construct(self):
        radius = 1
        horizontal = 4
        tex_scale = 1

        a = Circle(color=RED, radius=radius)
        a.shift(horizontal * LEFT)
        a_lbl = Text("A", color=GREEN).scale(tex_scale).next_to(a, UP)
        a_val = Text("42", color=WHITE).scale(tex_scale).move_to(a.get_center())

        b = Circle(color=RED, radius=radius)
        b.shift(horizontal * RIGHT)
        b_lbl = Text("B", color=GREEN).scale(tex_scale).next_to(b, UP)
        b_val = Text("42", color=WHITE).scale(tex_scale).move_to(b.get_center())

        self.add(a, a_lbl, a_val, b, b_lbl, b_val)
        self.wait()

        a_prec = Arrow(a.get_right(), b.get_left(), color=GREEN)
        a_prec_tex = Text("value == 42", color=WHITE).scale(tex_scale).next_to(a_prec, UP)
        self.play(GrowArrow(a_prec), FadeIn(a_prec_tex))
        self.wait()
        self.play(FadeOut(a_prec), FadeOut(a_prec_tex))
        self.wait()

        b_res = Arrow(b.get_left(), a.get_right(), color=GREEN)
        b_res_tex = Text("true", color=WHITE).scale(tex_scale).next_to(b_res, UP)
        self.play(GrowArrow(b_res), FadeIn(b_res_tex))
        self.wait()
        self.play(FadeOut(b_res), FadeOut(b_res_tex))
        self.wait()

        a_update = Text("43", color=WHITE).scale(tex_scale).move_to(a.get_center())
        a_commit = Arrow(a.get_right(), b.get_left(), color=GREEN)
        a_commit_tex = Text("value = 43", color=WHITE).scale(tex_scale).next_to(a_commit, UP)
        self.play(Transform(a_val, a_update))
        self.wait()
        self.play(GrowArrow(a_commit), FadeIn(a_commit_tex))
        self.wait()

        b_update = Text("43", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update))
        self.wait()


class PreconditionFalseIllustration(Scene):
    def construct(self):
        radius = 1
        horizontal = 4
        tex_scale = 1

        a = Circle(color=RED, radius=radius)
        a.shift(horizontal * LEFT)
        a_lbl = Text("A", color=GREEN).scale(tex_scale).next_to(a, UP)
        a_val = Text("42", color=WHITE).scale(tex_scale).move_to(a.get_center())

        b = Circle(color=RED, radius=radius)
        b.shift(horizontal * RIGHT)
        b_lbl = Text("B", color=GREEN).scale(tex_scale).next_to(b, UP)
        b_val = Text("42", color=WHITE).scale(tex_scale).move_to(b.get_center())

        a_arrow = Arrow(a.get_center() + np.sin(np.pi / 4) * RIGHT + np.cos(np.pi / 4) * UP,
                        b.get_center() + np.sin(np.pi / 4) * LEFT + np.cos(np.pi / 4) * UP, color=GREEN)
        a_arrow_tex = Text("value == 42", color=WHITE).next_to(a_arrow, UP)
        b_arrow = Arrow(b.get_center() + np.sin(np.pi / 4) * LEFT + np.cos(np.pi / 4) * DOWN,
                        a.get_center() + np.sin(np.pi / 4) * RIGHT + np.cos(np.pi / 4) * DOWN, color=GREEN)
        b_arrow_tex = Text("value == 42", color=WHITE).next_to(b_arrow, DOWN)

        a_false = Text("false", color=RED).next_to(a, RIGHT)
        b_false = Text("false", color=RED).next_to(b, LEFT)
        self.add(a, a_lbl, a_val, b, b_lbl, b_val, a_arrow, a_arrow_tex, b_arrow, b_arrow_tex, a_false, b_false)


class UsingTimestampsIllustration(Scene):
    def construct(self):
        radius = 1
        horizontal = 4
        tex_scale = 1

        a = Circle(color=RED, radius=radius)
        a.shift(horizontal * LEFT)
        a_lbl = Text("A", color=GREEN).scale(tex_scale).next_to(a, UP)
        a_val = MathTex("\emptyset", color=WHITE).scale(tex_scale).move_to(a.get_center())

        b = Circle(color=RED, radius=radius)
        b.shift(horizontal * RIGHT)
        b_lbl = Text("B", color=GREEN).scale(tex_scale).next_to(b, UP)
        b_val = MathTex("\emptyset", color=WHITE).scale(tex_scale).move_to(b.get_center())

        self.add(a, a_lbl, a_val, b, b_lbl, b_val)
        self.wait()

        a_t80 = Arrow(a.get_right(), b.get_left(), color=GREEN)
        a_update = MathTex("t_{80}", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(a_val, a_update), GrowArrow(a_t80))
        self.wait()
        b_update = MathTex("t_{80}", color=WHITE).scale(tex_scale).move_to(b.get_center())
        self.play(Transform(b_val, b_update), FadeOut(a_t80))
        self.wait()

        b_t24 = Arrow(b.get_left(), a.get_right(), color=GREEN)
        b_update = MathTex("t_{24}, t_{80}", color=WHITE).scale(tex_scale).move_to(b.get_center())
        a_update = MathTex("t_{24}, t_{80}", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(b_val, b_update), GrowArrow(b_t24))
        self.wait()
        self.play(FadeOut(b_t24), FadeOut(b_t24), Transform(a_val, a_update))
        self.wait()

        b_t80_ack = Arrow(b.get_left(), a.get_right(), color=BLUE)
        b_t80_ack_text = MathTex("ack(t_{80})", color=WHITE).scale(tex_scale).next_to(b_t80_ack, UP)
        self.play(GrowArrow(b_t80_ack), FadeIn(b_t80_ack_text))
        self.wait()
        self.play(FadeOut(b_t80_ack), FadeOut(b_t80_ack_text))
        self.wait()

        tex_scale = 0.8
        b_t37 = Arrow(b.get_left(), a.get_right(), color=GREEN)
        b_update = MathTex("t_{24}, t_{37}, t_{80}", color=WHITE).scale(tex_scale).move_to(b.get_center())
        a_update = MathTex("t_{24}, t_{37}, t_{80}", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(b_val, b_update), GrowArrow(b_t37))
        self.wait()
        self.play(FadeOut(b_t37), FadeOut(b_t37), Transform(a_val, a_update))
        self.wait()

        a_t37_ack = Arrow(a.get_right(), b.get_left(), color=BLUE)
        a_t37_ack_text = MathTex("ack(t_{37})", color=WHITE).scale(tex_scale).next_to(a_t37_ack, UP)
        self.play(GrowArrow(a_t37_ack), FadeIn(a_t37_ack_text))
        self.wait()
        self.play(FadeOut(a_t37_ack), FadeOut(a_t37_ack_text))
        self.wait()

        a_t24_ack = Arrow(a.get_right(), b.get_left(), color=BLUE)
        a_t24_ack_text = MathTex("ack(t_{24})", color=WHITE).scale(tex_scale).next_to(a_t24_ack, UP)
        self.play(GrowArrow(a_t24_ack), FadeIn(a_t24_ack_text))
        self.wait()
        self.play(FadeOut(a_t24_ack), FadeOut(a_t24_ack_text))
        self.wait()

        tex_scale = 1
        b_update = MathTex("t_{37}, t_{80}", color=WHITE).scale(tex_scale).move_to(b.get_center())
        a_update = MathTex("t_{37}, t_{80}", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(b_val, b_update), Transform(a_val, a_update))
        self.wait()

        b_update = MathTex("t_{80}", color=WHITE).scale(tex_scale).move_to(b.get_center())
        a_update = MathTex("t_{80}", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(b_val, b_update), Transform(a_val, a_update))
        self.wait()

        b_update = MathTex("\emptyset", color=WHITE).scale(tex_scale).move_to(b.get_center())
        a_update = MathTex("\emptyset", color=WHITE).scale(tex_scale).move_to(a.get_center())
        self.play(Transform(b_val, b_update), Transform(a_val, a_update))
        self.wait()

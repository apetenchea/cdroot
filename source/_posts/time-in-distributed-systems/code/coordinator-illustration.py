from manim import *

class CoordinatorIllustration(Scene):
    def construct(self):
        client = ImageMobject("assets/client.jpg")
        client.to_edge(UP)
        coord = ImageMobject("assets/coordinator.jpg")
        dbs = ImageMobject("assets/dbserver.jpg")
        dbs.to_edge(DOWN)
        fs = 48
        self.add(client, coord, dbs)
        q1_arrow = Arrow(client.get_bottom() + LEFT,
                         coord.get_top() + LEFT,
                         color=WHITE, max_tip_length_to_length_ratio=0.1)
        q1_text = MathTex("Q_1", font_size=fs, color=WHITE).next_to(q1_arrow, LEFT)
        anim1 = GrowArrow(q1_arrow)
        q2_arrow = Arrow(client.get_bottom() + RIGHT,
                         coord.get_top() + RIGHT,
                         color=WHITE, max_tip_length_to_length_ratio=0.1)
        q2_text = MathTex("Q_2", font_size=fs, color=WHITE).next_to(q2_arrow, RIGHT)
        anim3 = GrowArrow(q2_arrow)

        q1dbs_arrow = Arrow(coord.get_bottom() + LEFT,
                            dbs.get_top() + LEFT,
                            color=WHITE, max_tip_length_to_length_ratio=0.1)
        anim2 = GrowArrow(q1dbs_arrow, rate_func=rate_functions.not_quite_there(rate_functions.ease_in_sine))
        q1dbs_text = MathTex("Q_1", font_size=fs, color=WHITE).next_to(q1dbs_arrow, LEFT)
        q2dbs_arrow = Arrow(coord.get_bottom() + RIGHT,
                            dbs.get_top() + RIGHT,
                            color=WHITE, max_tip_length_to_length_ratio=0.1)
        anim4 = GrowArrow(q2dbs_arrow, rate_func=rate_functions.exponential_decay)
        q2dbs_text = MathTex("Q_2", font_size=fs, color=WHITE).next_to(q2dbs_arrow, RIGHT)

        self.wait(1)
        text1 = MathTex(r"Sends \ Q_1", font_size=fs, color=WHITE).next_to(client, LEFT)
        self.add(text1)
        self.play(anim1, FadeIn(q1_text), run_time=2)
        self.wait(1)
        text2 = MathTex(r"Forwards \ Q_1",
                        font_size=fs, color=WHITE).next_to(coord, LEFT)
        text3 = MathTex(r"Sends \ Q_2", font_size=fs, color=WHITE).next_to(client, RIGHT)
        self.add(text2, text3)
        self.play(anim3, FadeIn(q2_text), anim2, FadeIn(q1dbs_text), run_time=4)
        text4 = MathTex(r"Forwards \ Q_2", font_size=fs, color=WHITE).next_to(coord, RIGHT)
        text5 = MathTex(r"Q_2 \ arrives \ before \ Q_1", font_size=fs, color=WHITE).next_to(dbs, RIGHT)
        self.wait(1)
        self.add(text4, text5)
        self.play(anim4, FadeIn(q2dbs_text), run_time=2)
        self.wait(2)

from manim import *

class NtpIllustration(Scene):
    def construct(self):
        client_x = -2
        server_x = 2
        t = [2.5, 0.5, -0.5, -2.5]

        # Draw client and server
        d1 = Dot([client_x, t[0], 0])
        client_label = Text("Client").next_to(d1, UP)
        d2 = Dot([server_x, t[0], 0])
        server_label = Text("Server").next_to(d2, UP)
        self.add(d1, client_label, d2, server_label)
        self.wait()

        # Draw t1 -> t2
        d3 = Dot([server_x, t[1], 0])
        d2_d3_line = Line(d2.get_center(), d2.get_center(), color=BLUE)
        d1_d3_arrow = Arrow(d1.get_center(), d3.get_center(), color=BLUE)
        self.add(d3, d2_d3_line)
        t1_label = MathTex("t_1", color=GREEN).next_to(d1, LEFT)
        anim1 = d2_d3_line.animate.put_start_and_end_on(d2.get_center(), d3.get_center())
        anim2 = GrowArrow(d1_d3_arrow)
        self.play(anim1, anim2, FadeIn(t1_label))
        self.wait()
        b1 = Brace(d2_d3_line, direction=RIGHT)
        b1text = b1.get_text("Request time")
        self.play(GrowFromCenter(b1), FadeIn(b1text))
        self.wait()
        t2_label = MathTex("t_2", color=BLUE).next_to(d3, RIGHT)
        self.play(FadeOut(b1), FadeOut(b1text))
        self.play(FadeIn(t2_label))
        self.wait()

        # Draw t2 -> t3
        d4 = Dot([server_x, t[2], 0])
        d3_d4_line = Line(d3.get_center(), d3.get_center(), color=RED)
        self.add(d4, d3_d4_line)
        anim3 = d3_d4_line.animate.put_start_and_end_on(d3.get_center(), d4.get_center())
        self.play(anim3)
        self.wait()
        b2 = Brace(d3_d4_line, direction=LEFT)
        b2text = b2.get_text("Processing time")
        self.play(GrowFromCenter(b2), FadeIn(b2text))
        self.wait()
        t3_label = MathTex("t_3", color=RED).next_to(d4, RIGHT)
        self.play(FadeOut(b2), FadeOut(b2text))
        self.play(FadeIn(t3_label))
        self.wait()

        # Draw t3 -> t4
        d5 = Dot([client_x, t[3], 0])
        d6 = Dot([server_x, t[3], 0])
        d1_d5_line = Line(d1.get_center(), d1.get_center(), color=GREEN)
        d4_d6_line = Line(d4.get_center(), d4.get_center(), color=BLUE)
        d4_d5_arrow = Arrow(d4.get_center(), d5.get_center(), color=BLUE)
        self.add(d5, d1_d5_line, d6, d4_d6_line)
        anim1 = d1_d5_line.animate.put_start_and_end_on(d1.get_center(), d5.get_center())
        anim2 = d4_d6_line.animate.put_start_and_end_on(d4.get_center(), d6.get_center())
        anim3 = GrowArrow(d4_d5_arrow)
        self.play(anim1, anim2, anim3)
        self.wait()
        b3 = Brace(d4_d6_line, direction=RIGHT)
        b3text = b3.get_text("Response time")
        self.play(FadeOut(t3_label), GrowFromCenter(b3), FadeIn(b3text))
        self.wait()
        t4_label = MathTex("t_4", color=GREEN).next_to(d5, LEFT)
        self.play(FadeOut(b3), FadeOut(b3text), FadeIn(t4_label), FadeIn(t3_label))
        self.wait()

        # Translate
        group = VGroup(d3, d4, d3_d4_line, t2_label, t3_label)
        self.play(group.animate.shift(LEFT * (server_x - client_x)), FadeOut(d1_d3_arrow), FadeOut(d4_d5_arrow),
                  FadeOut(server_label), FadeOut(d2), FadeOut(d6), FadeOut(d4_d6_line), FadeOut(d2_d3_line),
                  FadeOut(client_label))
        self.wait()

        # Rotate
        group = VGroup(d3, d4, d3_d4_line, t2_label, t3_label, t1_label, t4_label, d1_d5_line, d1, d5)
        self.add_foreground_mobjects(d3_d4_line)
        t2_label.next_to(d3, LEFT)
        t3_label.next_to(d4, LEFT)
        self.play(group.animate.shift(RIGHT * ((server_x - client_x) / 2)))
        self.wait(0.5)
        self.play(Rotate(group, angle=PI/2))
        rotation = [
            Rotate(t1_label, angle=-PI/2),
            Rotate(t2_label, angle=-PI/2),
            Rotate(t3_label, angle=-PI/2),
            Rotate(t4_label, angle=-PI/2),
        ]
        self.play(*rotation)
        self.wait()

        # Explain
        delta = MathTex(r"\Delta = (t_4 - t_1) - (t_3 - t_2)")
        delta.next_to(d3_d4_line, UP * 8)
        theta = MathTex(r"\Theta = t_3 + \frac{\Delta}{2} - t_4")
        theta.next_to(delta, DOWN)
        self.play(Write(delta))
        self.play(Write(theta))
        self.wait()
from manim import *


class GossipIllustration(Scene):
    def __init__(self):
        super().__init__()
        self.infected = set()

    def construct(self):
        radius = 0.5

        # Create three circle objects
        upper = [Circle(radius=radius, color=RED) for _ in range(3)]
        middle = [Circle(radius=radius, color=RED) for _ in range(5)]
        lower = [Circle(radius=radius, color=RED) for _ in range(3)]

        # Calculate the horizontal and vertical shifts
        width = config.frame_width
        height = config.frame_height
        horizontal_margin_shift = width / 4
        horizontal_middle_shift = width / 5
        vertical_shift = height / 4

        # Position the circles
        for c in upper:
            c.shift(UP * vertical_shift)
        for c in lower:
            c.shift(DOWN * vertical_shift)

        upper[0].shift(LEFT * horizontal_margin_shift)
        lower[0].shift(LEFT * horizontal_margin_shift)
        upper[2].shift(RIGHT * horizontal_margin_shift)
        lower[2].shift(RIGHT * horizontal_margin_shift)
        middle[0].shift(LEFT * horizontal_middle_shift * 2)
        middle[1].shift(LEFT * horizontal_middle_shift)
        middle[3].shift(RIGHT * horizontal_middle_shift)
        middle[4].shift(RIGHT * horizontal_middle_shift * 2)

        middle[2].set_color(BLUE)
        self.infected.add(middle[2])

        self.add(*(upper + middle + lower))
        self.wait()

        self.send_message({"sender": middle[2], "receivers": [middle[3], lower[1]]})
        self.send_message({"sender": middle[3], "receivers": [upper[2], middle[4]]},
                          {"sender": lower[1], "receivers": [lower[0], middle[1]]})
        self.send_message({"sender": middle[4], "receivers": [upper[2], lower[2]]},
                          {"sender": upper[2], "receivers": [upper[1], middle[2]]},
                          {"sender": lower[0], "receivers": [middle[0], upper[0]]},
                          {"sender": middle[1], "receivers": [upper[1], middle[2]]})
        self.send_message({"sender": lower[2], "receivers": [lower[1], middle[2]]},
                          {"sender": upper[1], "receivers": [upper[2], middle[3]]},
                          {"sender": middle[0], "receivers": [upper[0], lower[1]]},
                          {"sender": upper[0], "receivers": [middle[2], middle[1]]})


    def send_message(self, *args):
        arrow_style = dict(
            color=GREEN,
            max_tip_length_to_length_ratio=0.1,
            max_stroke_width_to_length_ratio=1,
        )

        msg_recv_style = dict(
            color=BLUE,
            opacity=1,
        )

        arrows = []
        for arg in args:
            sender = arg["sender"]
            receivers = arg["receivers"]
            arrows.extend([Arrow(sender.get_center(), r.get_center(), **arrow_style) for r in receivers])
        self.play(*[GrowArrow(a) for a in arrows])
        self.wait()

        anims = []
        for arg in args:
            sender = arg["sender"]
            receivers = arg["receivers"]
            anims.extend([
                sender.animate.set_fill(**msg_recv_style),
                *[FadeOut(a) for a in arrows],
                *[r.animate.set_color(BLUE) for r in receivers if r not in self.infected]
            ])
            self.infected.update(receivers)

        self.play(*anims)
        self.wait()

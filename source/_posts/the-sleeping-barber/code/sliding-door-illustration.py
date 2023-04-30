from manim import *


class SlidingDoorIllustration(Scene):
    def construct(self):
        waiting_room = Rectangle(color=BLUE, stroke_width=8)
        waiting_room.shift(LEFT + DOWN)
        workspace = Rectangle(color=BLUE, stroke_width=8)
        workspace.next_to(waiting_room, RIGHT + UP, buff=0)
        workspace.shift(LEFT)
        t1 = Text("Waiting Room").move_to(waiting_room.get_center()).scale(0.5)
        t2 = Text("Workspace").move_to(workspace.get_center()).scale(0.5)
        doors = Line(workspace.get_corner(DL) + LEFT, waiting_room.get_corner(UR), color=RED, stroke_width=8)
        door = Line(workspace.get_corner(DL), waiting_room.get_corner(UR), color=GREEN, stroke_width=8)
        self.add(waiting_room, workspace, t1, t2, doors, door)
        self.play(door.animate.shift(LEFT))
        self.wait()
        self.play(door.animate.shift(RIGHT))
        self.wait()

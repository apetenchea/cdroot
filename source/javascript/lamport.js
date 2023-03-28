/*jshint esversion: 6 */

const LamportClocksGame = (function() {
    let p;
    let parentId;
    let speedSlider;
    let playButton;

    let unitX;
    let unitY;
    let radius;

    let messages = [];
    let nodes = new Map();

    class TextBox {
        constructor(x, y, label, ts) {
            this.label = label;
            this.scale(x, y, ts);
        }

        scale(x, y, ts) {
            this.x = x;
            this.y = y;
            this.textSize = ts;
            this.w = p.textWidth(this.label);
            this.h = p.textAscent() + p.textDescent();
        }

        draw() {
            p.noStroke();
            p.textSize(this.textSize);
            p.text(this.label, this.x, this.y);
        }

        containsPoint(x, y) {
            return x > this.x - this.w / 2 &&
                x < this.x + this.w / 2 &&
                y > this.y - this.h / 2 &&
                y < this.y + this.h / 2;
        }
    }

    class Message {
        constructor(start, r, c, t, target) {
            this.start = start;
            this.x = this.start.x;
            this.y = this.start.y;
            this.r = r;
            this.color = c;
            this.timestamp = t;
            this.target = target;
            this.progress = 0;
            this.speed = speedSlider.value();
        }

        scale(r) {
            this.r = r;
        }

        update() {
            this.progress += this.speed;
            this.x = p.lerp(this.start.x, this.target.x, this.progress);
            this.y = p.lerp(this.start.y, this.target.y, this.progress);
        }

        draw() {
            p.fill(this.color);
            p.stroke(0);
            p.ellipse(this.x, this.y, this.r * 2);
            p.fill(0);
            p.textAlign(p.CENTER, p.CENTER);
            p.textSize(this.r);
            p.text(this.timestamp, this.x, this.y);
        }

        isOngoing() {
            if (this.progress < 1) {
                return true;
            }
            this.target.receiveMessage(this);
        }
    }

    class Node {
        constructor(id, x, y, r, c) {
            this.id = id;
            this.x = x;
            this.y = y;
            this.r = r;
            this.color = c;
            this.counter = 0;
            this.executeText = new TextBox(this.x, this.y - this.r / 1.5, "exec", this.r / 4);
            this.sendText = new TextBox(this.x, this.y + this.r / 1.5, "send", this.r / 4);
        }

        scale(x, y, r) {
            this.x = x;
            this.y = y;
            this.r = r;
            this.executeText.scale(x, y - r / 1.5, r / 4);
            this.sendText.scale(x, y + r / 1.5, r / 4);
        }

        draw() {
            p.fill(...this.color);
            p.stroke(0);
            p.ellipse(this.x, this.y, this.r * 2);
            p.fill(0);
            p.textSize(this.r / 2);
            p.text(this.counter, this.x, this.y);
            this.executeText.draw();
            this.sendText.draw();
        }

        onClick(x, y) {
            const d = p.dist(x, y, this.x, this.y);
            if (d > this.r) {
                return;
            }
            if (this.executeText.containsPoint(x, y)) {
                this.executeEvent();
            } else if (this.sendText.containsPoint(x, y)) {
                this.sendMessage();
            }
        }

        executeEvent() {
            ++this.counter;
        }

        sendMessage() {
            ++this.counter;
            nodes.forEach((node) => {
                if (this.id !== node.id) {
                    messages.push(new Message(this, radius / 4, this.color, this.counter, node));
                }
            });
        }

        receiveMessage(msg) {
            this.counter = p.max(this.counter, msg.timestamp);
            ++this.counter;
        }
    }

    function getNodesSetup() {
        return [
            {id: "A", x: p.width / 2, y: unitY + radius, c: [181, 189, 104]},
            {id: "B", x: unitX + radius, y: p.height - unitY - radius, c: [138, 190, 183]},
            {id: "C", x: p.width - unitX - radius, y: p.height - unitY - radius, c: [204, 153, 204]}
        ];
    }

    function scale() {
        let width = document.getElementById(parentId).clientWidth;
        let height = document.getElementById(parentId).clientHeight;

        unitX = width / 10;
        unitY = height / 10;
        radius = unitX / 1.5;

        return [width, height];
    }

    function setup() {
        const [width, height] = scale();
        let canvas = p.createCanvas(width, height);
        canvas.parent(parentId);

        playButton = p.createButton("Play");
        playButton.position(unitX / 5, unitY / 5);
        playButton.size(unitX);
        playButton.mousePressed(() => {
            if (playButton.html() === "Play") {
                playButton.html("Pause");
            } else {
                playButton.html("Play");
            }
        });

        speedSlider = p.createSlider(0.005, 0.05, 0.02, 0.005);
        speedSlider.position(unitX / 5, playButton.height + unitY / 3);
        speedSlider.size(unitX);
        p.textAlign(p.CENTER, p.CENTER);
        p.rectMode(p.CENTER);

        getNodesSetup().forEach((node) =>
            nodes.set(node.id, new Node(node.id, node.x, node.y, radius, node.c))
        );
    }

    function draw() {
        p.background(33, 35, 38);

        nodes.forEach((node) => node.draw());
        messages = messages.filter((msg) => msg.isOngoing());
        messages.forEach((msg) => {
            msg.update();
            msg.draw();
        });
    }

    function windowResized() {
        const [width, height] = scale();
        p.resizeCanvas(width, height);
        messages.forEach((msg) => msg.scale(radius / 4));
        getNodesSetup().forEach((node) => nodes.get(node.id).scale(node.x, node.y, radius));
        playButton.position(unitX / 5, unitY / 5);
        playButton.size(unitX);
        speedSlider.position(unitX / 5, playButton.height + unitY / 3);
        speedSlider.size(unitX);
    }

    function mouseClicked() {
        for (let node of nodes.values()) {
            node.onClick(p.mouseX, p.mouseY);
        }
    }

    return {
        "gameEnv": function(_parentId) {
            parentId = _parentId;
        },
        "newGame": function(_p) {
            p = _p;
            p.setup = setup;
            p.draw = draw;
            p.mouseClicked = mouseClicked;
            p.windowResized = windowResized;
        }};
})();
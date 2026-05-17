import turtle
import time

t = turtle.Turtle()
turtle.bgcolor("black")
t.color("red")
t.speed(2)

# 画心形
t.penup()
t.goto(0,-100)
t.pendown()
t.begin_fill()
t.left(140)
t.forward(224)
for _ in range(200):
    t.right(1)
    t.forward(2)
t.left(120)
for _ in range(200):
    t.right(1)
    t.forward(2)
t.forward(224)
t.end_fill()

# 写文字
t.penup()
t.goto(0,0)
t.color("white")
t.write("我在想你", align="center", font=("Arial", 24, "bold"))
time.sleep(5)
turtle.done()
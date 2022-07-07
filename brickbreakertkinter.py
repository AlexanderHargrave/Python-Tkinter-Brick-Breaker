import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import PhotoImage
from random import randint
import time
import os.path

# Resolution of game is 1440x900.
# Comments on this are normally below the code it is describing/about.
# List of cheats and their binds in cheatsheet.txt file
# Base mechanics for collisions and movement comes from;
# "https://www.studytonight.com/tkinter/brick-breaker-game-using-tkinter-python-project"


class Object(object):  # The class is base inheritance of objects.
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def delete(self):
        self.canvas.delete(self.item)

    def set_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)


class Ball(Object):
    def __init__(self, canvas, x, y):
        # This is used for the ball's base stats.
        global speed
        self.radius = 15
        self.speed = speed
        self.direction = [1, -1]
        canvas.bind("<a>", lambda _: self.press_a())
        # This is to set direction to left before launch, binded to <a>.
        canvas.bind("<d>", lambda _: self.press_d())
        # This is to set direction to right before launch, binded to <d>.
        canvas.bind("<Down>", lambda _: self.speed_cheat_down())
        # This is a bind to a cheat to decrease speed, binded to down key.
        canvas.bind("<Up>", lambda _: self.speed_cheat_up())
        # This is a bind to a cheat to increase speed, binded to up key.

        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill="Yellow", outline="Gold")
        # Creation of what the ball looks like.
        super(Ball, self).__init__(canvas, item)

    def update(self):  # This is run constantly to move the ball.
        co_ords = self.set_position()
        width = self.canvas.winfo_width()
        if (co_ords[0] <= 0) or (co_ords[2] >= width):
            # This is for the walls on the sides
            self.direction[0] *= -1
        if (co_ords[1] <= 0):
            # This is the ceiling
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        # Since all parts of direction are 1 or -1,
        # All movements are in diagnols, 45 degrees.
        self.move(x, y)

    def press_a(self):  # This function changes start launch to left.
        self.direction = [-1, -1]
        self.canvas.unbind("<a>")
        # Developer cheat: if all turned off, allows control of ball middair.
        self.canvas.unbind("<d>")
        # Developer cheat: if all turned off, allows control of ball middair.

    def press_d(self):  # The function changes start launch to left.
        self.direction = [1, -1]
        self.canvas.unbind("<d>")
        # Developer cheat: if all turned off, allows control of ball middair.
        self.canvas.unbind("<a>")
        # Developer cheat: if all turned off, allows control of ball middair.

    def speed_cheat_down(self):  # This function is to lower speed.
        global speed
        if speed > 10:
            speed -= 3

    def speed_cheat_up(self):  # This function if to increase speed.
        global speed
        if speed < 25:
            speed += 3

    def change_colour(self):
        # This function is to change ball colour randomly.
        colour_list = ["Red", "Yellow", "Black", "White", "Green", "Blue"]
        num = randint(0, 5)
        return colour_list[num]

    def collision(self, widgets):
        # This function is to check collisions and change direction if needed.
        # This function also allows the ball to change colour
        co_ords = self.set_position()
        x = (co_ords[0] + co_ords[2]) * 0.5

        if (len(widgets)) > 1:
            # To uncomplicate what happens with collision with 2 bricks
            self.direction[1] *= -1
            self.canvas.itemconfig(self.item, fill=self.change_colour())
        elif (len(widgets)) == 1:
            widget = widgets[0]
            co_ords = widget.set_position()
            if (x > co_ords[2]):
                self.direction[0] = 1
            elif (x < co_ords[0]):
                self.direction[0] = -1
            else:
                self.canvas.itemconfig(self.item, fill=self.change_colour())
                self.direction[1] *= -1
        else:
            pass

        for i in widgets:
            if (isinstance(i, Brick)):
                i.hit()


class Paddle(Object):  # This is the class for Paddle.
    def __init__(self, canvas, x, y):  # Creation of paddle.
        self.length = 150
        self.height = 15
        self.ball = None
        item = canvas.create_rectangle(x - self.length / 2,
                                       y - self.height / 2,
                                       x + self.length / 2,
                                       y + self.height / 2,
                                       fill="Silver",
                                       outline="Gold",
                                       activefill="Gold")
        # Creation of silver rectangle and gold outline as the Paddle.
        super(Paddle, self).__init__(canvas, item)

    def place_ball(self, ball):
        self.ball = ball

    def paddle_move(self, right):
        # Allows specified movement of paddle later in the code, base = 30
        co_ords = self.set_position()
        width = self.canvas.winfo_width()
        paddle_speed = 30
        # This is how fast the paddle will move
        if right is True:
            difference = paddle_speed
        elif right is False:
            difference = -paddle_speed
        if (co_ords[0] + difference >= 0) and \
                (co_ords[2] + difference <= width):
            self.move(difference, 0)
            if (self.ball is not None):
                self.ball.move(difference, 0)


class Brick(Object):  # Brick class with inheritance of Object.
    colours = {1: "Red", 2: "Orange", 3: "Yellow", 4: "Dark Blue"}
    # This is a dictionary of colours and hits for bricks.
    # This is to assign a colour to the NO. hits needed to break the brick.

    def __init__(self, canvas, x, y, hits):
        # This is to assign base stats to bricks.
        # The width is 144 to allow for 10 bricks to fit in a 1440 wide screen.
        self.width = 144
        self.height = 20
        self.hits = hits
        colour = Brick.colours[hits]
        item = canvas.create_rectangle(x - self.width * 0.5,
                                       y - self.height * 0.5,
                                       x + self.width * 0.5,
                                       y + self.height * 0.5,
                                       fill=colour,
                                       outline="Black",
                                       tags="brick")
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # The functions that lowers the hit counts of bricks.
        # It also deletes them when hit count becomes smaller than 0.
        global ball_strength
        self.hits -= ball_strength
        if (self.hits <= 0):
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.colours[self.hits])
            # Change colour of brick after being hit


class BrickBreakerGame(tk.Frame):  # Most of game functions in this class.
    def __init__(self, master):
        global levels
        super(BrickBreakerGame, self).__init__(master)
        self.items = {}
        self.width = 1440
        self.height = 900
        self.lives = 2
        self.scores = 0
        self.canvas = tk.Canvas(self, bg="Grey", width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()
        self.ball = None
        self.paddle = Paddle(self.canvas, 720, 800)
        # Creation of the paddle on the canvas
        self.items[self.paddle.item] = self.paddle
        self.hud = None
        self.hud2 = None

        # Start of a list of binds for multiple functions.
        self.canvas.focus_set()
        self.canvas.bind("<Left>", lambda _: self.paddle.paddle_move(False))
        self.canvas.bind("<Right>", lambda _: self.paddle.paddle_move(True))
        self.canvas.bind("<b>", lambda _: self.boss_key())
        self.canvas.bind("<p>", lambda _: self.pause())
        self.canvas.bind("<c>", lambda _: self.cont())
        self.canvas.bind("<l>", lambda _: self.leaderboard())
        self.canvas.bind("<h>", lambda _: self.help())
        self.canvas.bind("<s>", lambda _: self.save())
        # End of a list of binds for multiple functions.

        save_file_exist = os.path.isfile("Savefile.txt")
        load = False
        if save_file_exist is True:
            # Checking to see if a save file already exists.
            load = messagebox.askyesno(
                    "Loading", "You have a save file, do you wish to load it?"
                    )
        if load is True:  # A code that loads a save file into game.
            with open("Savefile.txt") as s:
                loadfile = s.readline()
                loadfilel = loadfile.split(":")
                levels = int(loadfilel[0])
                self.lives = int(loadfilel[1])
                self.scores = (levels-1) * (levels-2) * 50
        self.add_levels(self.width, self.height)
        self.setup_game()

        if (os.path.isfile("./Leaderboard.txt") is False and
                os.path.isfile("./Savefile.txt") is False):
            # This is to give the help image for most likely first time user.
            # This is because since no save file or leaderboard.
            # This means no previous save or finished game so first time user.
            self.help()
            self.cont()

    def setup_game(self):
        # A function for start of game and after each life.
        global levels
        self.update_lives_text()
        self.update_scores()
        self.add_ball()

        self.text = self.drawtext(720, 500, "Please press Space to Start")
        self.canvas.bind("<space>", lambda _: self.start_game())
        self.canvas.bind("<q>", lambda _: self.qwertyq())
        # This is to bind <q> to start a cheat of 'qwerty'.
        # This cheat gives extra lives.
        self.canvas.bind("1", lambda _: self.instant_brick_kill1())
        # This is to bind '1' to start a cheat of '123'.
        # This cheat gives the ability to destroy each brick in one hit.

    def instant_brick_kill1(self):
        # This is activated with '1' pressed to start '123' cheat.
        self.canvas.unbind("1")
        self.canvas.bind("2", lambda _: self.instant_brick_kill2())

    def instant_brick_kill2(self):
        self.canvas.unbind("2")
        self.canvas.bind("3", lambda _: self.instant_brick_kill3())

    def instant_brick_kill3(self):
        # After '3' is pressed, activates cheat.
        # This cheat sets all bricks to lose 4 in hits so all brick are on hit.
        # ibk stands for instant brick kill.
        global ball_strength
        self.canvas.unbind("3")
        ball_strength = 4
        self.canvas.bind("3", lambda _: self.cancel_instant_brick_kill3())
        ibk_cheat_text = ("You have activated cheat '123',"
                          "you now have instant brick kill cheat")
        ibk_cheat_texts = self.drawtext(720, 850, ibk_cheat_text, 20)
        self.canvas.itemconfig(ibk_cheat_texts, text=ibk_cheat_text)
        self.after(1500, lambda: self.canvas.delete(ibk_cheat_texts))

    def cancel_instant_brick_kill3(self):
        # After the '123' cheat is activated, it can be cancelld with '321'.
        # This function is to start cancel of instant brick kill.
        self.canvas.unbind("3")
        self.canvas.bind("2", lambda _: self.cancel_instant_brick_kill2())

    def cancel_instant_brick_kill2(self):
        self.canvas.unbind("2")
        self.canvas.bind("1", lambda _: self.cancel_instant_brick_kill1())

    def cancel_instant_brick_kill1(self):
        # This ends up cancelling the '123' cheat.
        # This is done by setting ball_strength to 1 so hits only subtract 1.
        # After this, '1' is binded again to allow for '123' to be activated.
        global ball_strength
        self.canvas.unbind("1")
        ball_strength = 1
        self.canvas.bind("1", lambda _: self.instantbrickkill1())
        ibk_cheat_text = ("You have disabled cheat '123' with '321', "
                          "instant brick kill cheat is disabled")
        ibk_cheat_texts = self.drawtext(725, 850, ibk_cheat_text, 20)
        self.canvas.itemconfig(ibk_cheat_texts, text=ibk_cheat_text)
        self.after(1500, lambda: self.canvas.delete(ibk_cheat_texts))

    def qwertyq(self):
        # Start of the 'qwerty' cheat, binds with <q>.
        self.canvas.unbind("<q>")
        self.canvas.bind("<w>", lambda _: self.qwertyw())

    def qwertyw(self):
        self.canvas.unbind("<w>")
        self.canvas.bind("<e>", lambda _: self.qwertye())

    def qwertye(self):
        self.canvas.unbind("<e>")
        self.canvas.bind("<r>", lambda _: self.qwertyr())

    def qwertyr(self):
        self.canvas.unbind("<r>")
        self.canvas.bind("<t>", lambda _: self.qwertyt())

    def qwertyt(self):
        self.canvas.unbind("<t>")
        self.canvas.bind("<y>", lambda _: self.qwertyy())

    def qwertyy(self):
        # End of 'qwerty' cheat, when activated gives 15 extra lives.
        self.canvas.unbind("<y>")
        self.canvas.bind("<q>", lambda _: self.qwertyq())
        self.lives += 15
        self.update_lives_text()
        lives_cheat_text = ("You have activated cheat code 'qwerty', "
                            "you have gained 15 lives")
        live_cheat_texts = self.drawtext(720, 850, lives_cheat_text, 20)
        self.canvas.itemconfig(live_cheat_texts, text=lives_cheat_text)
        self.after(1500, lambda: self.canvas.delete(live_cheat_texts))

    def boss_key(self):
        # This is the function to activate a boss key.
        # This makes an image of code pop up when <b> is pressed.
        self.pause()
        boss_key_window = tk.Toplevel()
        boss_key_img = tk.PhotoImage(file="Screenshotofcode.gif")
        # The image used is an image of code developed bymyself.
        label = tk.Label(boss_key_window, image=boss_key_img)
        label.image = boss_key_img
        label.grid(row=0, column=0)

    def add_ball(self):
        # Creation of ball above paddle and attached to it.
        if (self.ball is not None):
            self.ball.delete()
        paddle_coords = self.paddle.set_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 777)
        self.paddle.place_ball(self.ball)

    def add_brick(self, x, y, hits):
        # A function to create a brick with different characteristics.
        # These characteristics are co-ordinates and number of hits.
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def add_levels(self, x, y):
        # Creation of level function.
        # This function changes difficulty dependent on level.
        # Up to level 15, every 3 levels add an extra layer of bricks.
        # Also each additional level increases chance for more bricks per row.
        # Finally each level increases chance of bricks with higher hit count.
        # The variable n is number of rows per level.
        self.scores += levels * 100 - 100
        # This is to add the score per level completed.
        # The higher the level, greater score gained.
        if (levels <= 3):
            n = 2
        elif (levels <= 6):
            n = 3
        elif (levels <= 9):
            n = 4
        elif (levels <= 12):
            n = 5
        elif (levels <= 15):
            n = 6
        else:
            n = 7
        for l in range(0, n):
            for i in range(0, 1440, 144):
                # This means creation of 10 bricks per level.
                # Variable 'h' is number of hits on the brick
                num = randint(1, 100)
                hitrandom = randint(1, 100)
                if (hitrandom >= 99 - levels):
                    h = 4
                elif (hitrandom >= 90 - levels):
                    h = 3
                elif (hitrandom >= 60 - levels):
                    h = 2
                else:
                    h = 1

                if (num >= 60 - levels):
                    # This randomises number of bricks per row per level.
                    # Higher the level, higher chance for more bricks per row.
                    self.add_brick(i + 72, 70 + 20 * l, h)

    def drawtext(self, x, y, text, size="40"):
        # This creates a base format for most outputted to canvas.
        writing_format = ("Times", size)
        return self.canvas.create_text(x, y, text=text, font=writing_format)

    def update_lives_text(self):
        # This is to be binded to a corner to constantly update NO. lives.
        text = "Lives Left: %s" % self.lives
        if (self.hud is None):
            self.hud = self.drawtext(180, 860, text, 40)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_scores(self):
        # This is to be binded to a corner to constantly update score.
        score_count = "Score: %s" % self.scores
        if (self.hud2 is None):
            self.hud2 = self.drawtext(1300, 860, score_count, 40)
        else:
            self.canvas.itemconfig(self.hud2, text=score_count)

    def start_game(self):
        # This is a function to get rid of starting text.
        # This also places a lot of buttons on the top of the canvas.
        # It also forces a check every 200 ms to see if pause is activated.
        self.canvas.unbind('<space>')
        self.cont()
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.update_scores()

        continue_button = tk.Button(self.canvas, text="Continue",
                                    command=self.cont)
        continue_button.place(x=20, y=10)
        # A button to continue after a pause.
        # This is to be done after pause, leaderboard, help and boss key.
        giveup_button = tk.Button(self.canvas, text="End Game",
                                  command=self.giveup)
        giveup_button.place(x=300, y=10)
        # A button to quickly end the game, set lives = 0.
        leaderboard_button = tk.Button(self.canvas, text="Leaderboards",
                                       command=self.leaderboard)
        leaderboard_button.place(x=550, y=10)
        # A button to show leaderboard of top 10 records on the computer..
        save_button = tk.Button(self.canvas, text="Save", command=self.save)
        save_button.place(x=800, y=10)
        # Creates a save file for the game.
        # This saves the level and lives left.
        # Score is not needed as it can be calculated from level.
        help_button = tk.Button(self.canvas, text="Help", command=self.help)
        help_button.place(x=1050, y=10)
        # A button to prevent an image created by myself as a basic guide.
        pause_button = tk.Button(self.canvas, text="Pause", command=self.pause)
        # A button to pause the game.
        pause_button.place(x=1350, y=10)

        self.after(200, self.running)
        # Used to check every 200 ms if game is paused
        self.gameloop()

    def pause(self):
        # Function pauses with running() function as ball stops moving.
        global on
        on = False

    def cont(self):
        # Function that is used to continue whenether game is paused.
        global on
        on = True

    def running(self):
        # This is run every 200ms to check if game is paused.
        # If pause is pressed, ball speed becomes 0.
        global speed
        if (on):
            self.ball.speed = speed
        else:
            self.ball.speed = 0
        self.after(200, self.running)

    def giveup(self):
        # Function that sets lives to 0 to quickly end game.
        self.lives = 0
        self.update_lives_text()

    def save(self):
        # This creates/overwrites a save file.
        # The current level and lives left is sent to the save file.
        global levels
        s = open("Savefile.txt", "w")
        s.write(str(levels)+":"+str(self.lives))
        declare_save = "You have saved the game"
        declare_save_d = self.drawtext(720, 850, declare_save, 30)
        self.canvas.itemconfig(declare_save_d, text=declare_save)
        self.after(1000, lambda: self.canvas.delete(declare_save_d))

    def help(self):
        # This functions creates a window of a help sheet image.
        self.pause()

        helpwindow = tk.Toplevel()
        helpwindow.attributes('-topmost', 1)
        helpimg = tk.PhotoImage(file="instructionsbrickbreaker.gif")
        # This image is created by myself.
        label = tk.Label(helpwindow, image=helpimg)
        label.image = helpimg
        label.grid(row=0, column=0)

    def leaderboard(self):
        # Creates a leaderboard of top 10 scores recorded.
        # If no previous records, outputs no previous leaderboards.
        # If more than 10 records, show only top 10.
        self.pause()

        fileexists = os.path.isfile("./Leaderboard.txt")
        if fileexists is False:
            openlb = tk.messagebox.showinfo("Leaderboard",
                                            "You have no previous "
                                            "leaderboard entries")
        elif fileexists is True:
            with open("Leaderboard.txt") as l:
                # lbl stands for leaderboardl
                lbl = l.readlines()
                lbl = [line.rstrip().split(":") for line in lbl]
                lbl = [(i[0], int(i[1])) for i in lbl]
                lbl.sort(key=lambda tup: tup[1], reverse=True)
                lengthleaderboard = len(lbl)
                message = ""
                if lengthleaderboard > 10:
                    lengthleaderboard = 10
                for i in range(0, lengthleaderboard):
                    message += (str(i + 1) + ")" + str(lbl[i][0]) +
                                ": " + str(lbl[i][1]) + "\n")
                message += ("Please press the continue "
                            "button to continue playing")
                openlb = tk.messagebox.showinfo("Leaderboard", message)

    def gameloop(self):
        # This is constantly run.
        global levels
        global speed
        global scores

        self.check_collisions()
        if (len(self.canvas.find_withtag("brick"))) == 0:
            # This is used to check when the number of bricks in a level is 0.
            # If this is so, it creates the enxt level.
            level_complete = "You have finished level " + str(levels)
            levelcoords = self.drawtext(720, 300, level_complete, 100)
            self.canvas.itemconfig(levelcoords, text=level_complete)
            # This is used to output the temporary message of level complete.
            self.ball.update()
            self.after(2500, lambda: self.canvas.delete(levelcoords))

            levels += 1
            self.add_levels(self.width, self.height)
            self.update_scores()
            self.canvas.delete(self.text)
            self.ball.update()
            self.after(50, self.gameloop)
            randomlife = randint(1, 100)
            if (randomlife >= 70):
                # This is used for a 30% chance for an extra life per level.
                special_level = "Congratulations for winning an extra life!"
                special_level_text = self.drawtext(720, 500,
                                                   special_level, 40)
                self.canvas.itemconfig(special_level_text, text=special_level)
                self.after(1500,
                           lambda: self.canvas.delete(special_level_text))
                self.lives += 1
                rungame.update_lives_text()

        elif self.ball.set_position()[3] >= self.height:
            # This is used for whether the ball hits the bottom floor.
            # This results in loss of life and if no lives left, ends game.
            # This results in asking for name for leaderboard entry.
            self.ball.speed = None
            self.lives -= 1
            if (self.lives < 0):
                end_game = "Game Over!"
                end_game_text = self.drawtext(720, 500, end_game, 100)
                self.canvas.itemconfig(end_game_text, text=end_game)
                self.after(2500, lambda: self.canvas.delete(end_game_text))

                askname = simpledialog.askstring(title="Name",
                                                 prompt="Whats your Name?: ")
                f = open("Leaderboard.txt", "a")
                f.write(askname + ":" + str(self.scores))
                f.write("\n")
                # This is used to rerun the game from the beginning
                self.lives = 2
                self.scores = 0
                levels = 1

                self.canvas.delete('brick')
                # Delete all bricks in the game
                self.add_levels(self.width, self.height)
                self.after(1700, self.setup_game)
                self.update_scores()

                restart_game = "Game Restarted!"
                restart_game_text = self.drawtext(720, 850, restart_game, 40)
                self.canvas.itemconfig(restart_game_text, text=restart_game)
                self.after(999, lambda: self.canvas.delete(restart_game_text))

            else:
                self.after(1000, self.setup_game)
                lost_life = "You have lost a life!"
                lost_life_text = self.drawtext(720, 850, lost_life, 30)
                self.canvas.itemconfig(lost_life_text, text=lost_life)
                self.after(999, lambda: self.canvas.delete(lost_life_text))
                # Used to respawn after death if theres still lives left.
        else:
            self.ball.update()
            self.after(40, self.gameloop)

    def check_collisions(self):
        # This checks for the co-ordinates of the ball and overlapping objects
        # Then runs the collision functions
        ball_co_ords = self.ball.set_position()
        items = self.canvas.find_overlapping(*ball_co_ords)
        objects_list = []
        for x in items:
            if x in self.items:
                objects_list.append(self.items[x])
        self.ball.collision(objects_list)

levels = 1  # global
scores = 0  # global
speed = 15  # global
ball_strength = 1  # global
on = True  # global
if (__name__ == "__main__"):
    # This is used to only run when this is the main program.
    root = tk.Tk()
    root.title("Brick Breaker")
    rungame = BrickBreakerGame(root)
    rungame.mainloop()
    # This is needed at the end.

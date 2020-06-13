import viz
import vizshape
import random
import time
import vizact
import vizmat
import numpy as np
import scipy as sp
from scipy.spatial.transform import Rotation as R

viz.go()
#vizshape.addAxes()

SIZE = 20

#viz.MainView.setEuler(-45,0,0)
viz.MainView.setPosition(0,0,0)
viz.MainWindow.fov(100)

newView = viz.addView()
newView.setPosition([SIZE/2, SIZE/2, SIZE/2])
newView.lookAt([0,0,0])
newwindow = viz.addWindow()
newwindow.setView(newView)
newwindow.fov(80)
def build_env():
	spaceSize = SIZE
	half = SIZE/2
	borders = [viz.addTexQuad(size=spaceSize) for x in range(6)]
	borders[0].setPosition([half, 0, 0])
	borders[1].setPosition([-half, 0, 0])
	borders[2].setPosition([0, half, 0])
	borders[3].setPosition([0, -half, 0])
	borders[4].setPosition([0, 0, half])
	borders[5].setPosition([0, 0, -half])
	
	borders[0].setAxisAngle([0,1,0,-90])
	borders[1].setAxisAngle([0,1,0,90])
	borders[2].setAxisAngle([1,0,0,90])
	borders[3].setAxisAngle([1,0,0,-90])
	borders[4].setAxisAngle([0,0,0,90])
	borders[5].setAxisAngle([0,0,0,-90])
	
	grid = viz.addTexture('grid.png')
	roof = viz.addTexture('roof.png')
	floor = viz.addTexture('floor.png')
	wall = viz.addTexture('wall.png')
	for t in [grid, floor, roof, wall]:
		t.wrap(viz.WRAP_S, viz.REPEAT)
		t.wrap(viz.WRAP_T, viz.REPEAT)
	
	matrix = vizmat.Transform()
	scale = matrix.getScale()
	scale[0] = scale[1] = SIZE
	matrix.setScale(scale)
	
	def setTex(b, t):
		b.texture(t, '', 0)
		b.texmat(matrix, '', 0)
		#print(b.getAxisAngle())
	setTex(borders[0], wall)
	setTex(borders[1], wall)
	setTex(borders[4], wall)
	setTex(borders[5], wall)
	setTex(borders[2], roof)
	setTex(borders[3], floor)
	
class Snake():
	def __init__(self, x=0, y=0, z=0, len=3):
		self.local_X = [fx,fy,fz] = [1,0,0]
		self.local_Y = [0,1,0]
		self.len = len
		self.body = [self.makeBodyBox(x,y,z)]
		for i in range(self.len - 1):
			formerBox = self.body[i]
			[xx,yy,zz] = formerBox.getPosition()
			self.body.append(self.makeBodyBox(xx-fx,yy-fy,zz-fz))
		print self.body[0].getAxisAngle()
			
	def makeBodyBox(self, x, y, z):
		box = vizshape.addCube(1)
		box.setPosition([x,y,z])
		box.color([128,64,0])
		return box
		
	def move(self):
		headBox = self.body[0]
		[xx,yy,zz] = headBox.getPosition()
		[fx,fy,fz] = self.local_X
		newBox = self.makeBodyBox(xx+fx, yy+fy, zz+fz)
		self.body.insert(0,newBox)
		self.setView()
		
		global apple
		if apple and newBox.getPosition() == apple.body.getPosition():
			self.len += 1
			del apple
			apple = None
			print("Ate an apple !")
		else:
			oldBox = self.body.pop(-1)
			oldBox.remove()
			
		banPos = [b.getPosition() for b in self.body[1:]]
		nowPos = self.body[0].getPosition()
		if nowPos in banPos:
			GameOver()
		if abs(xx) >SIZE/2 or abs(yy) >SIZE/2 or abs(zz) >SIZE/2:
			GameOver()
		'''
		print('------------')
		print("Heading :",self.local_X)
		print("Up      :",self.local_Y)
		print("location:",newBox.getPosition())
		'''
		
	def up(self):
		[x1,y1,z1] = self.local_X
		[x2,y2,z2] = self.local_Y
		self.local_X = [x2,y2,z2]
		self.local_Y = [-x1,-y1,-z1]
		
	def down(self):
		[x1,y1,z1] = self.local_X
		[x2,y2,z2] = self.local_Y
		self.local_X = [-x2,-y2,-z2]
		self.local_Y = [x1,y1,z1]
	
	def left(self):
		# Y x X
		[x1,y1,z1] = self.local_X
		[x2,y2,z2] = self.local_Y
		self.local_X = [y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2]
		
	def right(self):
		# X * Y
		[x1,y1,z1] = self.local_X
		[x2,y2,z2] = self.local_Y
		self.local_X = [- y1*z2 + z1*y2, - z1*x2 + x1*z2, - x1*y2 + y1*x2]
	
	def setView(self):
		headBox = self.body[0]
		pos = [xx,yy,zz] = headBox.getPosition()
		Xt = [x1,y1,z1] = self.local_X
		Yt = [x2,y2,z2] = self.local_Y
		
		#viz.MainView.setPosition([xx + x1/2., yy + y1/2., zz + z1/2.])
		viz.MainView.setPosition([xx - 2 * x1 + 2 * x2, yy - 2 * y1 + 2 * y2, zz - 2 * z1 + 2 * z2])
		
		xt = np.array(Xt)
		yt = np.array(Yt)
		zt = np.cross(xt,yt)
		rot = np.vstack([xt,yt,zt]).transpose().dot(np.array([[0,0,1],[0,1,0],[-1,0,0]]))
		r = R.from_dcm(rot)
		[x,y,z,w] = list(r.as_quat())
		viz.MainView.reset(viz.HEAD_ORI)
		viz.MainView.setQuat([x,y,z,w])
		#print(viz.MainView.getEuler())
		
		
class Apple():
	def __init__(self,x,y,z):
		self.body = vizshape.addCube(1)
		self.body.setPosition([x,y,z])
		self.body.color([200,0,0])
		print("Apple generated.")
		
	def __del__(self):
		self.body.remove()
		
def generateApple(size, bodys):
	banPos = [b.getPosition() for b in bodys]
	
	appPos = banPos[0]
	while appPos in banPos:
		appPos = (random.randint(-size/2 + 1, size/2-1),
			random.randint(-size/2 + 1, size/2-1),
			random.randint(-size/2 + 1, size/2-1))
			
	return Apple(*appPos)
	
		
def Loop():
	global apple
	global snake
	if not apple:
		apple = generateApple(SIZE, snake.body)
	#snake.move()
	
def GameOver(msg=''):
	viz.MainView.setPosition(110,0,0)
	newView.setPosition(000, 100, 0)
	gameover = viz.addText('GAME OVER',viz.SCREEN)
	gameover.scale(2,2,2)
	gameover.translate(0,0.5)
	

build_env()
snake = Snake(len = 5)
apple = None

vizact.ontimer(1, Loop)
vizact.onkeydown('w',snake.up)
vizact.onkeydown('s',snake.down)
vizact.onkeydown('a',snake.left)
vizact.onkeydown('d',snake.right)
vizact.onkeydown('m',snake.move)
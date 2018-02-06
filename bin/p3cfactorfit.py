import numpy as np
from scipy.optimize import curve_fit

def Cf(X, a, b, c):
    Dose,Drift = X
    return a + b*Dose + c*np.log(Drift)

# array to get bfactors
csv = np.genfromtxt ('/home/kailu/frame-drift-bf.csv', delimiter=",")
Dose = csv[:,0]
Drift = csv[:,1]
bf = csv[:,2]
# initial guesses for a,b,c:
p0 = 1., 1., 1.
popt, pcov = curve_fit(Bf, (Dose,Drift), bf, p0)
print popt
print pcov

'''
import matplotlib.pyplot as plt
plt.plot(Dose, z, 'b-', label='data')
plt.plot(Dose, Bf((Dose,Drift), *popt), 'r-', label='fit')
plt.xlabel('Dose')
plt.ylabel('Bfactor')
plt.legend()
plt.savefig('zz.png')

from numpy import exp,arange
from pylab import meshgrid,cm,imshow,contour,clabel,colorbar,axis,title,show,savefig

# the function that I'm going to plot
def z_func(x,y):
    return (1-(x**2+y**3))*exp(-(x**2+y**2)/2)
 
x = arange(0,30,1)
y = arange(0.001,30,1)
X,Y = meshgrid(x, y) # grid of point
#Z = z_func(X, Y) # evaluation of the function on the grid

Z = Bf((X,Y), *popt)
im = imshow(Z,cmap=cm.RdBu) # drawing the function
# adding the Contour lines with labels

#cset = contour(Z,arange(1,30,0.2),linewidths=2,cmap=cm.Set2)
#clabel(cset,inline=True,fmt='%1.1f',fontsize=10)
colorbar(im) # adding the colobar on the right

# latex fashion title
title('Bfactor= 60 - 10*Dose - 55*ln(Drift)')
show()
savefig('tt.png')


def main():
	progname = os.path.basename(sys.argv[0])
	usage = progname + """ [options] <*_bfactors.star>
	Fit .
	Prep1: make a new folder
	       mkdir polishPerPtcl;cd polishPerPtcl
	Prep2: link the intermediate maps (rootname: shiny-nodrift)
	       ln -s ../Refine3D/*_shiny-nodrift_*half?_class001_unfil.mrc .;cd ..
	"""
	
	args_def = {'apix':0.6575, 'bfile':'', 'polish':'', 'run':'','rootshiny':'shiny-nodrift'}	
	parser = argparse.ArgumentParser()
	parser.add_argument("drift", nargs='*', help="specify the Patch-FitCoeff.log files")
	parser.add_argument("-a", "--apix", type=float, help="specify apix, by default {}".format(args_def['apix']))
	parser.add_argument("-b", "--bfile", type=str, help="specify the old _bfactors.star file, by default {}".format(args_def['bfile']))
	parser.add_argument("-p", "--polish", type=str, help="specify the input data file for the old polish, e.x., run1_data-for-polish.star, do not put this file in current folder, by default {}".format(args_def['polish']))
	parser.add_argument("-r", "--run", type=str, help="specify the command file to run polish, by default {}".format(args_def['polish']))
	parser.add_argument("-rs", "--rootshiny", type=str, help="specify the root name for polish, by default {}".format(args_def['rootshiny']))
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print "usage: " + usage
		print "Please run '" + progname + " -h' for detailed options."
		sys.exit(1)
	# get default values
	for i in args_def:
		if args.__dict__[i] == None:
			args.__dict__[i] = args_def[i]
	# 
	
	
if __name__ == '__main__':
	main()
'''
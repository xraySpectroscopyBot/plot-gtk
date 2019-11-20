#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from configparser import ConfigParser
import math
import numpy as np
from scipy.interpolate import spline
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
import json
import os
import csv

path = os.path.dirname(os.path.abspath(__file__))

loadfile = ConfigParser()

stepsize = 0
time = 0
startsteps = 0
stepsperangle = 0

plot = {"plot" : False, "lambda" : False, "persecond" : False, "subtractbackground" : False, "smooth" : False, "zoom" : False}

counts = []     

class GtkSignalHandlers:
	def onQuit(self, *a, **kv):
		print ("Done")
		Gtk.main_quit()

	def onButtonTable(self, *a, **kv):
		stack.set_visible_child(tablebox)
		plot["plot"] = False
		plot["lambda"] = False
		plot["persecond"] = False
		plot["subtractbackground"] = False
		plot["smooth"] = False
		drawTable()
	def onButtonPlot(self, *a, **kv):
		stack.set_visible_child(plotbox)
		plot["plot"] = True
		plot["lambda"] = True
		plot["persecond"] = True
		plot["subtractbackground"] = True
		plot["smooth"] = True
		plot["zoom"] = True
		drawPlot()
	def onButtonLambda(self, *a, **kv):
		plot["lambda"] = not plot["lambda"]
		if plot["lambda"]:
			builder.get_object("lambda-plot").set_from_file(path + "/images/theta.svg")
			builder.get_object("lambda-table").set_from_file(path + "/images/theta.svg")
		else:
			builder.get_object("lambda-plot").set_from_file(path + "/images/lambda.svg")
			builder.get_object("lambda-table").set_from_file(path + "/images/lambda.svg")
		if plot["plot"]:
			drawPlot()
		else:
			drawTable()
	def onButtonPersecond(self, *a, **kv):
		plot["persecond"] = not plot["persecond"]
		if plot["persecond"]:
			builder.get_object("persecond-plot").set_from_file(path + "/images/pertime.svg")
			builder.get_object("persecond-table").set_from_file(path + "/images/pertime.svg")
		else:
			builder.get_object("persecond-plot").set_from_file(path + "/images/persecond.svg")
			builder.get_object("persecond-table").set_from_file(path + "/images/persecond.svg")
		if plot["plot"]:
			drawPlot()
		else:
			drawTable()
	def onButtonSubtractbackground(self, *a, **kv):
		plot["subtractbackground"] = not plot["subtractbackground"]
		if plot["subtractbackground"]:
			builder.get_object("subtractbackground-plot").set_from_file(path + "/images/back.svg")
			builder.get_object("subtractbackground-table").set_from_file(path + "/images/back.svg")
		else:
			builder.get_object("subtractbackground-plot").set_from_file(path + "/images/noback.svg")
			builder.get_object("subtractbackground-table").set_from_file(path + "/images/noback.svg")
		if plot["plot"]:
			drawPlot()
		else:
			drawTable()
	def onButtonSmooth(self, *a, **kv):
		plot["smooth"] = not plot["smooth"]
		if plot["smooth"]:
			builder.get_object("smooth-plot").set_from_file(path + "/images/sharp.svg")
		else:
			builder.get_object("smooth-plot").set_from_file(path + "/images/smooth.svg")
		drawPlot()
	def onButtonZoom(self, *a, **kv):
		plot["zoom"] = not plot["zoom"]
		if plot["zoom"]:
			builder.get_object("zoom-plot").set_from_file(path + "/images/nozoom.svg")
		else:
			builder.get_object("zoom-plot").set_from_file(path + "/images/zoom.svg")
		drawPlot()
	def onButtonSavePlot(self, *a, **kv):
		dialog = Gtk.FileChooserDialog("Diagramm speichern", window, Gtk.FileChooserAction.SAVE, ("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK))
		dialog.set_do_overwrite_confirmation(True)
		dialog.set_current_name("Diagramm")

		filter_jpg = Gtk.FileFilter()
		filter_jpg.set_name("Alle .jpg dateien")
		filter_jpg.add_mime_type("image/jpeg")
		dialog.add_filter(filter_jpg)

		filter_png = Gtk.FileFilter()
		filter_png.set_name("Alle .png dateien")
		filter_png.add_mime_type("image/png")
		dialog.add_filter(filter_png)

		filter_svg = Gtk.FileFilter()
		filter_svg.set_name("Alle .svg Dateien")
		filter_svg.add_mime_type("image/svg+xml")
		dialog.add_filter(filter_svg)

		filter_any = Gtk.FileFilter()
		filter_any.set_name("Alle Dateien")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)

		dialog.set_filter(filter_any)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			if dialog.get_filename()[-4:] == ".svg":
				drawPlot(dialog.get_filename())
			elif dialog.get_filename()[-4:] == ".png":
				drawPlot(dialog.get_filename())
			elif dialog.get_filename()[-4:] == ".jpg":
				drawPlot(dialog.get_filename())
			elif dialog.get_filter() == filter_jpg:
				drawPlot(dialog.get_filename() + ".jpg")
			elif dialog.get_filter() == filter_png:
				drawPlot(dialog.get_filename() + ".png")
			elif dialog.get_filter() == filter_svg:
				drawPlot(dialog.get_filename() + ".svg")
			else:
				drawPlot(dialog.get_filename() + ".png")
		elif response == Gtk.ResponseType.CANCEL:
			pass

		dialog.destroy()
	def onButtonSaveTable(self, *a, **kv):
		dialog = Gtk.FileChooserDialog("Tabelle speichern", window, Gtk.FileChooserAction.SAVE, ("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK))
		dialog.set_do_overwrite_confirmation(True)
		dialog.set_current_name("Daten")

		filter_csv = Gtk.FileFilter()
		filter_csv.set_name("Alle .csv dateien")
		filter_csv.add_mime_type("text/csv")
		dialog.add_filter(filter_csv)

		filter_any = Gtk.FileFilter()
		filter_any.set_name("Alle Dateien")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)

		dialog.set_filter(filter_any)

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			if dialog.get_filename()[-4:] == ".csv":
				drawTable(dialog.get_filename())
			else:
				drawTable(dialog.get_filename() + ".csv")
		elif response == Gtk.ResponseType.CANCEL:
			pass

		dialog.destroy()

def calculateValues():
	background = int(counts[0]) / time

	anglesize = stepsize / stepsperangle

	x = []
	y = []

	angle = np.empty(len(counts) - 1)
	for i in range(len(angle)):
		angle[i] = startsteps / stepsperangle + i * anglesize
	x = angle

	if plot["lambda"]:
		wavelength = np.empty(len(x))
		for i in range(len(x)):
			wavelength[i] = 2*d*math.sin(math.radians(angle[i]))
		x = wavelength

	counts_normalized = np.empty(len(x))
	for i in range(1, len(counts)):
		if plot["persecond"]:
			counts_normalized[i - 1] = int(counts[i]) / time
		else:
			counts_normalized[i - 1] = int(counts[i])
		if plot["subtractbackground"]:
			counts_normalized[i - 1] = counts_normalized[i - 1] - background
	y = counts_normalized

	if plot["smooth"]:
		xinterpolated = np.linspace(x.min(),x.max(),300)
		ysmoothed = spline(x, y, xinterpolated)
		x = xinterpolated
		y = ysmoothed

	return [x, y]

def drawTable(filename = ""):
	x, y = calculateValues()
	xLabel = builder.get_object("XLabel")
	yLabel = builder.get_object("YLabel")

	xText = ""
	yText = ""

	for value in x:
		if plot["lambda"]:
			xText = xText + "{:0.3e}".format(value) + "\n"
		else:
			xText = xText + str(value) + "\n"
	for value in y:
		yText = yText + str(value) + "\n"
	xLabel.set_text(xText)
	yLabel.set_text(yText)

	if plot["lambda"]:
		builder.get_object("XColumnLabel").set_text("Wellenlänge in m")
	else :
		builder.get_object("XColumnLabel").set_text("Glanzinkel in °")
	if plot["persecond"]:
		builder.get_object("YColumnLabel").set_text("Zählrahte in 1/s")
	else:
		builder.get_object("YColumnLabel").set_text("Zählrahte in 1/" + str(time) + "s")

	if filename != "":
		with open(filename, "w", newline="") as csvfile:
			csvwriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
			for i in range(len(x)):
				if plot["lambda"]:
					csvwriter.writerow(["{:0.3e}".format(x[i]), str(y[i])])
				else:
					csvwriter.writerow([str(x[i]), str(y[i])])

def drawPlot(filename = ""):
	if sw.get_child() != None:
		sw.remove(sw.get_child())

	figure = Figure(figsize=(8, 8), dpi=80)
	axis = figure.add_subplot(111)
	x, y = calculateValues()
	axis.plot(x, y)
	if plot["zoom"]:
		last = y[0]
		for i in range(len(y)):
			if y[i] > last:
				break
			last = y[i]
		axis.set_ylim(top=y[i:].max() + abs(y[i:].max() * 0.075), bottom=y[i:].min() - abs(y[i:].min() * 0.075))
	else:
		axis.set_ylim(top=y.max() + abs(y.max() * 0.075), bottom=y.min() - abs(y.min() * 0.075))
	if plot["lambda"]:
		axis.set_xlabel("Wellenlänge in m")
	else :
		axis.set_xlabel("Glanzinkel in °")
	if plot["persecond"]:
		axis.set_ylabel("Zählrahte in 1/s")
	else:
		axis.set_ylabel("Zählrahte in 1/" + str(time) + "s")
	axis.set_title("Röntgenspektrum")
	canvas = FigureCanvas(figure)
	sw.add(canvas)
	sw.show_all()

	if filename != "":
		figure.savefig(filename)

try:
	builder = Gtk.Builder()
	builder.add_from_file(path + "/plot.glade")
	builder.connect_signals(GtkSignalHandlers)
	window = builder.get_object("MainWindow");
	stack = builder.get_object("MainStack")
	sw = builder.get_object("PlotWindow")

	tablebox = builder.get_object("TableBox")
	plotbox = builder.get_object("PlotBox")

	dialog = Gtk.FileChooserDialog("Messwerte laden", window, Gtk.FileChooserAction.OPEN, ("Cancel", Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK))

	filter_dat = Gtk.FileFilter()
	filter_dat.set_name("Alle .dat dateien")
	filter_dat.add_pattern("*.dat")
	dialog.add_filter(filter_dat)

	filter_any = Gtk.FileFilter()
	filter_any.set_name("Alle Dateien")
	filter_any.add_pattern("*")
	dialog.add_filter(filter_any)

	dialog.set_filter(filter_dat)

	filepath = ""

	response = dialog.run()
	if response == Gtk.ResponseType.OK:
		loadfile.read(dialog.get_filename())
	elif response == Gtk.ResponseType.CANCEL:
		pass

	dialog.destroy()
	
	stepsize = float(loadfile["Parameters"]["stepsize"])
	time = float(loadfile["Parameters"]["time"])
	startsteps = float(loadfile["Parameters"]["startsteps"])
	stepsperangle = float(loadfile["Parameters"]["stepsperangle"])
	d = float(loadfile["Parameters"]["d"])
	counts = json.loads(loadfile["Data"]["counts"])

	builder.get_object("DLabel").set_text("d = " + "{:0.3e}".format(d) + "m")
	builder.get_object("BackgroundLabel").set_text("Hintergrundstrahlung: " + str(counts[0]) + " / " + str(time) + "s")
	
	stack.set_visible_child(tablebox)

	drawTable()

	window.show_all()
	Gtk.main()
except KeyError:
	print ("No input file!")

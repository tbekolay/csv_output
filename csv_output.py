#!/usr/bin/env python 
'''
Copyright (C) 2011 Trevor Bekolay, tbekolay@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

-------------------------- README --------------------------

This is an extension for Inkscape that adds an option for
writing to Comma-Separated-Value (CSV) files. These CSV
files do not represent the entire image, they only note
the x- and y-coordinates of each node in the SVG file.
It's mainly useful for taking plots that have been
vectorized and embedded in a and translating the vectorized
image to x,y values that can then be re-plotted
using a plotting library like Matplotlib or Matlab.

Portions of this extension were inspired by Bryan Hoyt's
PixelSnap and Aaron Spike's hpgl_output.py.

----------------------- INSTALLATION -----------------------

To install the extension, csv_output.py and csv_output.inx
have to reside in Inkscape's extensions folder. You can copy
them into a local extension folder.
  Linux: ~/.config/inkscape/extensions/
  Windows: C:\Documents and Settings\<UserName>\Application Data\Inkscape\extensions\

If you do this, you may have to uncomment some lines in
csv_output.py to ensure that the file can find inkex.py.

Another (easier) way to do this in Linux while still keeping
the extension easy to update is to create symbolic links.
  cd <folder containing csv_output.py and csv_output.inx>
  sudo ln -s ./csv_output.py /usr/share/inkscape/extensions/csv_output.py
  sudo ln -s ./csv_output.inx /usr/share/inkscape/extensions/csv_output.inx

-------------------------- USAGE ---------------------------

Once installed, you can save CSV files through the Save As...
dialog box. Make sure the original SVG file is saved, however,
as there is no way to load the CSV file once saved.
'''

# INKEX MODULE
# If you get the "No module named inkex" error, uncomment the relevant line
# below by removing the '#' at the start of the line.
#
#import sys
#sys.path += ['/usr/share/inkscape/extensions']                 # If you're using a standard Linux installation
#sys.path += ['/usr/local/share/inkscape/extensions']           # If you're using a custom Linux installation
#sys.path += ['C:\\Program Files\\Inkscape\\share\\extensions'] # If you're using a standard Windows installation

try:
    import inkex, simplepath, simpletransform
except ImportError:
    raise ImportError("Can't find inkex.\nPlease edit the file %s and see the section titled 'INKEX MODULE'" % __file__)



identity_m = [[1.0,0.0,0.0],[0.0,1.0,0.0]]

class MyEffect(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-m", "--mirror",
                        action="store", type="inkbool", 
                        dest="mirror", default="FALSE",
                        help="Mirror Y-Axis")
        self.OptionParser.add_option("-x", "--xOrigin",
                        action="store", type="float", 
                        dest="xOrigin", default=0.0,
                        help="X Origin (pixels)")
        self.OptionParser.add_option("-y", "--yOrigin",
                        action="store", type="float", 
                        dest="yOrigin", default=0.0,
                        help="Y Origin (pixels)")

        self.x = []
        self.y = []
    def output(self):
        print ', '.join(self.x) + '\n' + ', '.join(self.y)
    def effect(self):
        x0 = self.options.xOrigin
        y0 = self.options.yOrigin
        mirror = 1.0
        if self.options.mirror:
            mirror = -1.0
            if self.document.getroot().get('height'):
                y0 -= float(self.document.getroot().get('height'))
        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            i += 1
            layer_trans = layer.get('transform')
            if layer_trans:
                layer_m = simpletransform.parseTransform(layer_trans)
            else:
                layer_m = identity_m
            
            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for node in self.document.getroot().xpath(nodePath, namespaces=inkex.NSS):
                d = node.get('d')
                p = simplepath.parsePath(d)
                if p:
                    #sanity check
                    if p[0][0] == 'M':
                        pt = [p[0][1][0], p[0][1][1]]
                        t = node.get('transform')
                        if t:
                            m = simpletransform.parseTransform(t)
                            trans = simpletransform.composeTransform(layer_m, m)
                        else:
                            trans = layer_m
                        simpletransform.applyTransformToPoint(trans,pt)
                        
                        self.x.append(str(pt[0]-x0))
                        self.y.append(str(pt[1]*mirror-y0))

if __name__ == '__main__':   #pragma: no cover
    e = MyEffect()
    e.affect()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99

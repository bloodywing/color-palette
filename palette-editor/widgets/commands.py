from copy import copy
from PyQt4 import QtGui, QtCore

from color.colors import *

class SwatchesCommand(QtGui.QUndoCommand):
    def __init__(self, owner):
        QtGui.QUndoCommand.__init__(self)
        self.owner = owner
        self.colors = []

    def remember_swatches(self):
        self.colors = [[w.getColor() for w in row] for row in self.owner.swatches]

    def restore_swatches(self):
        for oldrow, row in zip(self.colors, self.owner.swatches):
            for clr, w in zip(oldrow, row):
                w.model.color = clr
                w.update()

    def undo(self):
        self.restore_swatches()

class ClearSwatches(SwatchesCommand):
    def __init__(self, owner):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("clearing color swatches"))

    def redo(self):
        self.remember_swatches()
        for row in self.owner.swatches:
            for w in row:
                w.setColor(None)
                w.model.color = None
                w.update()

class DoHarmony(SwatchesCommand):
    def __init__(self, owner):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("creating color harmony"))

    def redo(self):
        self.remember_swatches()
        self.owner._do_harmony()
        self.owner.update()

    def undo(self):
        self.restore_swatches()
        self.owner.update()

class UpdateShades(SwatchesCommand):
    def __init__(self, owner, prev_param, param):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("changing color shades"))
        self.prev_param = prev_param
        self.param = param

    def id(self):
        return 25

    def mergeWith(self, other):
        if not isinstance(other, UpdateShades):
            return False
        self.param = other.param
        #print "Merging: {} -> {}".format(self.prev_param, self.param)
        return True

    def redo(self):
        self.remember_swatches()
        p = float(self.param)/100.0
        self.owner._shades_parameter = p
        self.owner._auto_harmony()
        self.owner.shades_slider.set_value(self.param)

    def undo(self):
        self.restore_swatches()
        p = float(self.prev_param)/100.0
        self.owner._shades_parameter = p
        self.owner.shades_slider.set_value(self.prev_param)

class UpdateHarmony(SwatchesCommand):
    def __init__(self, owner, prev_param, param):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("changing color harmony"))
        self.prev_param = prev_param
        self.param = param

    def id(self):
        return 26

    def mergeWith(self, other):
        if not isinstance(other, UpdateHarmony):
            return False
        self.param = other.param
        #print "Merging: {} -> {}".format(self.prev_param, self.param)
        return True

    def redo(self):
        #print "UpdateHarmony"
        self.remember_swatches()
        p = float(self.param)/100.0
        self.owner.selector.set_harmony_parameter(p)
        self.owner.hcy_selector.set_harmony_parameter(p)
        self.owner._auto_harmony()
        self.owner.hcy_harmony_slider.set_value(self.param)
        self.owner.harmony_slider.set_value(self.param)

    def undo(self):
        self.restore_swatches()
        p = float(self.prev_param)/100.0
        self.owner.selector.set_harmony_parameter(p)
        self.owner.hcy_selector.set_harmony_parameter(p)
        self.owner.hcy_harmony_slider.set_value(self.prev_param)
        self.owner.harmony_slider.set_value(self.prev_param)

class ChangeSwatchesColors(SwatchesCommand):
    def __init__(self, owner, text, fn):
        SwatchesCommand.__init__(self, owner)
        if text is not None:
            self.setText(text)
        self.fn = fn

    def _map_swatches(self, fn):
        for row in self.owner.swatches:
            for w in row:
                clr = w.getColor()
                if clr is None:
                    continue
                clr = fn(clr)
                w.setColor_(clr)
        self.owner.update()

    def redo(self):
        self.remember_swatches()
        self._map_swatches(self.fn)

class MakeShades(SwatchesCommand):
    def __init__(self, owner, row, color):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("creating shades of color"))
        self.row = row
        self.color = color

    def redo(self):
        self.remember_swatches()
        self.old_base_color = self.owner.base_colors.get(self.row, None)
        self.old_color = self.owner.base_swatches[self.row].getColor()
        self.owner.base_colors[self.row] = self.color
        self.owner._do_harmony()
        self.owner.update()

    def undo(self):
        if self.old_color is None:
            del self.owner.base_colors[self.row]
        else:
            self.owner.base_colors[self.row] = self.old_base_color
        self.restore_swatches()
        swatch = self.owner.base_swatches[self.row]
        swatch.model.color = self.old_color
        swatch.update()

class ShadesFromScratchpad(SwatchesCommand):
    def __init__(self, owner):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("creating shades of colors from scratchpad"))

    def redo(self):
        self.remember_swatches()
        colors = self.owner.scratchpad.get_colors()
        self.old_base_colors = copy( self.owner.base_colors )
        for i, clr in enumerate(colors[:5]):
            self.owner.base_colors[i] = clr
        self.owner._do_harmony()
        self.owner.update()

    def undo(self):
        self.restore_swatches()
        self.owner.base_colors = self.old_base_colors
        self.owner.update()

class SetShader(SwatchesCommand):
    def __init__(self, owner, old_shader_idx, new_shader_idx):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("selecting shader"))
        self.old_shader_idx = old_shader_idx
        self.shader_idx = new_shader_idx

    def redo(self):
        self.remember_swatches()
        _, shader = self.owner.available_shaders[self.shader_idx]
        print("Selected shader: " + str(shader))
        self.owner.shader = shader
        self.owner._auto_harmony()
        self.owner.shaders.select_item(self.shader_idx)

    def undo(self):
        _, shader = self.owner.available_shaders[self.old_shader_idx]
        self.owner.shader = shader
        self.restore_swatches()
        self.owner.shaders.select_item(self.old_shader_idx)

class SelectColor(SwatchesCommand):
    def __init__(self, owner, selectors, sequence, prev_color, color):
        SwatchesCommand.__init__(self, owner)
        self.setText(_("selecting color"))
        self.selectors = selectors
        self.prev_color = prev_color
        self.color = color
        self.sequence = sequence
        self._id = hash(selectors[0])

    def id(self):
        return self._id

    def redo(self):
        #print "Selecting color:", self.color
        self.remember_swatches()
        self.old_base_colors = self.owner.base_colors
        self.owner.base_colors = {}
        self.owner.current_color.model.color = self.color
        self.owner.current_color.update()
        for selector in self.selectors:
            selector.setColor(self.color, no_signal=True)
        self.owner._auto_harmony()

    def undo(self):
        #print "Restoring color:", self.prev_color
        self.owner.base_colors = self.old_base_colors
        self.owner.current_color.model.color = self.prev_color
        self.owner.current_color.update()
        for selector in self.selectors:
            selector.setColor(self.prev_color, no_signal=True)
        self.restore_swatches()
        self.owner.update()

    def mergeWith(self, other):
        if not isinstance(other, SelectColor):
            return False
        if other.sequence != self.sequence:
            return False
        self.color = other.color
        return True


class SetMixer(QtGui.QUndoCommand):
    def __init__(self, owner, pairs, old_mixer_idx, new_mixer_idx):
        QtGui.QUndoCommand.__init__(self)
        self.owner = owner
        self.setText(_("selecting color model"))
        self.old_mixer_idx = old_mixer_idx
        self.mixer_idx = new_mixer_idx
        self.pairs = pairs

    def redo(self):
        _,  mixer = self.pairs[self.mixer_idx]
        print("Selected mixer: " + str(mixer))
        self.owner.setMixer(mixer, self.mixer_idx)

    def undo(self):
        _,  mixer = self.pairs[self.old_mixer_idx]
        self.owner.setMixer(mixer, self.old_mixer_idx)

class SetHarmony(SwatchesCommand):
    def __init__(self, selector, slider, owner, pairs, old_idx, new_idx, last_is_manual=False):
        SwatchesCommand.__init__(self, owner)
        self.selector = selector
        self.slider = slider
        self.setText(_("selecting harmony"))
        self.old_idx = old_idx
        self.idx = new_idx
        self.pairs = pairs
        self.last_is_manual = last_is_manual

    def redo(self):
        self.remember_swatches()
        if self.last_is_manual and self.idx >= len(self.pairs):
            self.selector.setHarmony(None)
            return
        _,  harmony = self.pairs[self.idx]
        print("Selected harmony: " + str(harmony))
        self.selector.setHarmony(harmony, self.idx)
        self.slider.setEnabled(harmony.uses_parameter)
        self.owner._auto_harmony()

    def undo(self):
        _,  harmony = self.pairs[self.old_idx]
        self.selector.setHarmony(harmony, self.old_idx)
        self.slider.setEnabled(harmony.uses_parameter)
        self.restore_swatches()
        self.owner._auto_harmony()

class ChangeColor(QtGui.QUndoCommand):
    def __init__(self, model, text, fn):
        QtGui.QUndoCommand.__init__(self)
        self.setText(text)
        self.fn = fn
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        color = self.fn(self.old_color)
        self.model.setColor(color)
        self.model.widget.repaint()

    def undo(self):
        self.model.setColor(self.old_color)
        self.model.widget.repaint()

class SetColor(QtGui.QUndoCommand):
    def __init__(self, model, color):
        QtGui.QUndoCommand.__init__(self)
        self.setText(_("setting color"))
        self.model = model
        self.color = color

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = self.color
        self.model.widget.repaint()
    
    def undo(self):
        self.model.color = self.old_color
        self.model.widget.repaint()

class Clear(QtGui.QUndoCommand):
    def __init__(self, model):
        QtGui.QUndoCommand.__init__(self)
        self.setText(_("clearing color swatch"))
        self.model = model

    def redo(self):
        self.old_color = self.model.getColor()
        self.model.color = None
        self.model.widget.repaint()

    def undo(self):
        self.model.color = self.old_color
        self.model.widget.repaint()

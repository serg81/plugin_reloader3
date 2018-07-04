# -*- coding: utf-8 -*-
# ***************************************************************************
# reloader_plugin.py  -  A Python Plugin Reloader for QGIS
# ---------------------
#     begin                : 2010-01-24
#     copyright            : (C) 2010 by Borys Jurgiel
#     email                : info at borysjurgiel dot pl
#     The "Reload" icon copyright by Matt Ball http://www.mattballdesign.com
# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************

#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QAction, QDialogButtonBox, QTreeWidgetItem, QComboBox, QAbstractItemView, QListWidgetItem, QToolBar, QFileDialog, QTableWidgetItem, QMessageBox, QComboBox, QApplication, QDateEdit, QTimeEdit, QAbstractItemView, QListWidgetItem, QDockWidget, QToolButton, QMenu
import qgis.core
#from qgis.core import QGis
from qgis.utils import plugins, reloadPlugin, updateAvailablePlugins, loadPlugin, startPlugin
#from configurereloaderbase import Ui_ConfigureReloaderDialogBase
#import resources_rc
qgis3 = hasattr(qgis.core, "Qgis")
print (u"qgis3={}".format(qgis3))
if qgis3:
    from qgis.core import (
        QgsDataSourceUri,
        QgsMarkerSymbol,
        QgsSymbol,
        QgsSingleSymbolRenderer,
        QgsLineSymbol,
        QgsFillSymbol,
        QgsRuleBasedRenderer,
        QgsSvgMarkerSymbolLayer,
        QgsUnitTypes,
        QgsWkbTypes,
        QgsSymbolLayer,
        QgsProperty,
        QgsPropertyCollection,
        QgsVectorLayerSimpleLabeling,
        QgsTextBufferSettings,
        QgsTextBackgroundSettings,
        QgsTextFormat,
        QgsStyle,
        QgsProject as QgsMapLayerRegistry
    )
    from qgis.gui import QgsStyleManagerDialog
else:
    from qgis.core import (
        QgsDataSourceURI as QgsDataSourceUri,
        QgsMarkerSymbolV2 as QgsMarkerSymbol,
        QgsSymbolV2 as QgsSymbol,
        QgsSingleSymbolRendererV2 as QgsSingleSymbolRenderer,
        QgsLineSymbolV2 as QgsLineSymbol,
        QgsFillSymbolV2 as QgsFillSymbol,
        QgsSymbolLayerV2 as QgsSymbolLayer,
        QgsRuleBasedRendererV2 as QgsRuleBasedRenderer,
        QgsSvgMarkerSymbolLayerV2 as QgsSvgMarkerSymbolLayer,
        QGis,
        QgsMapLayerRegistry,
        QgsStyleV2 as QgsStyle
    )
    from qgis.gui import QgsStyleV2ManagerDialog as QgsStyleManagerDialog

import os
import sys
from qgis.PyQt import uic


try:
    from builtins import unicode
    BASEDIR = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
except TypeError:
    BASEDIR = os.path.dirname(__file__)
Ui_ConfigureReloaderDialogBase = uic.loadUiType(os.path.join(BASEDIR, 'configurereloaderbase.ui'))[0]
#from configurereloaderbase import Ui_ConfigureReloaderDialogBase

qgisversion = hasattr(qgis.core, "QGIS_VERSION_INT")
if qgisversion >= 10900:
    SIPv2 = True
else:
    SIPv2 = False


def currentPlugin():
    settings = QSettings()
    if SIPv2:
      return unicode(settings.value('/PluginReloader/plugin', '', type=str))
    else:
      return unicode(settings.value('/PluginReloader/plugin', ''))


class ConfigureReloaderDialog (QDialog, Ui_ConfigureReloaderDialogBase):
  def __init__(self, parent):
    QDialog.__init__(self)
    self.iface = parent
    self.setupUi(self)
    self.plugins = sorted(plugins.keys())
    #self.plugins.sort()
    #update the plugin list first! The plugin could be removed from the list if was temporarily broken.
    #Still doesn't work in every case. TODO?: try to load from scratch the plugin saved in QSettings if doesn't exist
    plugin = currentPlugin()
    updateAvailablePlugins()
    #if not plugins.has_key(plugin):
      #try:
        #loadPlugin(plugin)
        #startPlugin(plugin)
      #except:
        #pass
    #updateAvailablePlugins()

    for plugin in self.plugins:
      self.comboPlugin.addItem(plugin)
    plugin = currentPlugin()
    #if plugins.has_key(plugin):
    if plugin in plugins:
      self.comboPlugin.setCurrentIndex(self.plugins.index(plugin))



class ReloaderPlugin(QObject):
  def __init__(self, iface):
    QObject.__init__(self)
    self.iface = iface
    self.toolButton = QToolButton()
    self.toolButton.setMenu(QMenu())
    self.toolButton.setPopupMode(QToolButton.MenuButtonPopup)
    self.iface.addToolBarWidget(self.toolButton)

  def initGui(self):
    self.actionRun = QAction(
      QIcon(os.path.join(BASEDIR, 'reload.png')),
      #QIcon(":/plugins/plugin_reloader/reload.png"), 
      u"Reload chosen plugin", 
      self.iface.mainWindow()
    )
    self.iface.registerMainWindowAction(self.actionRun, "F5")
    self.actionRun.setWhatsThis(u"Reload chosen plugin")
    plugin = currentPlugin()
    if plugin:
      self.actionRun.setWhatsThis(u"Reload plugin: %s" % plugin)
      self.actionRun.setText(u"Reload plugin: %s" % plugin)
    self.iface.addPluginToMenu("&Plugin Reloader", self.actionRun)
    m = self.toolButton.menu()
    m.addAction(self.actionRun)
    self.toolButton.setDefaultAction(self.actionRun)
    #QObject.connect(self.actionRun, SIGNAL("triggered()"), self.run)
    self.actionRun.triggered.connect(self.run)
    self.actionConfigure = QAction(
      QIcon(os.path.join(BASEDIR, 'reload-conf.png')),
      #QIcon(":/plugins/plugin_reloader/reload-conf.png"), 
      u"Choose a plugin to be reloaded", 
      self.iface.mainWindow()
    )
    self.iface.registerMainWindowAction(self.actionConfigure, "Shift+F5")
    self.actionConfigure.setWhatsThis(u"Choose a plugin to be reloaded")
    m.addAction(self.actionConfigure)
    self.iface.addPluginToMenu("&Plugin Reloader", self.actionConfigure)
    #QObject.connect(self.actionConfigure, SIGNAL("triggered()"), self.configure)
    self.actionConfigure.triggered.connect(self.configure)


  def unload(self):
    self.iface.removePluginMenu("&Plugin Reloader",self.actionRun)
    self.iface.removePluginMenu("&Plugin Reloader",self.actionConfigure)
    self.iface.removeToolBarIcon(self.actionRun)
    self.iface.removeToolBarIcon(self.actionConfigure)
    self.iface.unregisterMainWindowAction(self.actionRun)
    self.iface.unregisterMainWindowAction(self.actionConfigure)


  def run(self):
    plugin = currentPlugin()
    #update the plugin list first! The plugin could be removed from the list if was temporarily broken.
    updateAvailablePlugins()
    #try to load from scratch the plugin saved in QSettings if not loaded
    if plugin not in plugins:
      try:
        loadPlugin(plugin)
        startPlugin(plugin)
      except:
        pass
    updateAvailablePlugins()
    #give one chance for correct (not a loop)
    #if not plugins.has_key(plugin):
    if plugin not in plugins:
      self.configure()
      plugin = currentPlugin()
    #if plugins.has_key(plugin):
    if plugin in plugins:
      state = self.iface.mainWindow().saveState()
      reloadPlugin(plugin)
      self.iface.mainWindow().restoreState(state)


  def configure(self):
    dlg = ConfigureReloaderDialog(self.iface)
    dlg.exec_()
    if dlg.result():
      plugin = dlg.comboPlugin.currentText()
      settings = QSettings()
      if SIPv2:
        settings.setValue('/PluginReloader/plugin', plugin)
      else:
        settings.setValue('/PluginReloader/plugin', plugin)
      self.actionRun.setWhatsThis(u"Reload plugin: %s" % plugin)
      self.actionRun.setText(u"Reload plugin: %s" % plugin)
    # call the reloading immediately - note that it may cause a loop!!
    #self.run()

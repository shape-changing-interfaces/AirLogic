#Author-Hyunyoung Kim
#Description-MorpheesPlug script for Fusion 360
#Basic unit: cm, rad

from operator import truediv
import adsk.core, adsk.fusion, adsk.cam, traceback
import os

_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_handlers = []
_inputs = adsk.core.CommandInputs.cast(None)

commandId = 'airlogic'
commandName = 'AirLogic'
commandDescription = 'Drops AirLogic widgets in the workspace'
cwd = os.path.dirname(os.path.realpath(__file__))       # Current working directory
pathResources = os.path.join(cwd, "Resources")

def run(context):
    ui = None
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Create the command definition. 
        cmdDef = _ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription)
        
        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # # Add the button the ADD-INS panel.
        # addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        # addInsPanel.controls.addCommand(cmdDef)

        # Execute the command definition.
        inputs = adsk.core.NamedValues.create() # TODO. Not sure what this does.
        cmdDef.execute()                # Remove for Add-in

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)       # Remove for Add-in

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try: 
            global _inputs

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # # Connect to the command destroyed event.     # Remove for Add-in
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # # Connect to the input changed event.           
            # onInputChanged = MyCommandInputChangedHandler()
            # cmd.inputChanged.add(onInputChanged)
            # _handlers.append(onInputChanged)    

            # Connect to command excute handler. 
            onExecute = MyExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            # Connect to a preview handler.
            onExecutePreview = MyExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)
            
            # Get the CommandInputs collection associated with the command.
            _inputs = cmd.commandInputs
            #inputs = cmd.commandInputs
            
            # Connect to command inputs.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            um = des.unitsManager       # TODO. change the unit.
            dropDownInput = _inputs.addDropDownCommandInput('dropDown', 'Widget', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            dropDownInputItems = dropDownInput.listItems
            dropDownInputItems.add('Input-Touch', True)
            dropDownInputItems.add('Input-Button', False)
            dropDownInputItems.add('Input-Switch', False)
            dropDownInputItems.add('Input-Slider', False)
            dropDownInputItems.add('Input-Dial', False)
            dropDownInputItems.add('Logic-AND-NOT', False)
            dropDownInputItems.add('Logic-4-Way-AND-NOT', False)
            dropDownInputItems.add('Logic-OR', False)
            dropDownInputItems.add('Logic-XOR', False)
            dropDownInputItems.add('Output-Pin', False)
            dropDownInputItems.add('Output-Oscillating actuator', False)
            dropDownInputItems.add('Output-Whistle', False)
            dropDownInputItems.add('Output-Vibration motor', False)
            dropDownInputItems.add('Misc-2-Way-Splitter', False)
            dropDownInputItems.add('Misc-2-Way-Splitter-Sphere', False)
            dropDownInputItems.add('Misc-4-Way-Splitter', False)

            # Create radio button group input.
            radioButtonGroup = _inputs.addRadioButtonGroupCommandInput('radioButtonGroup', 'Type')
            radioButtonItems = radioButtonGroup.listItems
            radioButtonItems.add("Exterior - to print and test widgets", True)
            radioButtonItems.add("Pipe - to cut out from a model", False)
            #TODO. Set pitch for whistle

        except:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script. 
#      # Remove for Add-in           
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Now I feel this handler is not necessary, because the preview handler does the job I need.
class MyExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            
            dropDownInput = _inputs.itemById('dropDown')
            dropDownItem = dropDownInput.selectedItem
            #_ui.messageBox(dropDownItem.name)
            
            # Get import manager
            importManager = _app.importManager

            # Get active design
            product = _app.activeProduct
            design = adsk.fusion.Design.cast(product)
            
            # Get root component
            rootComp = design.rootComponent

            # Get selected radio button
            radiobuttons = _inputs.itemById('radioButtonGroup')
            selectedItem = radiobuttons.selectedItem
            if selectedItem.name == "Exterior - to print and test widgets":
                filePath = os.path.join(pathResources, dropDownItem.name+'.step')
            else:
                filePath = os.path.join(pathResources, dropDownItem.name+'-Pipe.step')
            
            stpOptions = importManager.createSTEPImportOptions(filePath)
            stpOptions.isViewFit = False
            importManager.importToTarget(stpOptions, rootComp) # Import step file to root component

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            
            dropDownInput = _inputs.itemById('dropDown')
            dropDownItem = dropDownInput.selectedItem
            #_ui.messageBox(dropDownItem.name)
            
            # Get import manager
            importManager = _app.importManager

            # Get active design
            product = _app.activeProduct
            design = adsk.fusion.Design.cast(product)
            
            # Get root component
            rootComp = design.rootComponent

            # Get selected radio button
            radiobuttons = _inputs.itemById('radioButtonGroup')
            selectedItem = radiobuttons.selectedItem
            if selectedItem.name == "Exterior - to print and test widgets":
                filePath = os.path.join(pathResources, dropDownItem.name+'.step')
            else:
                filePath = os.path.join(pathResources, dropDownItem.name+'-Pipe.step')
            
            stpOptions = importManager.createSTEPImportOptions(filePath)
            stpOptions.isViewFit = False
            importManager.importToTarget(stpOptions, rootComp) # Import step file to root component

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
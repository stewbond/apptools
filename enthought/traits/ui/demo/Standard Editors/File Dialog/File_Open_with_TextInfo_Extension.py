"""
This demonstrates using the Traits file dialog with a file dialog extension,
in this case, the <b>TextInfo</b> extension, which displays (if possible) the
contents of the currently selected file in a read-only text editor so the user
can quickly verify they are opening the correct file before leaving the file 
dialog.
 
For more information about why you would want to use the Traits file dialog 
over the standard OS file dialog, select the <b>File Open</b> demo. For a
demonstration of writing a custom file dialog extension, select the
<b>File Open with Custom Extension</b> demo.

This example also shows setting a file name filter which only allows Python
source (i.e. *.py) files to be viewed and selected. 
"""

#-- Imports --------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, File, Button
    
from enthought.traits.ui.api \
    import View, HGroup, Item

from enthought.traits.ui.file_dialog  \
    import open_file, TextInfo
    
#-- FileDialogDemo Class -------------------------------------------------------

# Demo specific file dialig id:
demo_id = 'enthought.traits.ui.demo.standard_editors.file_dialog.text_info'

class FileDialogDemo ( HasTraits ):
    
    # The name of the selected file:
    file_name = File
    
    # The button used to display the file dialog:
    open = Button( 'Open...' )
    
    #-- Traits View Definitions ------------------------------------------------
    
    view = View(
        HGroup(
            Item( 'open', show_label = False ),
            '_',
            Item( 'file_name', style = 'readonly', springy = True )
        ),
        width = 0.5
    )
    
    #-- Traits Event Handlers --------------------------------------------------
    
    def _open_changed ( self ):
        """ Handles the user clicking the 'Open...' button.
        """
        file_name = open_file( extensions = TextInfo(),
                               filter     = 'Python file (*.py)|*.py',
                               id         = demo_id )
        if file_name != '':
            self.file_name = file_name
            
#-- Set Up The Demo ------------------------------------------------------------

demo = FileDialogDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    

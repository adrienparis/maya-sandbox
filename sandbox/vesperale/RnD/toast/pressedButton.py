import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom

#create notifier
nManager = notifications.ToastNotificationManager
notifier = nManager.create_toast_notifier(r"C:\Users\USERNAME\AppData\Local\Programs\Python\Python38\python.exe")
# Use your python path there.

#define your notification as

tString = """
<toast>

    <visual>
        <binding template='ToastGeneric'>
            <text>New notifications</text>
            <text>Text</text>
            <text>Second text</text>
        </binding>
    </visual>

    <actions>
        <input id="textBox" type="text" placeHolderContent="Type a reply"/>
        <action
            content="Send"
            arguments="action=reply&amp;convId=01"
            activationType="background"
            hint-inputId="textBox"/>
            
        <action
            content="Button 1"
            arguments="action=viewdetails&amp;contentId=02"
            activationType="foreground"/>
    </actions>

</toast>
"""

#convert notification to an XmlDocument
xDoc = dom.XmlDocument()
xDoc.load_xml(tString)

# this is not called on the main thread.
def handle_activated(sender, _):
    print([sender, _])
    print('Button was pressed!')

# # add the activation token.
# activated_token = notifications.add_activated(handle_activated)

#display notification
notifier.show(notifications.ToastNotification(xDoc))

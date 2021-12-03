import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom
import time

def handle_activated(sender, event):
    print([sender, event])
    print(dir(sender))
    print(sender.data)
    print(dir(sender.data))
    print(event.reason)
    print(type(event.reason))
    print(dir(event))
    print('Button was pressed!')

#create notifier
nManager = notifications.ToastNotificationManager
notifier = nManager.create_toast_notifier(r"Vesperale")

temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\keyOwner.xml"
# temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\lateStudent.xml"

#define your notification as 
with open(temp_file, "r+") as f:
    tString = "".join(f.readlines())


#convert notification to an XmlDocument
xDoc = dom.XmlDocument()
xDoc.load_xml(tString)

temp = notifications.ToastNotification(xDoc)
activated_token = temp.add_dismissed(handle_activated)
#display notification
notifier.show(temp)

# print(nManager.OnActivated)


time.sleep(20)
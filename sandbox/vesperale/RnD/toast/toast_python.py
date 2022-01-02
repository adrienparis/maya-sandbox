import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom
import time

def printObject(obj):
    print(obj, type(obj))
    for attr in dir(obj):
        print("\t\t{}".format(attr))
    print("="*50 + "\n")

def handle_activated(sender, event):
    # print([sender, event])
    printObject(sender)
    printObject(sender.data)
    printObject(event)
    printObject(event.reason)
    print('Button was pressed!')

#create notifier
nManager = notifications.ToastNotificationManager
notifier = nManager.create_toast_notifier(r"Vesperale")

# temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\keyOwner.xml"
temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\lateStudent.xml"

#define your notification as 
with open(temp_file, "r+") as f:
    tString = "".join(f.readlines())


#convert notification to an XmlDocument
xDoc = dom.XmlDocument()
xDoc.load_xml(tString)

temp = notifications.ToastNotification(xDoc)
# print(dir(temp))
# activated_token = temp.add_activated(handle_activated)
activated_token = temp.add_dismissed(handle_activated)
#display notification
notifier.show(temp)

# print(nManager.OnActivated)

for i in range(10):
    time.sleep(1)
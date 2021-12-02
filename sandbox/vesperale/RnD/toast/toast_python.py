import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom

#create notifier
nManager = notifications.ToastNotificationManager
notifier = nManager.create_toast_notifier(r"Vesperale")

#define your notification as 
with open(r".\ToolBox\sandbox\vesperale\RnD\toast\keyOwner.xml", "r+") as f:
    tString = "".join(f.readlines())


#convert notification to an XmlDocument
xDoc = dom.XmlDocument()
xDoc.load_xml(tString)

#display notification
notifier.show(notifications.ToastNotification(xDoc))

print(nManager.OnActivated)
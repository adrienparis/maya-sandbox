import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom

#create notifier
nManager = notifications.ToastNotificationManager
notifier = nManager.create_toast_notifier(r"C:UsersRomainAppDataLocalProgramsPythonPython38python.exe")

#define your notification as


# temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\test.xml"
temp_file = r".\ToolBox\sandbox\vesperale\RnD\toast\lateStudent.xml"

#define your notification as 
with open(temp_file, "r+") as f:
    tString = "".join(f.readlines())


#convert notification to an XmlDocument
xDoc = dom.XmlDocument()
xDoc.load_xml(tString)

#display notification
notifier.show(notifications.ToastNotification(xDoc))
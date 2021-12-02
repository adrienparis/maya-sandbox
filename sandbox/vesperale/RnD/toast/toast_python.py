import winrt.windows.ui.notifications as notifications
import winrt.windows.data.xml.dom as dom

def handle_activated(sender, _):
    with open(r"C:\Users\paris_a\Documents\Creative Seeds\Rescources\toastAction.txt", "w+") as f:
        f.write([sender, _])
    print([sender, _])
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

for e in dir(notifier):
    print(e)
temp = notifications.ToastNotification(xDoc)
for e in dir(temp):
    print(e)
# exit()
activated_token = temp.add_dismissed(handle_activated)
for e in dir(activated_token):
    print(e)
print(activated_token.value)
with open("toastAction.txt", "w+") as f:
    f.write("plop")
#display notification
notifier.show(temp)

# print(nManager.OnActivated)



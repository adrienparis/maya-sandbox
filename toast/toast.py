# import plyer.platforms.win.notification
# from plyer import notification

# notification.notify("Quiet! 😤", "please 😓", app_name="Silencer", toast=False)
# notification.notify("choississez un horaire", "19h? 20h? 21h? 22h? 23h?", app_name="🌅 Présence vespérale", toast=False)
import subprocess

def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

cmd = """
function Show-Notification {
    [cmdletbinding()]
    Param (
        [string]
        $ToastTitle,
        [string]
        [parameter(ValueFromPipeline)]
        $ToastText
    )
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $Template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $RawXml = [xml] $Template.GetXml()
    ($RawXml.toast.visual.binding.text|where {$_.id -eq "1"}).AppendChild($RawXml.CreateTextNode($ToastTitle)) > $null
    ($RawXml.toast.visual.binding.text|where {$_.id -eq "2"}).AppendChild($RawXml.CreateTextNode($ToastText)) > $null>>
    $SerializedXml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $SerializedXml.LoadXml($RawXml.OuterXml)
    $Toast = [Windows.UI.Notifications.ToastNotification]::new($SerializedXml)
    $Toast.Tag = "##TITLE##"
    $Toast.Group = "##SUBTITLE##"
    $Toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(1)
    $Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("##CORE##")
    $Notifier.Show($Toast);
}
Show-Notification
"""
cmd = cmd.replace("##TITLE##", "PLOP").replace("##SUBTITLE##", "plop").replace("##CORE##", "_-_-_-_-_-_")

print(run(cmd))

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
    ($RawXml.toast.visual.binding.text|where {$_.id -eq "2"}).AppendChild($RawXml.CreateTextNode($ToastText)) > $null
    
    # $Item1 = New-BTSelectionBoxItem -Id 'Item1' -Content 'Picard Facepalm'
    # $Item2 = New-BTSelectionBoxItem -Id 'Item2' -Content 'Get It Girl'
    # $Item3 = New-BTSelectionBoxItem -Id 'Item3' -Content 'Seinfeld - Oh, right right right'
    # $Item4 = New-BTSelectionBoxItem -Id 'Item4' -Content 'Bob Ross?'
    
    # $InputSplat = @{
        #     Id    = 'Selection001'
        #     Title = 'Select a GIF to view now'
        #     DefaultSelectionBoxItemId = 'Item1'
        #     Items = $Item1, $Item2, $Item3, $Item4
        # }
        # $BTInput = New-BTInput @InputSplat
        # ($RawXml.toast.visual.binding.|where {$_.id -eq "3"}).AppendChild($RawXml.CreateTextNode($ToastText)) > $null
    
    $SerializedXml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $SerializedXml.LoadXml($RawXml.OuterXml)
    
    # $fileXml = Get-Content .\ToolBox\toast\template.xml -Raw
    $fileXml = Get-Content .\ToolBox\toast\lateStudent.xml -Raw
    # $fileXml = Get-Content .\ToolBox\toast\fromBigApp.xml -Raw
    
    $fileXml = $fileXml -replace '\r\n', ''
    $fileXml = $fileXml -replace '\t', ''

    # Write-Output $RawXml.OuterXml
    # Write-Output $fileXml
    
    $ToastXml = New-Object -TypeName Windows.Data.Xml.Dom.XmlDocument
    $ToastXml.LoadXml($fileXml)

    $Toast = [Windows.UI.Notifications.ToastNotification]::new($ToastXml)
    $Toast.Tag = "Vesperale"
    $Toast.Group = "Vesperale"
    $Toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(420)
    $Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Vesperale")
    $Notifier.Show($Toast);
}
Show-Notification "Harry Potter" "Et les relics de la mort"
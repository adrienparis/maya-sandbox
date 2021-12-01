# First, create all the component pieces

$AppLogo = New-BTImage -Source "S:/a.paris/Rescources/ToolBox/toast/sunset.jpg" -AppLogoOverride -Crop Circle
$HeroImage = New-BTImage -Source "S:/a.paris/Rescources/ToolBox/toast/sunset.jpg" -HeroImage
$MapImage = New-BTImage -Source "S:/a.paris/Rescources/ToolBox/toast/sunset.jpg"

$TextHeading = New-BTText -Text 'Upcoming Reservation'
$TextBody = New-BTText -Text 'You have a booking at Wildfire tonight, make sure you know how to get there!'

# Then bind them together

$Binding = New-BTBinding -Children $TextHeading, $TextBody, $MapImage -AppLogoOverride $AppLogo -HeroImage $HeroImage

# And remember that these components are visual, but not actionable

$Visual = New-BTVisual -BindingGeneric $Binding

# Speaking of actionable, we're using actions right?

$GoogleButton = New-BTButton -Content 'Google Maps' -Arguments 'https://www.google.com/maps/SNIP'
$BingButton = New-BTButton -Content 'Bing Maps' -Arguments 'https://www.bing.com/maps?SNIP'

# Don't forget that an action by itself is useless, even a single button needs to become plural

$Actions = New-BTAction -Buttons $GoogleButton, $BingButton

# Now all of the content is together...

$Content = New-BTContent -Visual $Visual -Actions $Actions

# We can submit it to the Operating System

Submit-BTNotification -Content $Content
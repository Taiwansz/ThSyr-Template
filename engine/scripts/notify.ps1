param(
    [string]$Title = "ThSyr // Alerta Cognitivo",
    [string]$Message = "Notificacao nativa operacional."
)

try {
    Add-Type -AssemblyName System.Windows.Forms
    $b = New-Object System.Windows.Forms.NotifyIcon
    $b.Icon = [System.Drawing.SystemIcons]::Information
    $b.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
    $b.BalloonTipTitle = $Title
    $b.BalloonTipText = $Message
    $b.Visible = $True
    $b.ShowBalloonTip(3000)
    Start-Sleep -Milliseconds 1500
    $b.Dispose()
} catch {
    # Silencioso se der erro
}
